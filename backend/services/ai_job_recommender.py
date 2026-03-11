"""
AI-Powered Job Recommendation Service

Uses OpenRouter API to generate diverse, personalized job recommendations
based on resume content instead of just matching against static job files.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from .openrouter_client import OpenRouterClient, get_openrouter_client


class AIJobRecommender:
    """
    Generates personalized job recommendations using OpenRouter API.
    Creates diverse recommendations tailored to each resume.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Job Recommender.
        
        Args:
            api_key: OpenRouter API key. If None, uses default from OpenRouterClient.
        """
        self.client = get_openrouter_client(api_key=api_key)
        if not self.client:
            raise ValueError(
                "OpenRouter API key is required. Set it in openrouter_client.py DEFAULT_API_KEY "
                "or pass as parameter."
            )

    def generate_recommendations(
        self,
        resume_data: Dict,
        *,
        top_n: int = 5,
        domain: Optional[str] = None,
        experience_level: Optional[str] = None,
    ) -> List[Dict]:
        """
        Generate personalized job recommendations based on resume.
        
        Args:
            resume_data: Parsed resume data with skills, experience, education, etc.
            top_n: Number of recommendations to generate
            domain: Optional domain filter (e.g., "data", "web", "mobile")
            experience_level: Optional experience level (e.g., "entry", "mid", "senior")
            
        Returns:
            List of job recommendation dictionaries
        """
        skills = resume_data.get("skills", [])
        experience = resume_data.get("experience", [])
        education = resume_data.get("education", [])
        name = resume_data.get("name", "Candidate")
        
        # Build context from resume
        skills_text = ", ".join(skills[:20]) if skills else "Not specified"
        experience_text = "\n".join(experience[:3]) if experience else "Not specified"
        education_text = "\n".join(education[:2]) if education else "Not specified"
        
        # Build the prompt for OpenRouter
        system_message = (
            "You are an expert career advisor. Generate personalized job recommendations "
            "based on a candidate's resume. Return ONLY valid JSON array, no other text."
        )
        
        prompt = f"""Based on the following resume information, generate {top_n} diverse and personalized job recommendations.

Candidate Information:
- Skills: {skills_text}
- Experience: {experience_text}
- Education: {education_text}
{f"- Domain Preference: {domain}" if domain else ""}
{f"- Experience Level: {experience_level}" if experience_level else ""}

Generate {top_n} different job recommendations that match the candidate's profile. Each recommendation should be unique and relevant.

Return a JSON array with this exact format:
[
  {{
    "title": "Job Title",
    "company_type": "Type of company",
    "salary_range": "Salary range",
    "description": "Job description and requirements",
    "required_skills": ["skill1", "skill2", "skill3"],
    "match_score": 85,
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3", "skill4"],
    "why_good_fit": "Brief explanation why this job matches"
  }}
]

