"""
Personalized Learning Path Generator (Module 7)

RAG pipeline:
1) Retrieve learning resources from FAISS for each missing skill
2) Build a phased learning path (foundation → intermediate → advanced)
3) Generate explainable outcomes using OpenRouter API (free tier models)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

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
from models.learning_step import LearningStep
from models.skill_report import SkillGapReport
from utils.path_builder import ResourceEntry, build_learning_steps


@dataclass
class LearningPathConfig:
    top_k_per_skill: int = 6
    max_resources_per_skill: int = 3
    max_steps: int = 8
    use_llm: bool = True  # Default to True to use OpenRouter
    model_name: str = "meta-llama/llama-3.2-3b-instruct:free"  # OpenRouter free model
    max_new_tokens: int = 200
    temperature: float = 0.3
    include_estimates: bool = True


class OutcomeGenerator:
    def generate(
        self,
        *,
        skill: str,
        target_role: str,
        context: str,
        gap_summary: str,
    ) -> str:
        raise NotImplementedError


class OpenRouterOutcomeGenerator(OutcomeGenerator):
    """
    Learning outcome generation using OpenRouter API (free tier models).
    """

    def __init__(self, model_name: Optional[str] = None, prompt_template: Optional[str] = None):
        try:
            self.client = OpenRouterClient(model=model_name)
        except Exception as e:
            raise Exception(f"Could not initialize OpenRouter client: {e}")
        self.prompt_template = prompt_template or (
            "Skill: {skill}\nTarget Role: {target_role}\n"
            "Gap Summary: {gap_summary}\nContext: {context}\n"
            "Learning Outcome:"
        )

    def generate(
        self,
        *,
        skill: str,
        target_role: str,
        context: str,
        gap_summary: str,
    ) -> str:
        prompt = self.prompt_template.format(
            skill=skill,
            target_role=target_role,
            context=context,
            gap_summary=gap_summary or "None",
        )
        system_message = (
            "You are a learning path generator. Generate concise, actionable learning outcomes "
            "that describe what a person will achieve after learning a specific skill for a target role. "
            "Keep responses brief (1-2 sentences) and focused on practical outcomes."
        )
        return self.client.generate_with_fallback(
            prompt=prompt,
            max_tokens=200,
            temperature=0.3,
            system_message=system_message,
            fallback_message=f"Master {skill} for {target_role} role.",
        )


class FlanT5OutcomeGenerator(OutcomeGenerator):
    """
    Open-source text generation for learning outcomes (fallback option).
    """

    def __init__(self, model_name: str, prompt_template: str):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library is required for FlanT5OutcomeGenerator. Install with: pip install transformers torch")
        self.prompt_template = prompt_template
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self._pipeline = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,
        )

    def generate(
        self,
        *,
        skill: str,
        target_role: str,
        context: str,
        gap_summary: str,
    ) -> str:
        prompt = self.prompt_template.format(
            skill=skill,
            target_role=target_role,
            context=context,
            gap_summary=gap_summary or "None",
        )
        outputs = self._pipeline(
            prompt,
            max_new_tokens=120,
            do_sample=False,
            temperature=0.0,
            truncation=True,
        )
        if not outputs:
            return ""
        return outputs[0].get("generated_text", "").strip()


class NVIDIALearningPathGenerator:
    """
    Enhanced learning path generator using NVIDIA NIM for detailed, animated learning paths.
    Note: This class will properly inherit from LearningPathGenerator after it's defined below.
    """
    
    def __init__(self, store: Optional[FaissVectorStore] = None, config: Optional[LearningPathConfig] = None):
        # Initialize as base LearningPathGenerator
        self.store = store or build_default_kb()
        self.config = config or LearningPathConfig()
        self.prompt_template = self._load_prompt(None)
        self.generator = self._init_generator()
        
        # Try to initialize NVIDIA client
        try:
            from .nvidia_client import get_nvidia_client
            self.nvidia_client = get_nvidia_client()
        except:
            self.nvidia_client = None
    
    # Base class methods needed for NVIDIA class to work
    def _load_prompt(self, prompt_path: Optional[Path]) -> str:
        if prompt_path is None:
            prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "learning_prompt.txt"
        try:
            return prompt_path.read_text(encoding="utf-8")
        except Exception:
            return (
                "Skill: {skill}\nTarget Role: {target_role}\n"
                "Gap Summary: {gap_summary}\nContext: {context}\n"
                "Learning Outcome:"
            )

    def _init_generator(self) -> Optional[OutcomeGenerator]:
        if not self.config.use_llm:
            return None
        try:
            return OpenRouterOutcomeGenerator(self.config.model_name, self.prompt_template)
        except Exception as e:
            print(f"Warning: Could not initialize OpenRouter generator: {e}")
            return None
    
    @staticmethod
    def _coerce_skill_gap_report(report: SkillGapReport | Dict) -> SkillGapReport:
        if isinstance(report, SkillGapReport):
            return report
        return SkillGapReport(
            matched_skills=report.get("matched_skills") or [],
            partial_skills=report.get("partial_skills") or [],
            missing_skills=report.get("missing_skills") or [],
            readiness_score=int(report.get("readiness_score") or 0),
            summary=report.get("summary") or "",
        )
    
    def _retrieve_resources(self, skill: str, target_role: str) -> List[ResourceEntry]:
        """Retrieve learning resources from FAISS."""
        query = f"learning resources, tutorial, roadmap for {skill} for {target_role}"
        results = self.store.search(query, top_k=self.config.top_k_per_skill).get("results", [])

        learning = [r for r in results if r.get("source") == "learning"]
        if not learning:
            learning = results
        
        if len(self.store) == 0:
            return []

        entries: List[ResourceEntry] = []
        for item in learning:
            metadata = item.get("metadata") or {}
            entries.append(
                ResourceEntry(
                    content=item.get("content") or "",
                    source_type=item.get("source") or metadata.get("source_type", "learning"),
                    document_id=metadata.get("document_id") or "resource",
                    score=float(item.get("score") or 0.0),
                )
            )

        by_doc: Dict[str, ResourceEntry] = {}
        for entry in entries:
            existing = by_doc.get(entry.document_id)
            if existing is None or entry.score > existing.score:
                by_doc[entry.document_id] = entry

        return sorted(by_doc.values(), key=lambda e: e.score, reverse=True)
    
    def generate(self, *, skill_gap_report: SkillGapReport | Dict, target_role: str, top_n: Optional[int] = None) -> Dict:
        """Create a personalized learning path from missing skills and role."""
        report = self._coerce_skill_gap_report(skill_gap_report)
        missing_skills = list(dict.fromkeys(report.missing_skills))
        if top_n is not None:
            missing_skills = missing_skills[:top_n]

        if not missing_skills:
            return {"learning_path": []}

        resource_map: Dict[str, List[ResourceEntry]] = {}
        for skill in missing_skills:
            resource_map[skill] = self._retrieve_resources(skill, target_role)

        steps: List[LearningStep] = build_learning_steps(
            missing_skills=missing_skills[: self.config.max_steps],
            target_role=target_role,
            resource_map=resource_map,
            skill_gap_report=report,
            max_resources=self.config.max_resources_per_skill,
            include_estimates=self.config.include_estimates,
            outcome_generator=self.generator if self.config.use_llm else None,
        )

        return {"learning_path": [step.to_dict() for step in steps]}
    
    def generate_detailed_learning_path(
        self,
        skill_gap_report: SkillGapReport,
        target_role: str,
        user_skills: List[str] = None,
        experience_level: str = "Mid-level"
    ) -> Dict:
        """
        Generate detailed learning path with animations and comprehensive information.
        
        Returns:
            {
                "learning_path": [...],
                "detailed_info": {
                    "total_duration": "3-6 months",
                    "difficulty_level": "Intermediate",
                    "prerequisites": [...],
                    "learning_phases": [...],
                    "milestones": [...],
                    "resources": [...],
                    "animations": {
                        "progress_steps": [...],
                        "skill_tree": {...},
                        "timeline": {...}
                    }
                }
            }
        """
        # Get basic learning path first
        basic_path = self.generate(skill_gap_report, target_role)
        
        if not self.nvidia_client:
            # Return basic path with minimal enhancements
            return self._enhance_basic_path(basic_path, skill_gap_report, target_role)
        
        # Use NVIDIA for detailed analysis
        missing_skills = skill_gap_report.missing_skills
        current_skills = user_skills or []
        
        try:
            detailed_analysis = self._generate_nvidia_learning_analysis(
                missing_skills, target_role, current_skills, experience_level
            )
            
            # Combine basic path with NVIDIA analysis
            enhanced_path = self._merge_learning_data(basic_path, detailed_analysis)
            
            return enhanced_path
            
        except Exception as e:
            print(f"⚠️  NVIDIA learning path generation failed: {e}")
            return self._enhance_basic_path(basic_path, skill_gap_report, target_role)
    
    def _generate_nvidia_learning_analysis(
        self, 
        missing_skills: List[str], 
        target_role: str, 
        current_skills: List[str],
        experience_level: str
    ) -> Dict:
        """Generate detailed learning analysis using NVIDIA NIM."""
        
        skills_str = ", ".join(missing_skills)
        current_skills_str = ", ".join(current_skills) if current_skills else "Basic programming knowledge"
        
        prompt = f"""
