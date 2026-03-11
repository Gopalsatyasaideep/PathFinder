"""
Resume-Based Job Matcher using RapidAPI JSearch
Matches jobs from Indeed, LinkedIn, Glassdoor based on resume skills and experience.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional
import requests
from services.web_job_scraper import clean_html


class ResumeBasedJobMatcher:
    """
    Advanced job matching using resume data and RapidAPI JSearch.
    Provides intelligent job recommendations based on skills, experience, and preferences.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the job matcher.
        
        Args:
            api_key: RapidAPI key for JSearch. Falls back to environment or default.
        """
        self.api_key = api_key or os.getenv("RAPIDAPI_KEY") or "c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b"
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.session = requests.Session()
    
    def get_job_recommendations(
        self,
        resume_data: Dict,
        target_role: Optional[str] = None,
        location: str = "remote",
        max_results: int = 15,
        prioritize_india: bool = True,
    ) -> List[Dict]:
        """
        Get personalized job recommendations based on resume.
        
        Args:
            resume_data: Parsed resume with skills, experience, education
            target_role: Desired job title (auto-detected if None)
            location: Preferred location or "remote"
            max_results: Number of jobs to return
            prioritize_india: Prioritize Indian jobs
            
        Returns:
            List of matched jobs with relevance scores
        """
        # Extract resume information
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        education = resume_data.get('education', [])
        
        # Auto-detect target role from experience
        if not target_role:
            target_role = self._detect_target_role(experience, skills)
        
        print(f"🎯 Target Role: {target_role}")
        print(f"💼 Skills: {', '.join(skills[:5])}...")
        
        # Build smart query
        query = self._build_smart_query(target_role, skills)
        
        # Search for jobs
        jobs = self._search_jobs(
            query=query,
            location=location,
            max_results=max_results * 2,  # Get more to filter
            prioritize_india=prioritize_india
        )
        
        # Score and rank jobs based on resume match
        scored_jobs = self._score_jobs(jobs, resume_data)
        
        # Sort by relevance score and return top results
        scored_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return scored_jobs[:max_results]
    
    def _detect_target_role(self, experience: List[Dict], skills: List[str]) -> str:
        """Auto-detect target role from experience and skills."""
        # Try to get from most recent job
        if experience and len(experience) > 0:
            latest_job = experience[0]
            if isinstance(latest_job, dict):
                role = latest_job.get('title', latest_job.get('role', ''))
                if role:
                    return role
        
        # Fallback: detect from skills
        skills_lower = [s.lower() for s in skills]
        
        if any(skill in skills_lower for skill in ['react', 'angular', 'vue', 'frontend']):
            return "Frontend Developer"
        elif any(skill in skills_lower for skill in ['python', 'django', 'flask', 'fastapi', 'backend']):
            return "Backend Developer"
        elif any(skill in skills_lower for skill in ['react', 'node', 'javascript', 'full stack', 'fullstack']):
            return "Full Stack Developer"
        elif any(skill in skills_lower for skill in ['machine learning', 'ml', 'tensorflow', 'pytorch']):
            return "Machine Learning Engineer"
        elif any(skill in skills_lower for skill in ['data science', 'pandas', 'numpy', 'analytics']):
            return "Data Scientist"
        elif any(skill in skills_lower for skill in ['devops', 'docker', 'kubernetes', 'aws', 'cloud']):
            return "DevOps Engineer"
        else:
            return "Software Engineer"
    
    def _build_smart_query(self, target_role: str, skills: List[str]) -> str:
        """Build optimized search query from role and skills."""
        # Base query is the target role
        query = target_role
        
        # Add top relevant skills (max 2-3 to avoid over-filtering)
        relevant_skills = []
        skills_lower = [s.lower() for s in skills]
        
        # Prioritize high-value skills
        priority_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 
            'aws', 'docker', 'kubernetes', 'machine learning', 'sql'
        ]
        
        for skill in priority_skills:
            if skill in skills_lower and len(relevant_skills) < 2:
                relevant_skills.append(skill)
        
        if relevant_skills:
            query += f" {' '.join(relevant_skills)}"
        
        return query
    
    def _search_jobs(
        self,
        query: str,
        location: str,
        max_results: int,
        prioritize_india: bool
    ) -> List[Dict]:
        """Search JSearch API for jobs."""
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        # Build search query
        search_query = query
        if location.lower() == "remote":
            search_query = f"{query} remote"
        elif location.lower() not in ["", "any", "anywhere"]:
            search_query = f"{query} in {location}"
        
        params = {
            "query": search_query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "month"
        }
        
        # Add country filter
        if prioritize_india:
            params["country"] = "in"
        
        if location.lower() == "remote":
            params["remote_jobs_only"] = "true"
        
        try:
            print(f"🔍 Searching: {search_query}")
            response = self.session.get(
                f"{self.base_url}/search",
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('data', [])[:max_results]:
                # Format job data
                job = self._format_job(result)
                jobs.append(job)
            
            print(f"✅ Found {len(jobs)} jobs")
            return jobs
            
        except Exception as e:
            print(f"⚠️ JSearch API error: {e}")
            return []
    
    def _format_job(self, result: Dict) -> Dict:
        """Format raw API result into standardized job dict."""
        # Clean description
        raw_desc = result.get('job_description', '')
        description = clean_html(raw_desc, max_length=500)
        
        # Get salary
        salary_min = result.get('job_min_salary', 0) or 0
        salary_max = result.get('job_max_salary', 0) or 0
        salary_avg = (salary_min + salary_max) / 2 if (salary_min and salary_max) else (salary_min or salary_max)
        
        # Format location
        job_city = result.get('job_city', '')
        job_state = result.get('job_state', '')
        job_country = result.get('job_country', '')
        
        if job_city and job_state:
            location_str = f"{job_city}, {job_state}"
        elif job_city:
            location_str = job_city
        elif job_state:
            location_str = job_state
        elif job_country:
            location_str = job_country
        else:
            location_str = 'Remote' if result.get('job_is_remote') else 'Not Specified'
        
        # Get highlights
        highlights = result.get('job_highlights', {})
        qualifications = highlights.get('Qualifications', [])
        responsibilities = highlights.get('Responsibilities', [])
        benefits = highlights.get('Benefits', [])
        
        return {
            'title': result.get('job_title', 'Unknown'),
            'company': result.get('employer_name', 'Unknown Company'),
            'location': location_str,
            'description': description,
            'url': result.get('job_apply_link') or result.get('job_google_link', ''),
            'salary': int(salary_avg),
            'salary_max': int(salary_max),
            'salary_min': int(salary_min),
            'posted_date': result.get('job_posted_at_datetime_utc', '')[:10] if result.get('job_posted_at_datetime_utc') else '',
            'source': 'JSearch (Indeed/LinkedIn/Glassdoor)',
            'job_type': result.get('job_employment_type', 'Full-time'),
            'is_remote': result.get('job_is_remote', False),
            'company_logo': result.get('employer_logo', ''),
            'qualifications': qualifications[:5] if qualifications else [],
            'responsibilities': responsibilities[:5] if responsibilities else [],
            'benefits': benefits[:3] if benefits else [],
        }
    
    def _score_jobs(self, jobs: List[Dict], resume_data: Dict) -> List[Dict]:
        """
        Score jobs based on resume match.
        Returns jobs with relevance_score field.
        """
        skills = set([s.lower() for s in resume_data.get('skills', [])])
        experience_years = self._calculate_experience_years(resume_data.get('experience', []))
        
        for job in jobs:
            score = 0.0
            
            # 1. Skill match (50% weight)
            job_text = (
                job.get('title', '') + ' ' +
                job.get('description', '') + ' ' +
                ' '.join(job.get('qualifications', []))
            ).lower()
            
            matched_skills = sum(1 for skill in skills if skill in job_text)
            if skills:
                skill_match_ratio = matched_skills / len(skills)
                score += skill_match_ratio * 50
            
            # 2. Experience level match (20% weight)
            job_title_lower = job.get('title', '').lower()
            if experience_years < 2:
                if any(word in job_title_lower for word in ['junior', 'entry', 'associate', 'intern']):
                    score += 20
                elif any(word in job_title_lower for word in ['senior', 'lead', 'principal']):
                    score += 5
            elif experience_years < 5:
                if any(word in job_title_lower for word in ['junior', 'entry']):
                    score += 10
                elif any(word in job_title_lower for word in ['senior', 'lead']):
                    score += 5
                else:
                    score += 20  # Mid-level is good match
            else:  # 5+ years
                if any(word in job_title_lower for word in ['senior', 'lead', 'principal', 'staff']):
                    score += 20
                else:
                    score += 10
            
            # 3. Salary provided (10% weight)
            if job.get('salary', 0) > 0:
                score += 10
            
            # 4. Remote job bonus (10% weight)
            if job.get('is_remote', False):
                score += 10
            
            # 5. Recent posting (10% weight)
            if job.get('posted_date', ''):
                score += 10
            
            job['relevance_score'] = round(score, 2)
            job['matched_skills'] = matched_skills
            job['skill_match_percentage'] = round(skill_match_ratio * 100, 1) if skills else 0
        
        return jobs
    
    def _calculate_experience_years(self, experience: List[Dict]) -> float:
        """Calculate total years of experience."""
        if not experience:
            return 0.0
        
        total_years = 0.0
        for exp in experience:
            if isinstance(exp, dict):
                # Try to get duration
                duration = exp.get('duration', '')
                if 'year' in duration.lower():
                    # Extract number
                    import re
                    years = re.findall(r'\d+', duration)
                    if years:
                        total_years += int(years[0])
        
        return total_years


# Singleton instance
_job_matcher = None


def get_resume_job_matcher(api_key: Optional[str] = None) -> ResumeBasedJobMatcher:
    """Get singleton instance of job matcher."""
    global _job_matcher
    if _job_matcher is None:
        _job_matcher = ResumeBasedJobMatcher(api_key=api_key)
    return _job_matcher
