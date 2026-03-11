"""
Minimal AI Service Manager

Lightweight version that focuses on API integrations without heavy ML dependencies.
Provides the same interface but without local model dependencies.
"""

from typing import Dict, List, Optional, Union
import os
import logging

from .nvidia_client import NVIDIAClient, get_nvidia_client
from .openrouter_client import OpenRouterClient, get_openrouter_client

logger = logging.getLogger(__name__)


class MinimalAIServiceManager:
    """
    Lightweight AI service manager focused on API integrations.
    No local ML dependencies - pure API-based AI services.
    """
    
    def __init__(
        self, 
        nvidia_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        prefer_nvidia: bool = True
    ):
        """
        Initialize minimal AI service manager.
        
        Args:
            nvidia_api_key: NVIDIA API key
            openrouter_api_key: OpenRouter API key  
            prefer_nvidia: Whether to prefer NVIDIA over OpenRouter
        """
        self.prefer_nvidia = prefer_nvidia
        self.nvidia_client = get_nvidia_client(api_key=nvidia_api_key)
        self.openrouter_client = get_openrouter_client(api_key=openrouter_api_key)
        
        # Log available providers
        available_providers = []
        if self.nvidia_client:
            available_providers.append("NVIDIA")
        if self.openrouter_client:
            available_providers.append("OpenRouter")
            
        logger.info(f"Minimal AI Service Manager initialized with: {available_providers}")
    
    def get_primary_client(self) -> Union[NVIDIAClient, OpenRouterClient, None]:
        """Get the primary client based on preference and availability."""
        if self.prefer_nvidia and self.nvidia_client:
            return self.nvidia_client
        elif self.openrouter_client:
            return self.openrouter_client
        elif self.nvidia_client:
            return self.nvidia_client
        else:
            return None
    
    def get_fallback_client(self) -> Union[NVIDIAClient, OpenRouterClient, None]:
        """Get the fallback client."""
        if self.prefer_nvidia and self.nvidia_client:
            return self.openrouter_client
        elif self.openrouter_client:
            return self.nvidia_client
        else:
            return None
    
    def generate_resume_analysis(self, resume_data: Dict) -> Dict:
        """
        Generate resume analysis using available AI services.
        """
        # Try primary client first
        primary_client = self.get_primary_client()
        if primary_client:
            try:
                if isinstance(primary_client, NVIDIAClient):
                    logger.info("Using NVIDIA API for resume analysis")
                    return primary_client.generate_resume_analysis(resume_data)
                else:
                    logger.info("Using OpenRouter API for resume analysis")
                    return self._openrouter_resume_analysis(resume_data)
            except Exception as e:
                logger.error(f"Primary client failed: {e}")
        
        # Try fallback client
        fallback_client = self.get_fallback_client()
        if fallback_client:
            try:
                if isinstance(fallback_client, NVIDIAClient):
                    logger.info("Using NVIDIA API (fallback) for resume analysis")
                    return fallback_client.generate_resume_analysis(resume_data)
                else:
                    logger.info("Using OpenRouter API (fallback) for resume analysis")
                    return self._openrouter_resume_analysis(resume_data)
            except Exception as e:
                logger.error(f"Fallback client failed: {e}")
        
        # Return basic analysis if all APIs fail
        logger.warning("All AI services unavailable, returning basic analysis")
        return self._basic_resume_analysis(resume_data)
    
    def generate_job_recommendations(
        self, 
        resume_data: Dict, 
        num_recommendations: int = 5
    ) -> List[Dict]:
        """
        Generate job recommendations using available AI services.
        """
        # Try primary client first
        primary_client = self.get_primary_client()
        if primary_client:
            try:
                if isinstance(primary_client, NVIDIAClient):
                    logger.info("Using NVIDIA API for job recommendations")
                    return primary_client.generate_job_recommendations(
                        resume_data, num_recommendations
                    )
                else:
                    logger.info("Using OpenRouter API for job recommendations")
                    return self._openrouter_job_recommendations(
                        resume_data, num_recommendations
                    )
            except Exception as e:
                logger.error(f"Primary client failed for job recommendations: {e}")
        
        # Try fallback client
        fallback_client = self.get_fallback_client()
        if fallback_client:
            try:
                if isinstance(fallback_client, NVIDIAClient):
                    logger.info("Using NVIDIA API (fallback) for job recommendations")
                    return fallback_client.generate_job_recommendations(
                        resume_data, num_recommendations
                    )
                else:
                    logger.info("Using OpenRouter API (fallback) for job recommendations")
                    return self._openrouter_job_recommendations(
                        resume_data, num_recommendations
                    )
            except Exception as e:
                logger.error(f"Fallback client failed: {e}")
        
        # Return basic recommendations if all APIs fail
        logger.warning("All AI services unavailable, returning basic job recommendations")
        return self._basic_job_recommendations(resume_data, num_recommendations)
    
    def generate_learning_path(
        self, 
        current_skills: List[str], 
        target_role: str,
        timeline: str = "3 months"
    ) -> Dict:
        """
        Generate learning path using available AI services.
        """
        # Try primary client first
        primary_client = self.get_primary_client()
        if primary_client:
            try:
                if isinstance(primary_client, NVIDIAClient):
                    logger.info("Using NVIDIA API for learning path")
                    return primary_client.generate_learning_path(
                        current_skills, target_role, timeline
                    )
                else:
                    logger.info("Using OpenRouter API for learning path")
                    return self._openrouter_learning_path(
                        current_skills, target_role, timeline
                    )
            except Exception as e:
                logger.error(f"Primary client failed for learning path: {e}")
        
        # Try fallback client
        fallback_client = self.get_fallback_client()
        if fallback_client:
            try:
                if isinstance(fallback_client, NVIDIAClient):
                    logger.info("Using NVIDIA API (fallback) for learning path")
                    return fallback_client.generate_learning_path(
                        current_skills, target_role, timeline
                    )
                else:
                    logger.info("Using OpenRouter API (fallback) for learning path")
                    return self._openrouter_learning_path(
                        current_skills, target_role, timeline
                    )
            except Exception as e:
                logger.error(f"Fallback client failed: {e}")
        
        # Return basic learning path if all APIs fail
        logger.warning("All AI services unavailable, returning basic learning path")
        return self._basic_learning_path(current_skills, target_role, timeline)
    
    def _openrouter_resume_analysis(self, resume_data: Dict) -> Dict:
        """Generate resume analysis using OpenRouter."""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience_summary', '')
        
        # Build prompt for OpenRouter
        prompt = f"""
Analyze this resume and provide insights:

SKILLS: {', '.join(skills)}
EXPERIENCE: {experience}

Provide a JSON response with:
- strengths: List of 3-5 key strengths
- improvements: List of 3-5 improvement areas  
- career_level: entry/mid/senior
- industry_fit: best matching industry
- skill_gaps: areas needing development

Format as valid JSON only.
"""
        
        try:
            response = self.openrouter_client.call_model(
                prompt=prompt,
                model="meta-llama/llama-3.2-3b-instruct:free",
                max_tokens=500,
                temperature=0.3
            )
            
            # Try to parse JSON response
            import json
            try:
                return json.loads(response)
            except:
                # Fallback if JSON parsing fails
                return {
                    "strengths": skills[:3] if skills else ["Skills identified"],
                    "improvements": ["AI analysis needs refinement"],
                    "career_level": "mid",
                    "industry_fit": "technology",
                    "skill_gaps": ["Continue skill development"]
                }
                
        except Exception as e:
            logger.error(f"OpenRouter analysis failed: {e}")
            return self._basic_resume_analysis(resume_data)
    
    def _openrouter_job_recommendations(self, resume_data: Dict, num_recommendations: int) -> List[Dict]:
        """Generate job recommendations using OpenRouter."""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience_summary', '')
        
        prompt = f"""
Based on this profile, recommend {num_recommendations} job positions:

SKILLS: {', '.join(skills)}
EXPERIENCE: {experience}

For each job, provide JSON with:
- title: Specific job title
- company_type: Type of company
- salary_range: Expected salary
- description: Brief description
- required_skills: List of key skills
- match_score: Match percentage (0-100)
- growth_potential: Career growth description

Return as JSON array only.
"""
        
        try:
            response = self.openrouter_client.call_model(
                prompt=prompt,
                model="meta-llama/llama-3.2-3b-instruct:free",
                max_tokens=1000,
                temperature=0.4
            )
            
            import json
            try:
                recommendations = json.loads(response)
                if isinstance(recommendations, dict):
                    recommendations = [recommendations]
                return recommendations[:num_recommendations]
            except:
                return self._basic_job_recommendations(resume_data, num_recommendations)
                
        except Exception as e:
            logger.error(f"OpenRouter job recommendations failed: {e}")
            return self._basic_job_recommendations(resume_data, num_recommendations)
    
    def _openrouter_learning_path(self, current_skills: List[str], target_role: str, timeline: str) -> Dict:
        """Generate learning path using OpenRouter."""
        prompt = f"""
Create a {timeline} learning path for:
CURRENT SKILLS: {', '.join(current_skills)}
TARGET ROLE: {target_role}

Provide JSON with:
- skill_gaps: List of skills to develop
- learning_phases: Array with title, duration, topics, resources
- milestones: Key achievements 
- estimated_hours: Total time needed
- priority_order: Which skills first

Return valid JSON only.
"""
        
        try:
            response = self.openrouter_client.call_model(
                prompt=prompt,
                model="meta-llama/llama-3.2-3b-instruct:free",
                max_tokens=800,
                temperature=0.3
            )
            
            import json
            try:
                return json.loads(response)
            except:
                return self._basic_learning_path(current_skills, target_role, timeline)
                
        except Exception as e:
            logger.error(f"OpenRouter learning path failed: {e}")
            return self._basic_learning_path(current_skills, target_role, timeline)
    
    def _basic_resume_analysis(self, resume_data: Dict) -> Dict:
        """Fallback resume analysis."""
        skills = resume_data.get('skills', [])
        return {
            "strengths": skills[:3] if skills else ["Resume uploaded successfully"],
            "improvements": ["AI analysis temporarily unavailable"],
            "career_level": "mid",
            "industry_fit": "technology", 
            "skill_gaps": ["AI analysis needed"]
        }
    
    def _basic_job_recommendations(self, resume_data: Dict, num_recommendations: int) -> List[Dict]:
        """Fallback job recommendations."""
        skills = resume_data.get('skills', [])
        return [
            {
                "title": f"Software Developer {i+1}",
                "company_type": "Technology Company",
                "salary_range": "$70,000 - $90,000",
                "description": "Great opportunity matching your background",
                "required_skills": skills[:3] if skills else ["Programming"],
                "match_score": 80 - (i * 5),
                "growth_potential": "Strong potential"
            } for i in range(num_recommendations)
        ]
    
    def _basic_learning_path(self, current_skills: List[str], target_role: str, timeline: str) -> Dict:
        """Fallback learning path."""
        return {
            "skill_gaps": ["AI-powered analysis needed"],
            "learning_phases": [
                {
                    "title": "Basic Phase",
                    "duration": timeline,
                    "topics": ["Skill development"],
                    "resources": ["Online resources"]
                }
            ],
            "milestones": ["Continue learning"],
            "estimated_hours": 80,
            "priority_order": ["Core skills"]
        }


# Global instance for dependency injection
_minimal_ai_service_manager = None


def get_minimal_ai_service_manager(
    nvidia_api_key: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
    prefer_nvidia: bool = True
) -> MinimalAIServiceManager:
    """
    Get or create the minimal AI service manager instance.
    """
    global _minimal_ai_service_manager
    
    if _minimal_ai_service_manager is None:
        _minimal_ai_service_manager = MinimalAIServiceManager(
            nvidia_api_key=nvidia_api_key,
            openrouter_api_key=openrouter_api_key,
            prefer_nvidia=prefer_nvidia
        )
    
    return _minimal_ai_service_manager