You are an expert learning path designer and career coach. Create a comprehensive, detailed learning path.

TARGET ROLE: {target_role}
SKILLS TO LEARN: {skills_str}
CURRENT SKILLS: {current_skills_str}
EXPERIENCE LEVEL: {experience_level}

Create a detailed learning path with the following JSON structure:

{{
  "overview": {{
    "total_duration": "3-6 months",
    "difficulty_level": "Beginner/Intermediate/Advanced",
    "time_commitment": "10-15 hours/week",
    "success_rate": "85%"
  }},
  "prerequisites": [
    "Skill or knowledge needed before starting"
  ],
  "learning_phases": [
    {{
      "phase": 1,
      "title": "Foundation Phase",
      "duration": "2-3 weeks",
      "description": "Build fundamental understanding",
      "skills": ["skill1", "skill2"],
      "milestones": ["Complete basic tutorial", "Build first project"],
      "resources": ["Online course", "Practice platform"],
      "animation_steps": [
        "Start with basics → Build confidence → Apply knowledge"
      ]
    }}
  ],
  "skill_tree": {{
    "root": "{target_role}",
    "branches": [
      {{
        "skill": "Primary skill",
        "dependencies": ["prerequisite1", "prerequisite2"],
        "sub_skills": ["sub1", "sub2"],
        "mastery_level": "70-80%"
      }}
    ]
  }},
  "milestones": [
    {{
      "week": 2,
      "title": "First Milestone",
      "description": "Complete fundamental concepts",
      "deliverable": "Build a simple project"
    }}
  ],
  "resources": [
    {{
      "type": "Course",
      "title": "Comprehensive Course Name",
      "provider": "Platform",
      "duration": "4 weeks",
      "rating": "4.8/5",
      "cost": "Free/Paid",
      "url": "example.com"
    }}
  ],
  "progress_tracking": [
    {{
      "metric": "Projects completed",
      "target": 5,
      "current": 0
    }}
  ],
  "career_impact": {{
    "salary_increase": "15-25%",
    "job_opportunities": "+40%",
    "industry_demand": "High"
  }}
}}

