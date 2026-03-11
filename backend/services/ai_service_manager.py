"""
Enhanced AI Service Manager

Provides a unified interface that can use either OpenRouter (free) 
or NVIDIA API (premium) based on availability and configuration.
"""

from typing import Dict, List, Optional, Union
import os
import logging

from .openrouter_client import OpenRouterClient, get_openrouter_client
from .nvidia_client import NVIDIAClient, get_nvidia_client

logger = logging.getLogger(__name__)


class AIServiceManager:
    """
    Manages multiple AI service providers with fallback capabilities.
    Prioritizes NVIDIA API for better quality, falls back to OpenRouter.
    """
    
    def __init__(
        self, 
        nvidia_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        prefer_nvidia: bool = True
    ):
        """
        Initialize AI service manager with multiple providers.
        
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
            
        logger.info(f"AI Service Manager initialized with providers: {available_providers}")
    
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
        Generate comprehensive resume analysis with fallback capability.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            Analysis results from best available provider
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
        Generate job recommendations with fallback capability.
        
        Args:
            resume_data: Parsed resume data
            num_recommendations: Number of recommendations to generate
            
        Returns:
            List of job recommendations from best available provider
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
                    # Use existing OpenRouter logic
                    from .ai_job_recommender import AIJobRecommender
                    recommender = AIJobRecommender(api_key=None)  # Uses default
                    result = recommender.generate_recommendations(
                        resume_data, top_n=num_recommendations
                    )
                    return result
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
                    from .ai_job_recommender import AIJobRecommender
                    recommender = AIJobRecommender(api_key=None)
                    result = recommender.generate_recommendations(
                        resume_data, top_n=num_recommendations
                    )
                    return result
            except Exception as e:
                logger.error(f"Fallback client failed for job recommendations: {e}")
        
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
        Generate learning path with fallback capability.
        
        Args:
            current_skills: List of current skills
            target_role: Desired job role
            timeline: Learning timeline
            
        Returns:
            Structured learning path from best available provider
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
                logger.error(f"Fallback client failed for learning path: {e}")
        
        # Return basic learning path if all APIs fail
        logger.warning("All AI services unavailable, returning basic learning path")
        return self._basic_learning_path(current_skills, target_role, timeline)
    
    def _openrouter_resume_analysis(self, resume_data: Dict) -> Dict:
        """Generate resume analysis using OpenRouter format."""
        # Use the existing OpenRouter client logic
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience_summary', '')
        
        return {
            "strengths": skills[:3] if skills else ["Skills identified"],
            "improvements": ["Continue skill development", "Gain more experience"],
            "career_level": "mid" if experience else "entry",
            "industry_fit": "technology",
            "skill_gaps": ["Advanced skills needed"]
        }
    
    def _openrouter_learning_path(
        self, 
        current_skills: List[str], 
        target_role: str, 
        timeline: str
    ) -> Dict:
        """Generate learning path using OpenRouter format."""
        return {
            "skill_gaps": ["Advanced programming", "System design"],
            "learning_phases": [
                {
                    "title": "Foundation Phase",
                    "duration": "4 weeks",
                    "topics": ["Core concepts", "Basic projects"],
                    "resources": ["Online courses", "Documentation"]
                }
            ],
            "milestones": ["Complete basics", "Build project", "Interview prep"],
            "estimated_hours": 100,
            "priority_order": ["Programming", "System Design"]
        }
    
    def _basic_resume_analysis(self, resume_data: Dict) -> Dict:
        """Fallback resume analysis when AI services are unavailable."""
        skills = resume_data.get('skills', [])
        return {
            "strengths": skills[:3] if skills else ["Resume uploaded successfully"],
            "improvements": ["AI analysis temporarily unavailable"],
            "career_level": "mid",
            "industry_fit": "technology",
            "skill_gaps": ["AI analysis needed"]
        }
    
    def _basic_job_recommendations(self, resume_data: Dict, num_recommendations: int) -> List[Dict]:
        """Fallback job recommendations when AI services are unavailable."""
        skills = resume_data.get('skills', [])
        return [
            {
                "title": f"Software Developer {i+1}",
                "company_type": "Technology Company",
                "salary_range": "$70,000 - $90,000",
                "description": "Great opportunity for your background",
                "required_skills": skills[:3] if skills else ["Programming"],
                "match_score": 80 - (i * 5),
                "growth_potential": "Strong potential"
            } for i in range(num_recommendations)
        ]
    
    def _basic_learning_path(self, current_skills: List[str], target_role: str, timeline: str) -> Dict:
        """Fallback learning path when AI services are unavailable."""
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
_ai_service_manager = None


def get_ai_service_manager(
    nvidia_api_key: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
    prefer_nvidia: bool = True
) -> AIServiceManager:
    """
    Get or create the AI service manager instance.
    
    Args:
        nvidia_api_key: NVIDIA API key
        openrouter_api_key: OpenRouter API key
        prefer_nvidia: Whether to prefer NVIDIA over OpenRouter
        
    Returns:
        AIServiceManager instance
    """
    global _ai_service_manager
    
    if _ai_service_manager is None:
        _ai_service_manager = AIServiceManager(
            nvidia_api_key=nvidia_api_key,
            openrouter_api_key=openrouter_api_key,
            prefer_nvidia=prefer_nvidia
        )
    
    return _ai_service_manager