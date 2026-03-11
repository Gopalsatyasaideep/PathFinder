"""
NVIDIA API Client for PathFinder AI

Uses NVIDIA's integration platform with multiple Llama models:
- Llama 3.1 405B for technical mock interviews
- Llama 3 70B for behavioral mock interviews  
- Qwen 3 Next 80B for resume analysis and job recommendations
"""

import os
import json
from typing import Dict, List, Optional, Iterator
from openai import OpenAI


class NVIDIAClient:
    """
    Client for NVIDIA API using OpenAI-compatible interface.
    Uses specialized Llama models for mock interviews and Qwen for other features.
    """
    
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    DEFAULT_MODEL = "meta/llama-3.1-405b-instruct"
    WEB_SEARCH_MODEL = "meta/llama-3.1-405b-instruct"
    # Mock Interview Models
    LLAMA_405B_MODEL = "meta/llama-3.1-405b-instruct"  # For technical/coding interviews
    LLAMA_70B_MODEL = "meta/llama-3.1-405b-instruct"  # For behavioral/HR/case-study interviews
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize NVIDIA client.
        
        Args:
            api_key: NVIDIA API key. If None, looks for NVIDIA_API_KEY env var.
            model: Model to use. Defaults to Qwen 3 Next 80B.
        """
        # Use provided key, then env var, then hardcoded fallback
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY") or "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"
        if not self.api_key:
            raise ValueError(
                "NVIDIA API key is required. Set NVIDIA_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model or self.DEFAULT_MODEL
        self.client = OpenAI(
            base_url=self.BASE_URL,
            api_key=self.api_key
        )

    def rank_and_filter_jobs(self, resume_data: Dict, jobs: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        Intelligently rank and filter jobs using NVIDIA NIM (Llama 3.1 70B).
        This implements the "Reasoning Engine" part of the Web Search flow.
        
        Flow: Web Search Results (Tool) -> NIM LLM (Reasoning) -> Final Answer
        """
        if not jobs:
            return []
            
        print(f"🤖 NVIDIA Job Ranking: Analyzing {len(jobs)} jobs with {self.WEB_SEARCH_MODEL}...")
        
        # Prepare condensed resume summary
        skills = resume_data.get('skills', [])
        if isinstance(skills, str):
            skills = skills.split(',')
        skills_str = ", ".join(skills[:20])  # Top 20 skills
        
        # Prepare job list for prompt (condensed to save tokens)
        job_list_text = ""
        for idx, job in enumerate(jobs):
            desc = job.get('description', '')[:200].replace('\n', ' ')
            job_list_text += f"ID: {idx}\nTitle: {job.get('title')}\nCompany: {job.get('company')}\nSkills: {', '.join(job.get('matched_skills', []))}\nSummary: {desc}...\n\n"

        prompt = f"""
You are an expert technical recruiter matching candidates to jobs.

CANDIDATE PROFILE:
Skills: {skills_str}
Role: {resume_data.get('target_role', 'Software Engineer')}

JOB LIST (Web Search Results):
{job_list_text}

TASK:
Identify the top {top_n} best matching jobs for this candidate from the list above.
Rank them by relevance to the candidate's skills and profile.
Ignore jobs that are clearly irrelevant.

RETURN ONLY A VALID JSON ARRAY of indices for the selected jobs, ordered by relevance.
Example: [3, 0, 5, 2]

Do not return any other text.
"""
        
        try:
            # specifically use the model recommended for reasoning/search
            completion = self.client.chat.completions.create(
                model=self.WEB_SEARCH_MODEL, # Uses Llama 3.1 70B as recommended
                messages=[
                    {"role": "system", "content": "You are a precise job matching engine. Output strictly JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Low temperature for consistent ranking
                max_tokens=100
            )
            
            response_text = completion.choices[0].message.content.strip()
            # Clean up potential markdown formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            selected_indices = json.loads(response_text)
            
            if not isinstance(selected_indices, list):
                print(f"⚠️ NVIDIA Ranking returned invalid format: {response_text}")
                return jobs[:top_n] # Fallback to original order
                
            # Construct result list in ranked order
            ranked_jobs = []
            for idx in selected_indices:
                if 0 <= idx < len(jobs):
                    job = jobs[idx]
                    # Add reasoning metadata
                    job['ai_reasoning'] = "Selected by NVIDIA NIM based on skill profile match."
                    ranked_jobs.append(job)
                    
            print(f"✅ NVIDIA Ranking: Selected {len(ranked_jobs)} best matches")
            return ranked_jobs
            
        except Exception as e:
            print(f"❌ NVIDIA Ranking failed: {e}")
            return jobs[:top_n] # Fallback to original order
    
    def generate_text(
        self,
        prompt: str,
        *,
        temperature: float = 0.6,
        top_p: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text using NVIDIA API.
        
        Args:
            prompt: Input prompt for text generation
            temperature: Controls randomness (0.0-1.0)
            top_p: Controls diversity via nucleus sampling
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            model: Specific model to use (overrides default)
            
        Returns:
            Generated text response
        """
        try:
            use_model = model or self.model
            
            completion = self.client.chat.completions.create(
                model=use_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                full_response = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                # Handle regular response
                return completion.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"NVIDIA API error: {str(e)}")
    
    def generate_interview_questions(
        self,
        prompt: str,
        interview_type: str,
        *,
        temperature: float = 0.2,
        top_p: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate interview questions using appropriate model based on interview type.
        
        - Uses Llama 3.1 405B for technical/coding interviews (temp=0.2, top_p=0.7)
        - Uses Llama 3 70B for behavioral/HR/case-study interviews (temp=0.5, top_p=1.0)
        
        Args:
            prompt: Question generation prompt
            interview_type: Type of interview (technical, behavioral, case-study, hr, mixed)
            temperature: Controls randomness (default varies by model)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated questions in JSON format
        """
        # Select model based on interview type with optimized parameters
        if interview_type.lower() in ['technical', 'coding']:
            model = self.LLAMA_405B_MODEL
            temp = 0.2
            top_p_val = 0.7
            print(f"🤖 Using Llama 3.1 405B for technical interview questions")
        else:
            model = self.LLAMA_70B_MODEL
            temp = 0.5
            top_p_val = 1.0
            print(f"🤖 Using Llama 3 70B for {interview_type} interview questions")
        
        return self.generate_text(
            prompt,
            temperature=temp,
            top_p=top_p_val,
            max_tokens=max_tokens,
            model=model
        )
    
    def evaluate_interview_answers(
        self,
        prompt: str,
        interview_type: str,
        *,
        temperature: float = 0.2,
        top_p: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Evaluate interview answers using appropriate model based on interview type.
        
        - Uses Llama 3.1 405B for technical/coding answers (temp=0.2, top_p=0.7)
        - Uses Llama 3 70B for behavioral/HR/case-study answers (temp=0.5, top_p=1.0)
        
        Args:
            prompt: Evaluation prompt
            interview_type: Type of interview (technical, behavioral, case-study, hr, mixed)
            temperature: Controls randomness (default varies by model)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            Evaluation results in JSON format
        """
        # Select model based on interview type with optimized parameters
        if interview_type.lower() in ['technical', 'coding']:
            model = self.LLAMA_405B_MODEL
            temp = 0.2
            top_p_val = 0.7
            print(f"🤖 Using Llama 3.1 405B for technical answer evaluation")
        else:
            model = self.LLAMA_70B_MODEL
            temp = 0.5
            top_p_val = 1.0
            print(f"🤖 Using Llama 3 70B for {interview_type} answer evaluation")
        
        return self.generate_text(
            prompt,
            temperature=temp,
            top_p=top_p_val,
            max_tokens=max_tokens,
            model=model
        )
    
    def generate_resume_analysis(self, resume_data: Dict) -> Dict:
        """
        Generate comprehensive resume analysis using NVIDIA's Qwen model.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            Analysis results including strengths, gaps, and recommendations
        """
        # Safely extract data with fallbacks
        skills = resume_data.get('skills', []) if isinstance(resume_data, dict) else []
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
        skills_str = ", ".join(skills) if skills else "General technical skills"
        
        experience = resume_data.get('experience_summary', 'No experience provided') if isinstance(resume_data, dict) else str(resume_data)
        if not experience and isinstance(resume_data, dict):
            experience = resume_data.get('experience', 'No experience provided')
        
        education_raw = resume_data.get('education', []) if isinstance(resume_data, dict) else []
        if isinstance(education_raw, str):
            education_raw = [education_raw]
        education = ", ".join([f"{edu.get('degree', '')} in {edu.get('field', '')}" if isinstance(edu, dict) else str(edu)
                              for edu in education_raw]) if education_raw else "Not specified"
        
        prompt = f"""
You are an expert career advisor analyzing a resume. Provide a comprehensive assessment.

**RESUME DATA:**
Skills: {skills_str}
Experience: {experience}
Education: {education}

**INSTRUCTIONS:**
Analyze this resume and return ONLY a valid JSON object with no additional text.

**REQUIRED JSON FORMAT:**
{{
  "strengths": ["strength 1", "strength 2", "strength 3", "strength 4", "strength 5"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3", "improvement 4"],
  "career_level": "entry" or "mid" or "senior",
  "industry_fit": "best industry match",
  "skill_gaps": ["skill gap 1", "skill gap 2", "skill gap 3"]
}}

**ANALYSIS CRITERIA:**
- Strengths: List 5 key strengths based on skills, experience, and achievements
- Improvements: List 4 actionable areas to enhance resume and career prospects
- Career Level: Determine if entry (0-2 years), mid (3-7 years), or senior (8+ years)
- Industry Fit: Best industry match based on skills and experience
- Skill Gaps: Identify 3 missing skills that would enhance career prospects

Return ONLY the JSON object, no markdown formatting, no explanations.
"""
        
        print(f"🤖 NVIDIA Resume Analysis Request:")
        print(f"   Skills: {skills_str}")
        print(f"   Experience: {experience[:200]}...")
        print(f"   Education: {education}")
        
        response = self.generate_text(prompt, temperature=0.2)
        
        print(f"🤖 NVIDIA Resume Analysis Response:")
        print(f"   Raw Response: {response[:500]}...")
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('```')[1]
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            
            print(f"✅ Resume Analysis Parsed Successfully:")
            print(f"   Strengths: {len(result.get('strengths', []))} items")
            print(f"   Improvements: {len(result.get('improvements', []))} items")
            print(f"   Career Level: {result.get('career_level', 'unknown')}")
            print(f"   Industry Fit: {result.get('industry_fit', 'unknown')}")
            print(f"   Skill Gaps: {len(result.get('skill_gaps', []))} items")
            
            # Validate required fields
            required_fields = ['strengths', 'improvements', 'career_level', 'industry_fit', 'skill_gaps']
            if all(field in result for field in required_fields):
                return result
            else:
                raise ValueError("Missing required fields")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Failed to parse resume analysis JSON: {e}")
            print(f"❌ Raw response was: {response}")
            # Fallback with sensible defaults
            return {
                "strengths": [
                    f"Possesses {len(resume_data.get('skills', []))} technical skills",
                    "Demonstrated experience in the field",
                    "Relevant educational background",
                    "Well-rounded skill set",
                    "Ready for next career opportunity"
                ],
                "improvements": [
                    "Add more quantifiable achievements",
                    "Highlight leadership experience",
                    "Include industry-specific keywords",
                    "Expand on project outcomes"
                ],
                "career_level": "mid",
                "industry_fit": "technology",
                "skill_gaps": [
                    "Advanced certifications",
                    "Cloud computing expertise",
                    "Leadership and management skills"
                ]
            }
    
    def generate_job_recommendations(
        self, 
        resume_data: Dict, 
        num_recommendations: int = 5
    ) -> List[Dict]:
        """
        Generate personalized job recommendations using NVIDIA's Qwen model.
        Uses detected target_role from resume data for more accurate recommendations.
        
        Args:
            resume_data: Parsed resume data (may include target_role from detection)
            num_recommendations: Number of job recommendations to generate
            
        Returns:
            List of job recommendation dictionaries
        """
        # Safely extract data with fallbacks
        skills = resume_data.get('skills', []) if isinstance(resume_data, dict) else []
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
        skills_str = ", ".join(skills) if skills else "General technical skills"
        
        # Get detected target role if available
        target_role = resume_data.get('target_role', None)
        role_level = resume_data.get('role_level', 'mid')
        industry = resume_data.get('industry', 'Technology')
        
        experience = resume_data.get('experience_summary', '') if isinstance(resume_data, dict) else str(resume_data)
        if not experience and isinstance(resume_data, dict):
            experience = resume_data.get('experience', '')
        if not experience:
            experience = "Professional experience in technology"
        # Ensure experience is always a string
        if not isinstance(experience, str):
            experience = str(experience) if experience else "Professional experience in technology"
            
        education = resume_data.get('education', []) if isinstance(resume_data, dict) else []
        if isinstance(education, str):
            education = [education]
        education_str = ", ".join([f"{edu.get('degree', '')} in {edu.get('field', '')}" if isinstance(edu, dict) else str(edu) for edu in education]) if education else "Computer Science or related field"
        
        # Calculate experience level - ensure experience is string
        experience_lower = str(experience).lower() if experience else ""
        if role_level == 'senior' or any(word in experience_lower for word in ['senior', '8+', '10+', 'lead', 'principal']):
            exp_level = 'senior'
            exp_years = '8+'
        elif role_level == 'mid' or any(word in experience_lower for word in ['mid', '3-5', '5-7', 'intermediate']):
            exp_level = 'mid'
            exp_years = '3-7'
        else:
            exp_level = 'entry'
            exp_years = '0-2'
        
        # Build role-specific guidance
        role_guidance = ""
        if target_role:
            role_guidance = f"""
**DETECTED TARGET ROLE:** {target_role}

PRIMARY FOCUS: Generate recommendations centered around {target_role} but include diverse variations:
- Direct {target_role} positions (40% of recommendations)
- Related roles in same domain (30%)
- Adjacent career paths and growth opportunities (30%)

This ensures recommendations are relevant while maintaining diversity."""
        
        prompt = f"""
You are an expert technical recruiter analyzing a candidate profile to recommend diverse, high-quality job matches.

**CANDIDATE PROFILE:**
- Primary Skills: {skills_str}
- Experience Level: {exp_level} ({exp_years} years)
- Industry Focus: {industry}
- Experience Summary: {experience}
- Education: {education_str}

{role_guidance}

**TASK:**
Recommend {num_recommendations} DIVERSE job positions from different industries, company sizes, and role types. 
Focus on VARIETY - avoid recommending similar positions!

**DIVERSITY REQUIREMENTS:**
1. Mix of industries: Technology, Finance, Healthcare, E-commerce, Consulting, Startups
2. Mix of company types: Big Tech, Startups, Fortune 500, Consulting, Government, Non-profit
3. Mix of role types: IC roles, Team Lead, Specialist, Generalist, Remote-first, Hybrid
4. Different career paths: Technical depth, Management track, Product-focused, Customer-facing
5. Salary ranges that reflect market reality for each industry/location

**QUALITY CRITERIA:**
- 70-95% skill alignment (realistic matches, not 100%)
- Appropriate seniority level for candidate experience
- Realistic salary ranges for industry/location
- Strong growth potential in different directions
- Consider remote work trends and location flexibility

**REQUIRED JSON FORMAT:**
Return ONLY a valid JSON array with no additional text. Each job must have this exact structure:
[
  {{
    "title": "Specific Job Title (varied and unique)",
    "company": "Example company name in that industry",
    "company_type": "Company type (Tech Giant, FinTech Startup, Healthcare Corp, etc.)",
    "location": "City, State or Remote",
    "job_type": "Full-time, Contract, Remote, Hybrid",
    "salary_range": "Realistic USD salary range for this role/industry",
    "description": "2-3 sentence role description focusing on unique aspects",
    "required_skills": ["5-6 specific skills relevant to this role"],
    "matched_skills": ["3-4 candidate skills that match this role"],
    "missing_skills": ["2-3 skills candidate should learn for this role"],
    "match_score": 75,
    "growth_potential": "Specific career growth path for this role type",
    "why_good_fit": "3 specific reasons this role suits the candidate",
    "experience_required": "{exp_years} years",
    "remote_option": "Fully Remote" or "Hybrid" or "On-site",
    "industry": "Primary industry sector",
    "work_style": "Individual contributor" or "Team collaboration" or "Leadership" or "Client-facing"
  }}
]

**CRITICAL:** 
- Each job must be FUNDAMENTALLY DIFFERENT from others
- NO duplicates or similar positions
- Return ONLY the JSON array, no markdown
- Match scores should vary (70-95) based on actual fit
- Focus on realistic, achievable next steps in career
"""
        
        response = self.generate_text(prompt, temperature=0.3, max_tokens=3000)
        
        print(f"🎯 NVIDIA Job Recommendations Request:")
        print(f"   Target: {num_recommendations} diverse job recommendations")
        print(f"   Skills: {skills_str[:100]}...")
        print(f"   Experience Level: {exp_level} ({exp_years} years)")
        
        print(f"🎯 NVIDIA Job Recommendations Response:")
        print(f"   Raw Response Length: {len(response)} characters")
        print(f"   Raw Response Sample: {response[:300]}...")
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('```')[1]
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            
            recommendations = json.loads(cleaned)
            
            print(f"✅ Job Recommendations Parsed Successfully:")
            print(f"   Found {len(recommendations) if isinstance(recommendations, list) else 1} recommendations")
            
            # Ensure it's a list
            if isinstance(recommendations, dict):
                recommendations = [recommendations]
            
            # Validate each recommendation has required fields
            required_fields = ['title', 'company_type', 'salary_range', 'description', 'required_skills', 'match_score']
            valid_recommendations = []
            
            for rec in recommendations:
                # Ensure basic required fields exist
                if all(field in rec for field in required_fields):
                    # Ensure match_score is a number
                    if isinstance(rec.get('match_score'), (int, float)):
                        # Add default values for optional fields if missing
                        rec.setdefault('company', 'Tech Company')
                        rec.setdefault('location', 'Bangalore, India')
                        rec.setdefault('job_type', 'Full-time')
                        rec.setdefault('matched_skills', rec.get('required_skills', [])[:3])
                        rec.setdefault('missing_skills', [])
                        rec.setdefault('growth_potential', 'Strong growth opportunities')
                        rec.setdefault('why_good_fit', 'Good skill alignment with career goals')
                        rec.setdefault('experience_required', exp_years)
                        rec.setdefault('remote_option', 'Remote')
                        rec.setdefault('industry', 'Technology')
                        rec.setdefault('work_style', 'Individual contributor')
                        
                        valid_recommendations.append(rec)
            
            # Sort by match score descending, then randomize within similar scores for diversity
            valid_recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            print(f"✅ Valid Job Recommendations: {len(valid_recommendations)}")
            for i, rec in enumerate(valid_recommendations[:3]):  # Log first 3
                print(f"   {i+1}. {rec.get('title')} - {rec.get('match_score')}% match - {rec.get('company_type')}")
            
            if valid_recommendations:
                return valid_recommendations[:num_recommendations]
            else:
                raise ValueError("No valid recommendations found")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"❌ Failed to parse job recommendations JSON: {e}")
            print(f"❌ Raw response was: {response[:500]}...")
            # Fallback recommendations based on actual skills
            skill_list = skills_str.split(", ") if skills_str and isinstance(skills_str, str) else ["General Skills"]
            # Ensure all items in skill_list are strings
            skill_list = [str(s) for s in skill_list if s]
            
            # Create intelligent fallback based on skills
            job_titles = []
            if any(str(s).lower() in ['python', 'java', 'javascript', 'react', 'node'] for s in skill_list):
                job_titles = [
                    ("Full Stack Developer", "$80,000 - $120,000", ["Python", "React", "Node.js", "SQL", "Git"]),
                    ("Backend Engineer", "$85,000 - $125,000", ["Python", "Java", "SQL", "REST APIs", "Cloud"]),
                    ("Frontend Developer", "$75,000 - $110,000", ["React", "JavaScript", "CSS", "HTML", "TypeScript"]),
                    ("Software Engineer", "$90,000 - $130,000", ["Python", "Java", "Git", "Agile", "Testing"]),
                    ("DevOps Engineer", "$95,000 - $135,000", ["Docker", "Kubernetes", "CI/CD", "AWS", "Python"])
                ]
            elif any(str(s).lower() in ['machine learning', 'ml', 'data science', 'ai'] for s in skill_list):
                job_titles = [
                    ("Machine Learning Engineer", "$100,000 - $150,000", ["Python", "TensorFlow", "ML", "Data Science", "Statistics"]),
                    ("Data Scientist", "$90,000 - $140,000", ["Python", "Statistics", "SQL", "ML", "Data Analysis"]),
                    ("AI Engineer", "$105,000 - $160,000", ["Python", "Deep Learning", "NLP", "ML", "Research"]),
                    ("Data Engineer", "$95,000 - $145,000", ["Python", "SQL", "Big Data", "ETL", "Spark"]),
                    ("Research Scientist", "$110,000 - $170,000", ["Python", "ML", "Research", "Mathematics", "AI"])
                ]
            else:
                job_titles = [
                    ("Software Developer", "$70,000 - $100,000", skill_list[:5]),
                    ("Technical Analyst", "$65,000 - $95,000", skill_list[:5]),
                    ("Systems Engineer", "$75,000 - $105,000", skill_list[:5]),
                    ("Application Developer", "$70,000 - $100,000", skill_list[:5]),
                    ("Technical Consultant", "$80,000 - $110,000", skill_list[:5])
                ]
            
            return [
                {
                    "title": job[0],
                    "company_type": "Technology Company",
                    "salary_range": job[1],
                    "description": f"Exciting opportunity for a {job[0]} role working with modern technologies and innovative projects. Join a dynamic team focused on delivering high-quality solutions.",
                    "required_skills": job[2],
                    "match_score": 85 - (i * 3),
                    "growth_potential": "Strong career growth with opportunities to advance and learn new technologies",
                    "why_good_fit": f"Your skills align well with this {job[0]} position, offering both challenge and growth.",
                    "experience_required": exp_years,
                    "remote_option": True,
                    "industry": "Technology"
                } for i, job in enumerate(job_titles[:num_recommendations])
            ]
    
    def generate_learning_path(
        self, 
        current_skills: List[str], 
        target_role: str,
        timeline: str = "3 months"
    ) -> Dict:
        """
        Generate personalized learning path using NVIDIA's Qwen model.
        
        Args:
            current_skills: List of current skills
            target_role: Desired job role
            timeline: Learning timeline
            
        Returns:
            Structured learning path
        """
        skills_str = ", ".join(current_skills)
        
        prompt = f"""
Create a {timeline} learning path for someone with these skills: {skills_str}
Target Role: {target_role}

Provide a structured learning plan with:
1. skill_gaps: List of skills to develop
2. learning_phases: Array of phases (each with title, duration, topics, resources)
3. milestones: Key achievements to track progress
4. estimated_hours: Total time investment needed
5. priority_order: Which skills to learn first

Format as JSON with these exact keys.
"""
        
        response = self.generate_text(prompt, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback learning path
            missing_skills = ["Advanced Programming", "System Design", "Leadership"]
            return {
                "skill_gaps": missing_skills,
                "learning_phases": [
                    {
                        "title": "Foundation Phase",
                        "duration": "4 weeks",
                        "topics": missing_skills[:2],
                        "resources": ["Online courses", "Practice projects"]
                    }
                ],
                "milestones": ["Complete foundation", "Build project", "Get certified"],
                "estimated_hours": 120,
                "priority_order": missing_skills
            }
    
    def detect_target_role(self, resume_data: Dict) -> Dict:
        """
        Intelligently detect the most suitable job role/title for a candidate using NVIDIA NIM.
        
        This method analyzes the resume comprehensively to determine:
        - Primary target role (most suitable job title)
        - Alternative roles (other good fits)
        - Role level (entry/mid/senior)
        - Industry fit
        
        Args:
            resume_data: Parsed resume data with skills, experience, education
            
        Returns:
            Dictionary with detected role information:
            {
                "target_role": "Primary job title",
                "alternative_roles": ["Role 1", "Role 2", "Role 3"],
                "role_level": "entry|mid|senior",
                "industry": "Primary industry",
                "confidence": 0.0-1.0
            }
        """
        # Extract and normalize resume data
        skills = resume_data.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
        skills_str = ", ".join(skills[:30]) if skills else "General technical skills"
        
        experience = resume_data.get('experience', [])
        if isinstance(experience, list):
            experience_str = " | ".join([str(e)[:150] for e in experience[:5]])
        else:
            experience_str = str(experience)[:500] if experience else "Entry-level professional"
        
        education = resume_data.get('education', [])
        if isinstance(education, list):
            education_str = ", ".join([f"{edu.get('degree', '') if isinstance(edu, dict) else str(edu)}" for edu in education])
        else:
            education_str = str(education) if education else "Not specified"
        
        prompt = f"""
You are an expert career counselor and technical recruiter with deep knowledge of job markets across industries.

CANDIDATE PROFILE:
Skills: {skills_str}
Experience: {experience_str}
Education: {education_str}

TASK:
Analyze this candidate's profile and detect the MOST SUITABLE target job role for them.
Consider:
1. Primary technical skills and their market demand
2. Experience level and achievements
3. Educational background
4. Current industry trends and job market reality
5. Natural career progression

REQUIRED JSON OUTPUT (no markdown, no additional text):
{{
  "target_role": "Specific, accurate job title (e.g., 'Full Stack Developer', 'Data Scientist', 'DevOps Engineer')",
  "alternative_roles": ["Alternative role 1", "Alternative role 2", "Alternative role 3"],
  "role_level": "entry" or "mid" or "senior",
  "industry": "Primary industry sector",
  "confidence": 0.85,
  "reasoning": "2-3 sentence explanation of why this role fits best",
  "key_strengths": ["Strength 1", "Strength 2", "Strength 3"]
}}

GUIDELINES:
- Be specific and accurate with job titles (use industry-standard titles)
- Match role level to actual experience (0-2 years=entry, 3-7=mid, 8+=senior)
- Consider current market demand for the skills
- Target role should be realistic and achievable
- Confidence should reflect how well skills align with role

Return ONLY the JSON object.
"""
        
        print(f"🎯 NVIDIA Role Detection Request:")
        print(f"   Analyzing skills: {skills_str[:100]}...")
        print(f"   Experience data: {experience_str[:100]}...")
        
        response = self.generate_text(prompt, temperature=0.2, max_tokens=800)
        
        print(f"🎯 NVIDIA Role Detection Response:")
        print(f"   Raw Response: {response[:300]}...")
        
        try:
            # Clean response - remove markdown if present
            cleaned = response.strip()
            if cleaned.startswith('```'):
                # Extract content between code blocks
                parts = cleaned.split('```')
                if len(parts) >= 2:
                    cleaned = parts[1]
                    if cleaned.startswith('json'):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            
            # Validate required fields
            required_fields = ['target_role', 'alternative_roles', 'role_level', 'industry', 'confidence']
            if all(field in result for field in required_fields):
                print(f"✅ Role Detection Success:")
                print(f"   Target Role: {result['target_role']}")
                print(f"   Role Level: {result['role_level']}")
                print(f"   Industry: {result['industry']}")
                print(f"   Confidence: {result['confidence']}")
                print(f"   Alternative Roles: {', '.join(result['alternative_roles'][:2])}")
                return result
            else:
                raise ValueError("Missing required fields in response")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠️  Failed to parse role detection JSON: {e}")
            print(f"⚠️  Falling back to heuristic role detection")
            
            # Fallback: Intelligent heuristic-based role detection
            skills_lower = [str(s).lower() for s in skills]
            
            # Determine role based on skill patterns
            target_role = "Software Developer"
            industry = "Technology"
            alternative_roles = ["Software Engineer", "Application Developer", "Technical Analyst"]
            
            # Web Development
            if any(skill in skills_lower for skill in ['react', 'angular', 'vue', 'javascript', 'frontend', 'html', 'css']):
                if any(skill in skills_lower for skill in ['node', 'express', 'python', 'java', 'backend']):
                    target_role = "Full Stack Developer"
                    alternative_roles = ["Full Stack Engineer", "Web Developer", "Software Engineer"]
                else:
                    target_role = "Frontend Developer"
                    alternative_roles = ["UI Developer", "React Developer", "Web Developer"]
            
            # Backend/API Development
            elif any(skill in skills_lower for skill in ['django', 'flask', 'fastapi', 'spring', 'node', 'express', 'api']):
                target_role = "Backend Developer"
                alternative_roles = ["API Developer", "Backend Engineer", "Server-Side Developer"]
            
            # Data Science/ML
            elif any(skill in skills_lower for skill in ['machine learning', 'ml', 'data science', 'tensorflow', 'pytorch', 'nlp']):
                target_role = "Machine Learning Engineer"
                alternative_roles = ["Data Scientist", "AI Engineer", "ML Developer"]
                industry = "AI/ML"
            
            # Data Engineering
            elif any(skill in skills_lower for skill in ['spark', 'hadoop', 'etl', 'data pipeline', 'big data', 'kafka']):
                target_role = "Data Engineer"
                alternative_roles = ["Big Data Engineer", "ETL Developer", "Data Platform Engineer"]
                industry = "Data Engineering"
            
            # DevOps/Cloud
            elif any(skill in skills_lower for skill in ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'devops', 'ci/cd', 'terraform']):
                target_role = "DevOps Engineer"
                alternative_roles = ["Cloud Engineer", "Site Reliability Engineer", "Infrastructure Engineer"]
                industry = "Cloud/DevOps"
            
            # Mobile Development
            elif any(skill in skills_lower for skill in ['android', 'ios', 'swift', 'kotlin', 'react native', 'flutter']):
                target_role = "Mobile Developer"
                alternative_roles = ["Android Developer", "iOS Developer", "Mobile App Developer"]
                industry = "Mobile"
            
            # QA/Testing
            elif any(skill in skills_lower for skill in ['selenium', 'testing', 'qa', 'automation', 'cypress', 'jest']):
                target_role = "QA Engineer"
                alternative_roles = ["Test Automation Engineer", "SDET", "Quality Analyst"]
            
            # Determine experience level from experience text
            exp_text = str(experience_str).lower()
            if any(word in exp_text for word in ['senior', 'lead', '8+', '10+', 'principal', 'architect']):
                role_level = 'senior'
            elif any(word in exp_text for word in ['mid', '3-5', '5-7', 'intermediate', '4 years', '5 years']):
                role_level = 'mid'
            else:
                role_level = 'entry'
            
            return {
                "target_role": target_role,
                "alternative_roles": alternative_roles,
                "role_level": role_level,
                "industry": industry,
                "confidence": 0.75,
                "reasoning": f"Based on skill analysis, {target_role} is the most suitable role. Primary skills align well with this career path.",
                "key_strengths": skills[:3] if skills else ["Technical skills", "Problem solving", "Team collaboration"],
                "detection_method": "heuristic_fallback"
            }

    def generate_ats_score(
        self,
        resume_data: Dict,
        job_description: Optional[str] = None,
        job_requirements: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate ATS (Applicant Tracking System) score for a resume.
        
        Args:
            resume_data: Parsed resume data with skills, experience, etc.
            job_description: Full job description text (optional)
            job_requirements: List of specific job requirements (optional)
            
        Returns:
            ATS score analysis with recommendations
        """
        # Handle skills - can be list or string
        skills_raw = resume_data.get('skills', [])
        if isinstance(skills_raw, list):
            skills = ", ".join([str(s) for s in skills_raw])
        else:
            skills = str(skills_raw)
        
        experience = resume_data.get('experience_summary', '')
        if not experience:
            experience = resume_data.get('experience', '')
        if not experience:
            experience = "No experience provided"
        
        education_raw = resume_data.get('education', [])
        if isinstance(education_raw, list):
            education = ", ".join([f"{edu.get('degree', '') if isinstance(edu, dict) else str(edu)}" for edu in education_raw]) if education_raw else "Not specified"
        else:
            education = str(education_raw) if education_raw else "Not specified"
        
        # Build job section
        job_section = ""
        if job_description:
            job_section = f"\n\nJOB DESCRIPTION:\n{job_description}"
        if job_requirements:
            job_section += f"\n\nREQUIRED SKILLS:\n" + ", ".join(job_requirements)
        
        prompt = f"""
You are an ATS (Applicant Tracking System) expert. Analyze this resume and provide a comprehensive ATS score.

RESUME DATA:
Skills: {skills}
Experience: {experience}
Education: {education}
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

Be specific and actionable in your recommendations.
"""
        
        response = self.generate_text(prompt, temperature=0.2, max_tokens=2048)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback ATS score
            return {
                "overall_score": 75,
                "category_scores": {
                    "skills_match": 75,
                    "experience_match": 75,
                    "education_match": 75,
                    "formatting": 80
                },
                "keyword_matches": {
                    "matched_keywords": resume_data.get('skills', [])[:5],
                    "missing_keywords": [],
                    "match_percentage": 75
                },
                "strengths": ["Clear skill presentation", "Relevant experience"],
                "improvement_areas": ["Add more keywords", "Quantify achievements"],
                "ats_recommendations": [
                    "Include industry-specific keywords",
                    "Use standard section headings",
                    "Add measurable achievements"
                ],
                "pass_likelihood": "medium",
                "summary": "Resume shows good potential with room for optimization. Focus on keyword density and quantifiable achievements.",
                "raw_analysis": response
            }


def get_nvidia_client(api_key: Optional[str] = None, model: Optional[str] = None) -> Optional[NVIDIAClient]:
    """
    Factory function to create NVIDIA client.
    Returns None if API key is not available.
    """
    try:
        return NVIDIAClient(api_key=api_key, model=model)
    except ValueError:
        return None


# Example usage for testing
if __name__ == "__main__":
    # Test the client
    client = NVIDIAClient()
    
    # Test basic text generation
    response = client.generate_text("What are the key skills for a software engineer?")
    print("Basic generation test:")
    print(response)
    
    # Test resume analysis
    sample_resume = {
        "skills": ["Python", "React", "SQL"],
        "experience_summary": "2 years as junior developer",
        "education": [{"degree": "Bachelor", "field": "Computer Science"}]
    }
    
    analysis = client.generate_resume_analysis(sample_resume)
    print("\nResume analysis test:")
    print(json.dumps(analysis, indent=2))