Make it comprehensive, actionable, and motivating. Focus on practical steps and real outcomes.
"""
        
        response = self.nvidia_client.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=3000
        )
        
        try:
            # Parse JSON response
            import json
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
            
            return json.loads(cleaned_response)
            
        except json.JSONDecodeError:
            # Return fallback structure
            return self._create_fallback_detailed_analysis(missing_skills, target_role)
    
    def _create_fallback_detailed_analysis(self, missing_skills: List[str], target_role: str) -> Dict:
        """Create fallback detailed analysis if NVIDIA fails."""
        return {
            "overview": {
                "total_duration": "3-4 months", 
                "difficulty_level": "Intermediate",
                "time_commitment": "10-12 hours/week",
                "success_rate": "80%"
            },
            "prerequisites": ["Basic programming knowledge", "Problem-solving skills"],
            "learning_phases": [
                {
                    "phase": 1,
                    "title": "Foundation Phase",
                    "duration": "3-4 weeks", 
                    "description": f"Build core skills for {target_role}",
                    "skills": missing_skills[:3],
                    "milestones": ["Complete tutorials", "Build first project"],
                    "resources": ["Online courses", "Documentation"],
                    "animation_steps": ["Learn basics → Practice → Apply → Build projects"]
                },
                {
                    "phase": 2,
                    "title": "Advanced Phase", 
                    "duration": "4-6 weeks",
                    "description": "Master advanced concepts and best practices",
                    "skills": missing_skills[3:] if len(missing_skills) > 3 else ["Advanced concepts"],
                    "milestones": ["Complete complex project", "Pass certification"],
                    "resources": ["Advanced courses", "Real projects"],
                    "animation_steps": ["Advanced learning → Expert-level projects → Portfolio building"]
                }
            ],
            "skill_tree": {
                "root": target_role,
                "branches": [
                    {
                        "skill": skill,
                        "dependencies": ["Basic programming"],
                        "sub_skills": [f"{skill} fundamentals", f"Advanced {skill}"],
                        "mastery_level": "75-85%"
                    } for skill in missing_skills[:3]
                ]
            },
            "milestones": [
                {
                    "week": 3,
                    "title": "First Project Complete",
                    "description": "Built your first functional project",
                    "deliverable": "Working application or component"
                },
                {
                    "week": 8,
                    "title": "Portfolio Ready",
                    "description": "Professional portfolio with 3+ projects", 
                    "deliverable": "GitHub portfolio and resume update"
                }
            ],
            "resources": [
                {
                    "type": "Course",
                    "title": f"Complete {target_role} Course",
                    "provider": "Various platforms",
                    "duration": "8-12 weeks",
                    "rating": "4.5/5",
                    "cost": "Free/Paid",
                    "url": "#"
                }
            ],
            "progress_tracking": [
                {
                    "metric": "Skills mastered",
                    "target": len(missing_skills),
                    "current": 0
                },
                {
                    "metric": "Projects completed", 
                    "target": 5,
                    "current": 0
                }
            ],
            "career_impact": {
                "salary_increase": "20-30%",
                "job_opportunities": "+50%",
                "industry_demand": "High"
            }
        }
    
    def _merge_learning_data(self, basic_path: Dict, nvidia_analysis: Dict) -> Dict:
        """Merge basic learning path with NVIDIA detailed analysis."""
        return {
            "learning_path": basic_path.get("learning_path", []),
            "detailed_info": nvidia_analysis,
            "animations": {
                "progress_steps": self._generate_animation_steps(nvidia_analysis),
                "skill_tree": nvidia_analysis.get("skill_tree", {}),
                "timeline": self._generate_timeline_animation(nvidia_analysis),
                "fullscreen_enabled": True,
                "interactive_elements": [
                    "progress_bars",
                    "skill_nodes", 
                    "milestone_markers",
                    "achievement_badges"
                ]
            },
            "enhanced": True,
            "nvidia_powered": True
        }
    
    def _enhance_basic_path(self, basic_path: Dict, skill_gap_report: SkillGapReport, target_role: str) -> Dict:
        """Enhance basic path without NVIDIA."""
        return {
            "learning_path": basic_path.get("learning_path", []),
            "detailed_info": self._create_fallback_detailed_analysis(skill_gap_report.missing_skills, target_role),
            "animations": {
                "progress_steps": ["Step 1 → Step 2 → Step 3 → Completion"],
                "skill_tree": {"root": target_role, "branches": []},
                "timeline": {"phases": ["Foundation", "Intermediate", "Advanced"]},
                "fullscreen_enabled": True
            },
            "enhanced": False,
            "nvidia_powered": False
        }
    
    def _generate_animation_steps(self, analysis: Dict) -> List[str]:
        """Generate animation steps from analysis."""
        steps = []
        phases = analysis.get("learning_phases", [])
        for phase in phases:
            animation = phase.get("animation_steps", ["Learning → Practice → Mastery"])
            if isinstance(animation, list):
                steps.extend(animation)
            else:
                steps.append(str(animation))
        return steps or ["Start Learning → Build Projects → Master Skills → Get Job"]
    
    def _generate_timeline_animation(self, analysis: Dict) -> Dict:
        """Generate timeline animation data."""
        phases = analysis.get("learning_phases", [])
        return {
            "total_duration": analysis.get("overview", {}).get("total_duration", "3-4 months"),
            "phases": [
                {
                    "title": phase.get("title", f"Phase {phase.get('phase', 1)}"),
                    "duration": phase.get("duration", "2-3 weeks"),
                    "progress": phase.get("phase", 1) * 25  # 25% per phase
                } for phase in phases
            ]
        }


class LearningPathGenerator:
    """
    End-to-end learning path generator using RAG.
    """

    def __init__(
        self,
        store: FaissVectorStore,
        *,
        config: Optional[LearningPathConfig] = None,
        prompt_path: Optional[Path] = None,
        generator: Optional[OutcomeGenerator] = None,
    ):
        self.store = store
        self.config = config or LearningPathConfig()
        self.prompt_template = self._load_prompt(prompt_path)
        self.generator = generator or self._init_generator()

    def generate(
        self,
        *,
        skill_gap_report: SkillGapReport | Dict,
        target_role: str,
        top_n: Optional[int] = None,
    ) -> Dict:
        """
        Create a personalized learning path from missing skills and role.
        """
        report = self._coerce_skill_gap_report(skill_gap_report)
        missing_skills = list(dict.fromkeys(report.missing_skills))
        if top_n is not None:
            missing_skills = missing_skills[:top_n]

        if not missing_skills:
            return {"learning_path": []}

        resource_map: Dict[str, List[ResourceEntry]] = {}
        for skill in missing_skills:
            resource_map[skill] = self._retrieve_resources(skill, target_role)

        steps: List[LearningStep] = build_learning_steps(
            missing_skills=missing_skills[: self.config.max_steps],
            target_role=target_role,
            resource_map=resource_map,
            skill_gap_report=report,
            max_resources=self.config.max_resources_per_skill,
            include_estimates=self.config.include_estimates,
            outcome_generator=self.generator if self.config.use_llm else None,
        )

        return {"learning_path": [step.to_dict() for step in steps]}

    # ---------- Retrieval ----------

    def _retrieve_resources(self, skill: str, target_role: str) -> List[ResourceEntry]:
        """
        Retrieve learning resources from FAISS.

        RAG benefit: semantic retrieval finds relevant resources even
        if skill names vary across sources.
        """
        query = f"learning resources, tutorial, roadmap for {skill} for {target_role}"
        results = self.store.search(query, top_k=self.config.top_k_per_skill).get("results", [])

        learning = [r for r in results if r.get("source") == "learning"]
        if not learning:
            learning = results
        
        # If vector store is empty, return empty list gracefully
        if len(self.store) == 0:
            return []

        entries: List[ResourceEntry] = []
        for item in learning:
            metadata = item.get("metadata") or {}
            entries.append(
                ResourceEntry(
                    content=item.get("content") or "",
                    source_type=item.get("source") or metadata.get("source_type", "learning"),
                    document_id=metadata.get("document_id") or "resource",
                    score=float(item.get("score") or 0.0),
                )
            )

        # Deduplicate by document_id while keeping highest score
        by_doc: Dict[str, ResourceEntry] = {}
        for entry in entries:
            existing = by_doc.get(entry.document_id)
            if existing is None or entry.score > existing.score:
                by_doc[entry.document_id] = entry

        return sorted(by_doc.values(), key=lambda e: e.score, reverse=True)

    # ---------- Helpers ----------

    def _load_prompt(self, prompt_path: Optional[Path]) -> str:
        if prompt_path is None:
            prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "learning_prompt.txt"
        try:
            return prompt_path.read_text(encoding="utf-8")
        except Exception:
            return (
                "Skill: {skill}\nTarget Role: {target_role}\n"
                "Gap Summary: {gap_summary}\nContext: {context}\n"
                "Learning Outcome:"
            )

    def _init_generator(self) -> Optional[OutcomeGenerator]:
        if not self.config.use_llm:
            return None
        # Try OpenRouter first (preferred), fallback to FLAN-T5
        try:
            return OpenRouterOutcomeGenerator(self.config.model_name, self.prompt_template)
        except Exception as e:
            print(f"Warning: Could not initialize OpenRouter generator: {e}. Trying FLAN-T5 fallback.")
            try:
                return FlanT5OutcomeGenerator(self.config.model_name, self.prompt_template)
            except Exception as e2:
                print(f"Warning: Could not initialize FLAN-T5 generator: {e2}. Learning path will not use LLM-generated outcomes.")
                return None

    @staticmethod
    def _coerce_skill_gap_report(report: SkillGapReport | Dict) -> SkillGapReport:
        if isinstance(report, SkillGapReport):
            return report
        return SkillGapReport(
            matched_skills=report.get("matched_skills") or [],
            partial_skills=report.get("partial_skills") or [],
            missing_skills=report.get("missing_skills") or [],
            readiness_score=int(report.get("readiness_score") or 0),
            summary=report.get("summary") or "",
        )


def get_enhanced_learning_path_generator(store: Optional[FaissVectorStore] = None) -> LearningPathGenerator:
    """
    Factory function to get the best available learning path generator.
    Tries NVIDIA-enhanced version first, falls back to basic version.
    """
    try:
        # Try to create NVIDIA-enhanced generator
        return NVIDIALearningPathGenerator(store=store)
    except Exception as e:
        print(f"⚠️  NVIDIA learning path generator not available: {e}")
        # Fall back to basic generator
        return LearningPathGenerator(store=store)


def build_default_learning_path_generator() -> LearningPathGenerator:
    """
    Convenience constructor for quick testing.
    """
    store = build_default_kb()
    return LearningPathGenerator(store=store)


if __name__ == "__main__":
    # Simple demo (requires backend/data/learning_resources)
    generator = build_default_learning_path_generator()
    demo_gap = {"missing_skills": ["Docker", "Spark", "System Design"]}
    result = generator.generate(skill_gap_report=demo_gap, target_role="Data Engineer")
    print(result)