Important:
- Make recommendations diverse (different roles, not just variations of the same job)
- Match score should be 0-100 based on how well the job fits
- Include realistic matched and missing skills
- Provide clear, helpful reasons for each recommendation
- Ensure all {top_n} recommendations are different job titles/roles
"""

        try:
            print(f"Generating AI job recommendations for {len(skills)} skills...")
            response = self.client.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.8,  # Higher temperature for more diversity
                system_message=system_message,
            )
            print(f"Received response from OpenRouter (length: {len(response)})")
            
            # Parse JSON response
            # Sometimes LLM adds markdown code blocks, so we need to extract JSON
            response = response.strip()
            if response.startswith("```"):
                # Remove markdown code blocks
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
            if response.startswith("```json"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
            
            # Try to find JSON array in response
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            if start_idx >= 0 and end_idx > start_idx:
                response = response[start_idx:end_idx]
            
            recommendations = json.loads(response)
            print(f"Parsed {len(recommendations)} recommendations from JSON")
            
            # Validate and format recommendations
            formatted = []
            for rec in recommendations[:top_n]:
                if isinstance(rec, dict):
                    formatted.append({
                        "title": rec.get("title") or rec.get("job_title", "Job Role"),
                        "company_type": rec.get("company_type", "Technology Company"),
                        "salary_range": rec.get("salary_range", "Competitive"),
                        "description": rec.get("description", ""),
                        "required_skills": rec.get("required_skills", rec.get("matched_skills", [])),
                        "match_score": min(100, max(0, int(rec.get("match_score", 70)))),
                        "matched_skills": rec.get("matched_skills", []),
                        "missing_skills": rec.get("missing_skills", []),
                        "why_good_fit": rec.get("why_good_fit") or rec.get("reason", "This role matches your profile."),
                    })
            
            if formatted:
                print(f"Returning {len(formatted)} formatted recommendations")
                return formatted
            else:
                print("No formatted recommendations, using fallback")
                return self._generate_fallback_recommendations(skills, top_n)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from OpenRouter: {e}")
            print(f"Response was: {response[:500]}")
            return self._generate_fallback_recommendations(skills, top_n)
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            return self._generate_fallback_recommendations(skills, top_n)

    def _generate_fallback_recommendations(self, skills: List[str], top_n: int) -> List[Dict]:
        """Generate basic fallback recommendations if AI fails."""
        # Map skills to common job roles
        skill_lower = [s.lower() for s in skills]
        
        jobs = []
        if any(s in skill_lower for s in ["python", "java", "javascript", "react", "node"]):
            jobs.append({
                "title": "Software Developer",
                "company_type": "Technology Company",
                "salary_range": "$70,000 - $100,000",
                "description": "Develop and maintain software applications using modern technologies.",
                "required_skills": ["Python", "JavaScript", "Git", "Problem Solving"],
                "match_score": 75,
                "matched_skills": [s for s in skills if any(tech in s.lower() for tech in ["python", "java", "javascript"])],
                "missing_skills": ["System Design", "Cloud Architecture"],
                "why_good_fit": "Your programming skills align well with software development roles.",
            })
        
        if any(s in skill_lower for s in ["sql", "database", "data", "analytics"]):
            jobs.append({
                "title": "Data Analyst",
                "company_type": "Tech/Analytics Company",
                "salary_range": "$65,000 - $95,000",
                "description": "Analyze data and provide insights to drive business decisions.",
                "required_skills": ["SQL", "Data Analysis", "Excel", "Visualization"],
                "match_score": 70,
                "matched_skills": [s for s in skills if any(tech in s.lower() for tech in ["sql", "data"])],
                "missing_skills": ["Machine Learning", "Statistics"],
                "why_good_fit": "Your data skills are suitable for data analysis positions.",
            })
        
        if any(s in skill_lower for s in ["aws", "cloud", "docker", "kubernetes"]):
            jobs.append({
                "title": "DevOps Engineer",
                "company_type": "Technology Company",
                "salary_range": "$80,000 - $120,000",
                "description": "Manage infrastructure and automate deployment processes.",
                "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD"],
                "match_score": 72,
                "matched_skills": [s for s in skills if any(tech in s.lower() for tech in ["aws", "cloud", "docker"])],
                "missing_skills": ["CI/CD", "Infrastructure as Code"],
                "why_good_fit": "Your cloud and containerization skills match DevOps roles.",
            })
        
        # Fill remaining slots with generic recommendations
        while len(jobs) < top_n:
            jobs.append({
                "title": f"Technology Professional",
                "company_type": "Technology Company",
                "salary_range": "Competitive",
                "description": "Leverage your technical skills in a professional technology role.",
                "required_skills": skills[:3] if skills else ["Technical Skills"],
                "match_score": 65,
                "matched_skills": skills[:3] if skills else [],
                "missing_skills": ["Domain-specific expertise"],
                "why_good_fit": "Your skills align with technology roles.",
                "reason": "General technology role based on your skills.",
            })
        
        return jobs[:top_n]

