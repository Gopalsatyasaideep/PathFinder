"""
ATS (Applicant Tracking System) Scorer Service

This service uses NVIDIA's API to score resumes against job descriptions,
providing insights into how well a resume matches specific job requirements.
"""

from typing import Dict, List, Optional, Any
import json
from .nvidia_client import NVIDIAClient, get_nvidia_client


class ATSScorer:
    """
    Scores resumes against job descriptions using NVIDIA's AI model.
    Provides ATS compatibility scores, keyword matches, and improvement suggestions.
    """
    
    def __init__(self, nvidia_client: Optional[NVIDIAClient] = None):
        """
        Initialize ATS Scorer with NVIDIA client.
        
        Args:
            nvidia_client: Optional NVIDIA client. If None, creates a new one.
        """
        self.client = nvidia_client or get_nvidia_client()
        if not self.client:
            raise ValueError("NVIDIA API client is required for ATS scoring")
    
    def score_resume(
        self,
        resume_data: Dict[str, Any],
        job_description: Optional[str] = None,
        job_requirements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Score a resume against a job description or requirements.
        
        Args:
            resume_data: Parsed resume data with skills, experience, etc.
            job_description: Full job description text (optional)
            job_requirements: List of specific job requirements (optional)
            
        Returns:
            Dictionary with ATS score, keyword matches, and recommendations
        """
        # Extract resume components safely
        skills = resume_data.get('skills', []) if isinstance(resume_data, dict) else []
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
        
        experience = resume_data.get('experience_summary', '') if isinstance(resume_data, dict) else str(resume_data)
        if not experience and isinstance(resume_data, dict):
            experience = resume_data.get('experience', '')
            
        education = resume_data.get('education', []) if isinstance(resume_data, dict) else []
        if isinstance(education, str):
            education = [education]
        
        # Build prompt for ATS scoring
        prompt = self._build_scoring_prompt(
            skills=skills,
            experience=experience,
            education=education,
            job_description=job_description,
            job_requirements=job_requirements
        )
        
        try:
            response = self.client.generate_text(
                prompt,
                temperature=0.2,  # Low temperature for consistent scoring
                max_tokens=2048
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Ensure all required fields are present
            return self._validate_and_enhance_result(result, resume_data)
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._generate_fallback_score(resume_data, job_description)
    
    def score_against_job_recommendation(
        self,
        resume_data: Dict[str, Any],
        job_recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score a resume against a specific job recommendation.
        
        Args:
            resume_data: Parsed resume data
            job_recommendation: Job recommendation with title, description, and required_skills
            
        Returns:
            ATS score with detailed analysis
        """
        # Safely extract job information
        job_title = job_recommendation.get('title', 'Unknown Position') if isinstance(job_recommendation, dict) else str(job_recommendation)
        job_description = job_recommendation.get('description', '') if isinstance(job_recommendation, dict) else ''
        required_skills = job_recommendation.get('required_skills', []) if isinstance(job_recommendation, dict) else []
        
        # Handle case where required_skills might be a string
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(',') if s.strip()]
        
        # Combine description and skills into comprehensive job requirements
        full_description = f"{job_title}\n\n{job_description}"
        
        return self.score_resume(
            resume_data=resume_data,
            job_description=full_description,
            job_requirements=required_skills
        )
    
    def batch_score_jobs(
        self,
        resume_data: Dict[str, Any],
        job_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Score resume against multiple job recommendations.
        
        Args:
            resume_data: Parsed resume data
            job_recommendations: List of job recommendations
            
        Returns:
            List of job recommendations with ATS scores added
        """
        scored_jobs = []
        
        print(f"📊 Starting ATS Scoring for {len(job_recommendations)} jobs...")
        
        for i, job in enumerate(job_recommendations):
            try:
                # Handle case where job might be a string instead of dict
                if isinstance(job, str):
                    # Convert string to dict format
                    job = {
                        'title': job,
                        'description': '',
                        'required_skills': []
                    }
                
                job_title = job.get('title', f'Job {i+1}')
                print(f"📊 Scoring job {i+1}/{len(job_recommendations)}: {job_title}")
                
                ats_score = self.score_against_job_recommendation(
                    resume_data=resume_data,
                    job_recommendation=job
                )
                
                print(f"✅ ATS Score for {job_title}: {ats_score.get('overall_score', 0)}/100")
                
                # Add ATS score to job recommendation
                job_with_score = job.copy() if isinstance(job, dict) else {'title': job}
                job_with_score['ats_score'] = ats_score
                scored_jobs.append(job_with_score)
                
            except Exception as e:
                # If scoring fails, add job without score
                job_title = job.get('title', 'Unknown') if isinstance(job, dict) else str(job)
                print(f"❌ Failed to score job {job_title}: {e}")
                job_with_score = job.copy() if isinstance(job, dict) else {'title': str(job)}
                job_with_score['ats_score'] = {
                    "overall_score": 0,
                    "error": str(e)
                }
                scored_jobs.append(job_with_score)
        
        print(f"📊 ATS Scoring Complete: {len(scored_jobs)} jobs processed")
        successful_scores = [j for j in scored_jobs if j.get('ats_score', {}).get('overall_score', 0) > 0]
        print(f"📊 Successfully scored: {len(successful_scores)}/{len(scored_jobs)} jobs")
        if successful_scores:
            avg_score = sum(j['ats_score']['overall_score'] for j in successful_scores) / len(successful_scores)
            print(f"📊 Average ATS Score: {avg_score:.1f}/100")
        
        return scored_jobs
    
    def _build_scoring_prompt(
        self,
        skills: List[str],
        experience: str,
        education: List[Dict],
        job_description: Optional[str],
        job_requirements: Optional[List[str]]
    ) -> str:
        """Build the prompt for ATS scoring."""
        
        # Format education - handle both dict and string items
        education_str = ", ".join([
            f"{edu.get('degree', '') if isinstance(edu, dict) else str(edu)}"
            for edu in education
        ]) if education else "Not specified"
        
        # Format skills - ensure all are strings
        skills_str = ", ".join([str(s) for s in skills]) if skills else "No skills listed"
        
        # Build job requirements section
        job_section = ""
        if job_description:
            job_section = f"\n\nJOB DESCRIPTION:\n{job_description}"
        if job_requirements:
            job_section += f"\n\nREQUIRED SKILLS:\n" + ", ".join(job_requirements)
        
        prompt = f"""
You are an ATS (Applicant Tracking System) expert. Analyze this resume and provide a comprehensive ATS score.

RESUME DATA:
Skills: {skills_str}
Experience: {experience}
Education: {education_str}
{job_section}

Provide a detailed ATS analysis with the following JSON structure:
{{
    "overall_score": <integer 0-100>,
    "category_scores": {{
        "skills_match": <integer 0-100>,
        "experience_match": <integer 0-100>,
        "education_match": <integer 0-100>,
        "formatting": <integer 0-100>
    }},
    "keyword_matches": {{
        "matched_keywords": [<list of matched keywords>],
        "missing_keywords": [<list of important missing keywords>],
        "match_percentage": <integer 0-100>
    }},
    "strengths": [<3-5 key strengths as strings>],
    "improvement_areas": [<3-5 areas to improve as strings>],
    "ats_recommendations": [<3-5 specific recommendations for improving ATS score>],
    "pass_likelihood": "<high/medium/low>",
    "summary": "<2-3 sentence summary of the ATS analysis>"
}}

Be specific and actionable in your recommendations. Focus on ATS compatibility and keyword optimization.
"""
        
        return prompt
    
    def _validate_and_enhance_result(
        self,
        result: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and enhance the ATS scoring result."""
        
        # Ensure required fields exist
        if 'overall_score' not in result:
            result['overall_score'] = 70
        
        if 'category_scores' not in result:
            result['category_scores'] = {
                "skills_match": 70,
                "experience_match": 70,
                "education_match": 70,
                "formatting": 85
            }
        
        if 'keyword_matches' not in result:
            result['keyword_matches'] = {
                "matched_keywords": resume_data.get('skills', [])[:5],
                "missing_keywords": [],
                "match_percentage": 70
            }
        
        if 'strengths' not in result:
            result['strengths'] = ["Clear skill presentation", "Relevant experience"]
        
        if 'improvement_areas' not in result:
            result['improvement_areas'] = ["Add more keywords", "Quantify achievements"]
        
        if 'ats_recommendations' not in result:
            result['ats_recommendations'] = [
                "Include more industry-specific keywords",
                "Use standard section headings",
                "Add measurable achievements"
            ]
        
        if 'pass_likelihood' not in result:
            score = result['overall_score']
            if score >= 80:
                result['pass_likelihood'] = "high"
            elif score >= 60:
                result['pass_likelihood'] = "medium"
            else:
                result['pass_likelihood'] = "low"
        
        if 'summary' not in result:
            result['summary'] = f"Resume scored {result['overall_score']}/100 with {result['pass_likelihood']} likelihood of passing ATS screening."
        
        return result
    
    def _generate_fallback_score(
        self,
        resume_data: Dict[str, Any],
        job_description: Optional[str]
    ) -> Dict[str, Any]:
        """Generate a basic fallback score if AI analysis fails."""
        
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience_summary', '')
        
        # Simple scoring logic
        base_score = 60
        if len(skills) >= 5:
            base_score += 10
        if len(skills) >= 10:
            base_score += 10
        if experience and len(experience) > 50:
            base_score += 10
        
        return {
            "overall_score": base_score,
            "category_scores": {
                "skills_match": base_score,
                "experience_match": base_score,
                "education_match": base_score,
                "formatting": 80
            },
            "keyword_matches": {
                "matched_keywords": skills[:5],
                "missing_keywords": [],
                "match_percentage": base_score
            },
            "strengths": [
                "Resume parsed successfully",
                f"Contains {len(skills)} identified skills"
            ],
            "improvement_areas": [
                "Consider adding more specific keywords",
                "Quantify achievements with metrics"
            ],
            "ats_recommendations": [
                "Add industry-specific keywords",
                "Use standard resume section headings",
                "Include measurable results"
            ],
            "pass_likelihood": "medium" if base_score >= 60 else "low",
            "summary": f"Basic ATS analysis complete. Score: {base_score}/100. Consider detailed review for optimization."
        }


def get_ats_scorer(nvidia_client: Optional[NVIDIAClient] = None) -> Optional[ATSScorer]:
    """
    Factory function to create ATS scorer.
    Returns None if NVIDIA client is not available.
    """
    try:
        return ATSScorer(nvidia_client=nvidia_client)
    except ValueError:
        return None
