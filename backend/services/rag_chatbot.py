"""
RAG-based AI Career Assistant (Module 6).

Pipeline:
1) Retrieve relevant context from FAISS (jobs, skills, learning resources)
2) Build a grounded prompt with resume + skill gap + job recommendations
3) Generate a response using OpenRouter API (free tier models)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoModelForSeq2SeqLM = None
    AutoTokenizer = None
    pipeline = None

from .vector_store import FaissVectorStore, build_default_kb
from .openrouter_client import OpenRouterClient, get_openrouter_client
from .nvidia_client import NVIDIAClient, get_nvidia_client
from models.chat_response import ChatResponse
from models.skill_report import SkillGapReport
from utils.context_builder import ContextChunk, build_context


@dataclass
class ChatConfig:
    top_k_retrieval: int = 8
    max_chunks: int = 6
    max_new_tokens: int = 500  # Increased for OpenRouter
    temperature: float = 0.7
    model_name: str = "meta-llama/llama-3.2-3b-instruct:free"  # OpenRouter free model


class BaseTextGenerator:
    """
    Minimal generator interface to swap in different local models later.
    """

    def generate(self, prompt: str, *, max_new_tokens: int, temperature: float) -> str:
        raise NotImplementedError


class SimpleTextGenerator(BaseTextGenerator):
    """
    Simple fallback generator when transformers is not available.
    Provides basic responses based on context.
    """

    def generate(self, prompt: str, *, max_new_tokens: int, temperature: float) -> str:
        """Generate a simple response based on prompt content."""
        prompt_lower = prompt.lower()
        
        # Extract question from prompt
        if "question:" in prompt_lower:
            question_part = prompt.split("Question:")[-1].split("Context:")[0].strip().lower()
        else:
            question_part = prompt_lower[:200]
        
        # Simple keyword-based responses
        if any(word in question_part for word in ["skill", "learn", "need", "require"]):
            return "Based on your profile, focus on building skills that align with your target role. Check the learning path section for structured guidance."
        elif any(word in question_part for word in ["job", "role", "position", "career"]):
            return "I recommend reviewing the job recommendations section to see roles that match your skills. Consider roles where you have 60%+ match scores."
        elif any(word in question_part for word in ["gap", "missing", "improve"]):
            return "Review your skill gap analysis to identify areas for improvement. Focus on the missing skills listed for your target role."
        else:
            return "I can help you with career guidance, skill development, and job recommendations. Please upload your resume and specify your target role for personalized advice."


class OpenRouterGenerator(BaseTextGenerator):
    """
    Text generation using OpenRouter API (free tier models).
    
    This uses OpenRouter's free models for fast, reliable text generation
    without requiring local model downloads or GPU resources.
    """

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        try:
            self.client = OpenRouterClient(api_key=api_key, model=model_name)
        except Exception as e:
            raise Exception(f"Could not initialize OpenRouter client: {e}")

    def generate(self, prompt: str, *, max_new_tokens: int, temperature: float) -> str:
        system_message = (
            "You are PathFinder AI, a helpful career guidance assistant. "
            "Provide clear, concise, and actionable advice based on the context provided."
        )
        return self.client.generate_with_fallback(
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            system_message=system_message,
            fallback_message="I apologize, but I'm having trouble generating a response right now. Please try again later.",
        )


class NVIDIAGenerator(BaseTextGenerator):
    """
    Text generation using NVIDIA API with Qwen model.
    
    This uses NVIDIA's integration platform for high-quality text generation.
    Provides an alternative to OpenRouter with enterprise-grade reliability.
    """

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        try:
            self.client = NVIDIAClient(api_key=api_key, model=model_name)
        except Exception as e:
            raise Exception(f"Could not initialize NVIDIA client: {e}")

    def generate(self, prompt: str, *, max_new_tokens: int, temperature: float) -> str:
        # Add system message context to prompt
        system_context = (
            "You are PathFinder AI, a helpful career guidance assistant. "
            "Provide clear, concise, and actionable advice based on the context provided.\n\n"
        )
        full_prompt = system_context + prompt
        
        try:
            return self.client.generate_text(
                prompt=full_prompt,
                temperature=temperature,
                max_tokens=max_new_tokens,
            )
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)[:100]}. Please try again."


class FlanT5Generator(BaseTextGenerator):
    """
    Free, open-source text generation using FLAN-T5 (fallback option).

    This is a fallback for when OpenRouter is not available.
    """

    def __init__(self, model_name: str):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library is required for FlanT5Generator. Install with: pip install transformers torch")
        # Try local files first to avoid blocking on download
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, local_files_only=True)
        except Exception:
            # If local files don't work, try without (may block)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            except Exception as e:
                raise Exception(f"Could not load model {model_name}: {type(e).__name__}")
        # Use device=-1 (CPU) by default; pipeline auto-detects available GPU.
        self._pipeline = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,
        )

    def generate(self, prompt: str, *, max_new_tokens: int, temperature: float) -> str:
        outputs = self._pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0.0,
            temperature=temperature,
            truncation=True,
        )
        if not outputs:
            return ""
        return outputs[0].get("generated_text", "").strip()


class RagCareerAssistant:
    """
    RAG career assistant that stays grounded in retrieved context.
    """

    def __init__(
        self,
        store: FaissVectorStore,
        *,
        config: Optional[ChatConfig] = None,
        generator: Optional[BaseTextGenerator] = None,
        prompt_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        use_nvidia: bool = False,
    ):
        self.store = store
        self.config = config or ChatConfig()
        # Try to initialize generator: NVIDIA, OpenRouter, FLAN-T5, or simple fallback
        if generator:
            self.generator = generator
        else:
            generator_initialized = False
            
            # Try NVIDIA first if requested
            if use_nvidia:
                try:
                    self.generator = NVIDIAGenerator()
                    print("Using NVIDIA API for text generation")
                    generator_initialized = True
                except Exception as e:
                    print(f"Warning: Could not initialize NVIDIA generator: {e}. Trying alternatives.")
            
            # Try OpenRouter if NVIDIA not requested or failed
            if not generator_initialized:
                try:
                    self.generator = OpenRouterGenerator(self.config.model_name)
                    print("Using OpenRouter API for text generation")
                    generator_initialized = True
                except Exception as e:
                    print(f"Warning: Could not initialize OpenRouter generator: {e}. Trying FLAN-T5 fallback.")
            
            # Try FLAN-T5 as fallback
            if not generator_initialized:
                try:
                    self.generator = FlanT5Generator(self.config.model_name)
                    print("Using local FLAN-T5 for text generation")
                    generator_initialized = True
                except (ImportError, Exception) as e2:
                    print(f"Warning: Could not initialize FLAN-T5 generator: {e2}. Using simple fallback.")
            
            # Use simple fallback if all else fails
            if not generator_initialized:
                self.generator = SimpleTextGenerator()
                print("Using simple fallback generator")
                
        self.prompt_template = self._load_prompt(prompt_path)
        self._recent_questions: List[str] = []

    def ask(
        self,
        question: str,
        *,
        resume_json: Optional[Dict] = None,
        skill_gap_report: Optional[SkillGapReport | Dict] = None,
        job_recommendations: Optional[Dict] = None,
        chat_history: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> ChatResponse:
        """
        Answer a user question with RAG grounding and chat history context.
        """
        question = (question or "").strip()
        if not question:
            return ChatResponse(question="", answer="Please provide a question.", sources=[], confidence=0.0)

        report = self._coerce_skill_gap_report(skill_gap_report)

        retrieved = self._retrieve_context(question, top_k=top_k or self.config.top_k_retrieval)
        context, sources = build_context(
            question=question,
            resume_json=resume_json,
            skill_gap_report=report,
            job_recommendations=job_recommendations,
            retrieved_chunks=retrieved,
            max_chunks=self.config.max_chunks,
        )

        # Add chat history to context if available
        if chat_history:
            context = f"Previous conversation:\n{chat_history}\n\nCurrent context:\n{context}"

        memory = self._format_memory()
        prompt = self.prompt_template.format(
            question=question,
            context=context,
            memory=memory,
        )

        # Avoid generating answers without retrieval if we have zero context.
        if not retrieved and not context.strip():
            answer = "I do not have enough information to answer that yet."
            confidence = 0.0
        else:
            answer = self.generator.generate(
                prompt,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
            )
            if not answer:
                answer = "I do not have enough information to answer that yet."
            confidence = self._estimate_confidence(retrieved)

        self._remember(question)
        return ChatResponse(
            question=question,
            answer=answer,
            sources=sources,
            confidence=confidence,
        )

    # ---------- Retrieval ----------

    def _retrieve_context(self, question: str, *, top_k: int) -> List[ContextChunk]:
        """
        Retrieve top-k chunks from FAISS for RAG grounding.
        """
        results = self.store.search(question, top_k=top_k).get("results", [])
        chunks: List[ContextChunk] = []
        for item in results:
            metadata = item.get("metadata") or {}
            chunks.append(
                ContextChunk(
                    content=item.get("content") or "",
                    source_type=item.get("source") or metadata.get("source_type", "unknown"),
                    document_id=metadata.get("document_id") or "unknown",
                    score=float(item.get("score") or 0.0),
                )
            )
        return chunks

    # ---------- Helpers ----------

    def _load_prompt(self, prompt_path: Optional[Path]) -> str:
        if prompt_path is None:
            prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "career_prompt.txt"
        try:
            return prompt_path.read_text(encoding="utf-8")
        except Exception:
            return (
                "You are PathFinder AI. Use only the CONTEXT.\n"
                "Question: {question}\n"
                "Context: {context}\n"
                "Answer:"
            )

    def _remember(self, question: str) -> None:
        self._recent_questions.append(question)
        self._recent_questions = self._recent_questions[-3:]

    def _format_memory(self) -> str:
        if not self._recent_questions:
            return "None"
        return "\n".join(f"- {q}" for q in self._recent_questions)

    @staticmethod
    def _estimate_confidence(chunks: Sequence[ContextChunk]) -> float:
        if not chunks:
            return 0.0
        scores = [c.score for c in chunks[:3]]
        # FAISS uses inner product on normalized vectors; map [-1, 1] to [0, 1].
        mapped = [max(0.0, min(1.0, (s + 1.0) / 2.0)) for s in scores]
        return float(np.mean(mapped))

    @staticmethod
    def _coerce_skill_gap_report(report: Optional[SkillGapReport | Dict]) -> Optional[SkillGapReport]:
        if report is None:
            return None
        if isinstance(report, SkillGapReport):
            return report
        if isinstance(report, dict):
            return SkillGapReport(
                matched_skills=report.get("matched_skills") or [],
                partial_skills=report.get("partial_skills") or [],
                missing_skills=report.get("missing_skills") or [],
                readiness_score=int(report.get("readiness_score") or 0),
                summary=report.get("summary") or "",
            )
        return None


def build_default_rag_assistant() -> RagCareerAssistant:
    """
    Convenience constructor for quick testing.
    """
    store = build_default_kb()
    return RagCareerAssistant(store=store)


if __name__ == "__main__":
    # Simple CLI demo (requires backend/data/* to be populated)
    assistant = build_default_rag_assistant()
    demo_resume = {"skills": ["Python", "SQL", "AWS"]}
    while True:
        q = input("\nAsk a career question (or 'exit'): ").strip()
        if not q or q.lower() == "exit":
            break
        response = assistant.ask(q, resume_json=demo_resume)
        print(response.to_dict())
