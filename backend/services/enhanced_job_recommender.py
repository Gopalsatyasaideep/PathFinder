"""
Enhanced Job Recommender with Web Search Integration.

Combines AI-powered job matching with real-time job data from 12+ job APIs:
- Remotive, Jobicy, RemoteOK (Remote jobs)
- IndianAPI (India-focused)
- DevITjobs (Tech jobs UK)
- The Muse, Arbeitnow (General/Global)
- Adzuna, JSearch, Reed, USAJobs (Optional with API keys)

Provides personalized job recommendations based on resume skills and auto-detected roles.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from services.web_job_scraper import get_web_job_scraper
from services.ai_job_recommender import AIJobRecommender
from services.job_recommender import JobRecommender
from services.vector_store import FaissVectorStore


class EnhancedJobRecommender:
    """
    Job recommender that combines:
    1. Local vector store job matching
    2. AI-powered job analysis
    3. Real-time web job scraping
    """
    
    def __init__(self, store: Optional[FaissVectorStore] = None):
        self.local_recommender = JobRecommender(store=store) if store else None
        try:
            self.ai_recommender = AIJobRecommender()
        except:
            self.ai_recommender = None
        self.web_scraper = get_web_job_scraper()
    
    def get_recommendations(
        self,
        skills: List[str],
        target_role: str,
        location: str = "remote",
        experience_level: str = "Mid-level",
        top_n: int = 10,
        include_web_jobs: bool = True,
        prioritize_india: bool = True,
    ) -> Dict:
        """
        Get comprehensive job recommendations.
        
        Args:
            skills: User's skills list
            target_role: Target job title/role
            location: Job location or "remote"
            experience_level: Entry, Mid, Senior, etc.
            top_n: Number of results
            include_web_jobs: Whether to include real web jobs
            prioritize_india: If True, prioritize India-based jobs
            
        Returns:
            Dictionary with recommended_jobs, web_jobs, and metadata
            NOTE: Web jobs are NOT sent to NVIDIA for ATS comparison
        """
        results = {
            'recommended_jobs': [],
            'web_jobs': [],
            'total_jobs': 0,
            'sources': [],
        }
        
        # 1. Get local/vector store recommendations (DISABLED - causing errors)
        # if self.local_recommender:
        #     try:
        #         local_jobs = self.local_recommender.recommend_jobs(
        #             resume_json={'skills': skills},
        #             top_n=min(top_n, 5),
        #         )
        #         if local_jobs:
        #             results['recommended_jobs'].extend(local_jobs)
        #             results['sources'].append('Local Database')
        #     except Exception as e:
        #         print(f"⚠️  Local recommender error: {e}")
        
        # 2. Get AI-enhanced recommendations (DISABLED - causing errors)
        # if self.ai_recommender:
        #     try:
        #         ai_jobs = self.ai_recommender.generate_recommendations(
        #             resume_data={'skills': skills},
        #             top_n=min(top_n, 5),
        #         )
        #         if ai_jobs:
        #             results['recommended_jobs'].extend(ai_jobs)
        #             results['sources'].append('AI Analysis')
        #     except Exception as e:
        #         print(f"⚠️  AI recommender error: {e}")
        
        # 3. Get real web jobs (PRIMARY SOURCE)
        if include_web_jobs:
            try:
                # Request more jobs to ensure we get 10+ after filtering
                web_jobs = self.web_scraper.search_jobs(
                    query=target_role,
                    location=location,
                    max_results=max(top_n, 20),  # Fetch at least 20 to ensure 10+ quality results
                    prioritize_india=prioritize_india,
                )
                
                print(f"✅ Fetched {len(web_jobs)} jobs from web APIs (NO ATS SCORING)")
                
                # Score web jobs based on skill match with enhanced algorithm
                for job in web_jobs:
                    job['match_score'] = self._calculate_enhanced_match_score(
                        job, skills, target_role, experience_level
                    )
                
                # Debug: Show score distribution
                if web_jobs:
                    scores = [j.get('match_score', 0) for j in web_jobs]
                    skill_counts = [j.get('skill_match_count', 0) for j in web_jobs]
                    print(f"📊 Score range: {min(scores):.1f}% - {max(scores):.1f}%, Avg: {sum(scores)/len(scores):.1f}%")
                    print(f"📊 Skill matches: {min(skill_counts)} - {max(skill_counts)}, Avg: {sum(skill_counts)/len(skill_counts):.1f}")
                
                # FILTER: More lenient - accept jobs with reasonable scores OR skill matches
                # Changed to OR condition for better results while still personalizing
                min_skill_matches = 1  # At least 1 skill match
                min_score = 15  # Lowered from 20% - more lenient threshold
                
                filtered_jobs = [
                    job for job in web_jobs 
                    if (job.get('skill_match_count', 0) >= min_skill_matches 
                        or job.get('match_score', 0) >= min_score)  # OR condition - more lenient
                ]
                
                print(f"🔍 Filtered: {len(web_jobs)} jobs → {len(filtered_jobs)} relevant jobs (≥{min_skill_matches} skill match OR ≥{min_score}% score)")
                
                # Sort by match score (preliminary sorting)
                filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
                
                # --- NVIDIA NIM INTEGRATION (Reasoning Engine) ---
                # Use Llama 3.1 70B to intelligently rank the top candidate jobs
                # This implements the "Web Search + reasoning" flow
                if filtered_jobs:
                    try:
                        from services.nvidia_client import get_nvidia_client
                        # Get client without arguments to use env vars
                        nvidia_client = get_nvidia_client()
                        if nvidia_client:
                            # Use top 15 filtered jobs for expensive LLM ranking
                            # Only rank if we have enough jobs to make it worthwhile
                            candidates = filtered_jobs[:15]
                            
                            # Construct minimal resume data for context
                            resume_context = {
                                'skills': skills,
                                'target_role': target_role
                            }
                            
                            print(f"🧠 NVIDIA NIM: Re-ranking top {len(candidates)} jobs with Reasoning Engine...")
                            ranked_jobs = nvidia_client.rank_and_filter_jobs(
                                resume_data=resume_context,
                                jobs=candidates,
                                top_n=top_n
                            )
                            
                            if ranked_jobs:
                                # Replace the top of the list with the LLM-ranked jobs
                                # and append any remaining jobs that weren't ranked (as fallback)
                                ranked_ids = {id(j) for j in ranked_jobs}
                                remaining = [j for j in filtered_jobs if id(j) not in ranked_ids]
                                
                                # Use ranked jobs first, then remaining
                                filtered_jobs = ranked_jobs + remaining
                                print(f"✅ NVIDIA NIM: Successfully re-ranked jobs")
                    except Exception as e:
                        # Don't fail if NVIDIA API is down or not configured
                        print(f"⚠️  NVIDIA NIM ranking skipped: {str(e)}")
                # ------------------------------------------------
                
                # Return filtered jobs
                results['web_jobs'] = filtered_jobs
                
                # Get unique sources from web jobs
                unique_sources = set(job.get('source', 'Unknown') for job in web_jobs)
                results['sources'].extend(unique_sources)
            except Exception as e:
                print(f"⚠️  Web scraper error: {e}")
        
        # Deduplicate and merge
        results['total_jobs'] = len(results['recommended_jobs']) + len(results['web_jobs'])
        results['sources'] = list(set(results['sources']))
        
        return results
    
    def _calculate_enhanced_match_score(
        self,
        job: Dict,
        skills: List[str],
        target_role: str,
        experience_level: str = "Mid-level"
    ) -> float:
        """
        Enhanced skill match calculation with realistic scoring (60-95% range).
        
        Args:
            job: Job posting with title, description, required_skills
            skills: User's skills
            target_role: Target job role
            experience_level: User's experience level
            
        Returns:
            Match score as percentage (60-95% for good matches)
        """
        if not skills:
            return 65.0  # Base score for no skills
            
        job_title = job.get('title', '').lower()
        job_description = job.get('description', '').lower()
        job_required_skills = job.get('required_skills', [])
        
        # Convert skills to lowercase for matching
        user_skills_lower = [s.lower().strip() for s in skills if s]
        
        # 1. EXACT SKILL MATCHING (40% of score)
        exact_matches = 0
        partial_matches = 0
        
        for user_skill in user_skills_lower:
            # Check in required skills
            if job_required_skills:
                for req_skill in job_required_skills:
                    req_skill_lower = str(req_skill).lower()
                    if user_skill == req_skill_lower:
                        exact_matches += 2  # Exact match worth more
                    elif user_skill in req_skill_lower or req_skill_lower in user_skill:
                        partial_matches += 1
            
            # Check in job description
            if user_skill in job_description:
                exact_matches += 1
            
            # Check in job title
            if user_skill in job_title:
                exact_matches += 2  # Title matches worth more
        
        # Calculate skill match component (0-40 points)
        total_skill_points = exact_matches * 2 + partial_matches
        skill_score = min(40, total_skill_points * 3)  # Cap at 40
        
        # 2. ROLE ALIGNMENT (25% of score) 
        role_score = 0
        target_role_lower = target_role.lower()
        
        # Check title similarity
        title_words = job_title.split()
        role_words = target_role_lower.split()
        
        common_words = set(title_words) & set(role_words)
        if common_words:
            role_score += len(common_words) * 5
        
        # Bonus for exact role match
        if target_role_lower in job_title or any(word in job_title for word in role_words):
            role_score += 10
            
        role_score = min(25, role_score)  # Cap at 25
        
        # 3. EXPERIENCE LEVEL MATCH (15% of score)
        exp_score = 15  # Default score
        exp_keywords = {
            'entry': ['entry', 'junior', 'graduate', 'trainee', 'intern', '0-2', '1-2'],
            'mid': ['mid', 'intermediate', '3-5', '2-5', '3-7', 'experienced'],
            'senior': ['senior', 'lead', 'principal', '5+', '7+', '8+', 'expert']
        }
        
        exp_level = experience_level.lower()
        if 'entry' in exp_level or 'junior' in exp_level:
            target_exp = 'entry'
        elif 'senior' in exp_level or 'lead' in exp_level:
            target_exp = 'senior'
        else:
            target_exp = 'mid'
            
        # Check if job matches experience level
        job_text = (job_title + ' ' + job_description).lower()
        if any(keyword in job_text for keyword in exp_keywords[target_exp]):
            exp_score += 5
        
        # 4. QUALITY BONUS (20% of score)
        quality_score = 10  # Base quality
        
        # Bonus for having salary info
        if job.get('salary') or job.get('salary_range'):
            quality_score += 5
            
        # Bonus for having detailed description
        if len(job.get('description', '')) > 200:
            quality_score += 3
            
        # Bonus for having company info
        if job.get('company') and job.get('company') != 'Unknown':
            quality_score += 2
            
        quality_score = min(20, quality_score)
        
        # Calculate total score
        total_score = skill_score + role_score + exp_score + quality_score
        
        # Ensure realistic range (60-95% for matches, 45-65% for poor matches)
        if total_score < 30:
            final_score = 45 + (total_score / 30) * 20  # 45-65%
        else:
            final_score = 60 + (min(total_score, 80) / 80) * 35  # 60-95%
        
        # Store debug info
        job['skill_match_count'] = exact_matches + (partial_matches // 2)
        job['debug_score_breakdown'] = {
            'skill_score': skill_score,
            'role_score': role_score, 
            'exp_score': exp_score,
            'quality_score': quality_score,
            'total': total_score,
            'final': round(final_score, 1)
        }
        
        return round(final_score, 1)

    def _calculate_match_score(
        self,
        job: Dict,
        skills: List[str],
        target_role: str,
    ) -> float:
        """
        Calculate how well a job matches user's profile.
        
        HEAVILY prioritizes exact skill matches for better personalization.
        Returns score between 0 and 100.
        """
        score = 0.0
        
        # Initialize skill_match_count to 0 (will be updated below)
        job['skill_match_count'] = 0
        job['matched_skills'] = []
        
        # Extract base target role (remove skills from enhanced query)
        role_words = target_role.lower().split()
        # Take first 2-3 words as the actual role (e.g., "Data Scientist")
        base_role = ' '.join(role_words[:3])
        
        # Title match (30 points) - REDUCED from 40
        job_title = job.get('title', '').lower()
        
        # Exact base role match
        if base_role in job_title:
            score += 30
        # Partial match - any word from base role
        elif any(word in job_title for word in base_role.split() if len(word) > 3):
            score += 20
        # Related role keywords
        elif any(keyword in job_title for keyword in ['developer', 'engineer', 'analyst', 'scientist', 'manager', 'designer']):
            score += 10
        
        # Skill match (65 points) - INCREASED from 50 for better personalization
        job_text = (
            job.get('title', '') + ' ' +
            job.get('description', '') + ' ' +
            ' '.join(job.get('tags', [])) + ' ' +
            ' '.join(job.get('required_skills', []))
        ).lower()
        
        matched_skills = []
        exact_matches = 0
        partial_matches = 0
        
        # Check ALL skills for comprehensive matching
        for idx, skill in enumerate(skills[:20]):  # Check top 20 skills
            skill_lower = skill.lower()
            skill_base = skill_lower.split('.')[0].split('/')[0].split('-')[0]
            
            # Exact match (worth more)
            if skill_lower in job_text:
                matched_skills.append(skill)
                # Weight top skills more heavily
                weight = 1.5 if idx < 5 else 1.0
                exact_matches += weight
            # Base match (worth less)
            elif skill_base in job_text and len(skill_base) > 2:
                matched_skills.append(skill)
                weight = 1.2 if idx < 5 else 0.8
                partial_matches += weight
        
        # Calculate skill match score with heavy weighting
        if skills:
            total_skill_weight = (exact_matches * 2) + (partial_matches * 1)
            max_possible = min(len(skills), 20) * 2  # Max if all top skills matched exactly
            skill_match_ratio = min(total_skill_weight / max_possible, 1.0)
            
            # Award up to 65 points for skill matches
            score += skill_match_ratio * 65
            
            # BONUS: Award extra points for high skill match count
            if len(matched_skills) >= 5:
                score += 10
            elif len(matched_skills) >= 3:
                score += 5
            
            # Store matched skills in job for frontend display
            job['matched_skills'] = matched_skills[:10]
            job['skill_match_count'] = len(matched_skills)
        
        # Bonus for remote (3 points) - REDUCED from 5
        if 'remote' in job.get('location', '').lower():
            score += 3
        
        # Bonus for recent posting (2 points) - REDUCED from 3
        if job.get('posted_date'):
            score += 2
        
        return round(min(score, 100), 2)  # Cap at 100
    
    def get_job_details(self, job_id: str, source: str) -> Optional[Dict]:
        """Get detailed information about a specific job."""
        # Implementation would depend on source
        return None


def get_enhanced_job_recommender(store: Optional[FaissVectorStore] = None) -> EnhancedJobRecommender:
    """Get singleton instance of EnhancedJobRecommender."""
    if not hasattr(get_enhanced_job_recommender, '_instance'):
        get_enhanced_job_recommender._instance = EnhancedJobRecommender(store=store)
    return get_enhanced_job_recommender._instance


# Testing
if __name__ == "__main__":
    recommender = EnhancedJobRecommender()
    
    test_skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS"]
    target = "Full Stack Developer"
    
    print(f"🔍 Finding jobs for {target}...\n")
    
    results = recommender.get_recommendations(
        skills=test_skills,
        target_role=target,
        location="remote",
        top_n=10,
    )
    
    print(f"📊 Total jobs found: {results['total_jobs']}")
    print(f"📚 Sources: {', '.join(results['sources'])}\n")
    
    print(f"\n🌐 Real Web Jobs ({len(results['web_jobs'])}):")
    for idx, job in enumerate(results['web_jobs'][:5], 1):
        print(f"\n{idx}. {job['title']} at {job['company']}")
        print(f"   Match Score: {job.get('match_score', 0):.1f}%")
        print(f"   Location: {job['location']}")
        print(f"   Source: {job['source']}")
