"""
Web Job Scraper Service - Fetches real job postings from public APIs and websites.

This service integrates with 12+ job search APIs to provide real-time job recommendations:

FREE APIs (No API Key Required):
- The Muse API - Diverse job listings
- RemoteOK API - Remote jobs worldwide
- Arbeitnow API - European remote jobs
- Remotive API - Remote jobs focus
- Jobicy API - Remote job board
- DevITjobs API - Tech jobs (UK focus)
- IndianAPI - Indian job market focus

APIs with Optional Keys (Free Tiers Available):
- Adzuna API - Global job search
- RapidAPI JSearch - Indeed, LinkedIn, Glassdoor aggregate
- Reed UK Jobs API - UK job market
- USAJobs API - US Government jobs

Prioritizes India-based jobs when requested for better local job matching.
"""

from __future__ import annotations

import os
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
import requests
from urllib.parse import quote_plus
from html import unescape


def clean_html(text: str, max_length: int = 500) -> str:
    """
    Remove HTML tags and clean up text for display.
    
    Args:
        text: Raw text that may contain HTML
        max_length: Maximum length of cleaned text
        
    Returns:
        Cleaned text without HTML tags
    """
    if not text:
        return ''
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Decode HTML entities
    text = unescape(text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text


class WebJobScraper:
    """
    Fetch real job postings from multiple sources with 12+ job APIs.
    
    Integrates with free and freemium job APIs to provide comprehensive job search.
    Prioritizes India-based jobs when requested and supports remote job filtering.
    """
    
    def __init__(self):
        # API keys from environment (with fallback for RapidAPI)
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID", "")
        self.adzuna_app_key = os.getenv("ADZUNA_APP_KEY", "")
        # RapidAPI key with fallback to ensure JSearch is always available
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY") or "c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b"
        self.reed_api_key = os.getenv("REED_API_KEY", "")
        self.usajobs_api_key = os.getenv("USAJOBS_API_KEY", "")
        self.usajobs_user_agent = os.getenv("USAJOBS_USER_AGENT", "PathFinderApp/1.0")
        
        # Base URLs
        self.adzuna_base = "https://api.adzuna.com/v1/api/jobs"
        self.muse_base = "https://www.themuse.com/api/public/jobs"
        self.remoteok_base = "https://remoteok.com/api"
        self.jsearch_base = "https://jsearch.p.rapidapi.com/search"
        self.reed_base = "https://www.reed.co.uk/api/1.0/search"
        self.usajobs_base = "https://data.usajobs.gov/api/search"
        self.arbeitnow_base = "https://www.arbeitnow.com/api/job-board-api"
        
        # NEW: Additional free job APIs (no keys required)
        self.remotive_base = "https://remotive.com/api/remote-jobs"
        self.jobicy_base = "https://jobicy.com/api/v2/remote-jobs"
        self.devitjobs_base = "https://www.devitjobs.uk/api/jobs"
        self.graphql_jobs_base = "https://api.graphql.jobs"
        self.freejobs_base = "https://freepublicapis.com/jobs-api"
        self.indianapi_base = "https://indianapi.in/api/jobs"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PathFinder Career Assistant/1.0'
        })
    
    def search_jobs(
        self,
        query: str,
        location: str = "remote",
        country: str = "us",
        max_results: int = 10,
        prioritize_india: bool = True,
    ) -> List[Dict]:
        """
        Search for jobs across multiple sources and aggregate results.
        
        Args:
            query: Job title or keywords (e.g., "Software Engineer", "Data Analyst")
            location: Location or "remote" for remote jobs
            country: Country code (us, uk, ca, in, etc.)
            max_results: Maximum number of results to return
            prioritize_india: If True, prioritize jobs from India
            
        Returns:
            List of job dictionaries with standardized fields (NO ATS scoring)
        """
        all_jobs = []
        
        # Try each source and aggregate - order by reliability
        # FREE APIs (no keys needed)
        sources = [
            ("The Muse", self._search_muse),
            ("RemoteOK", self._search_remoteok),
            ("Arbeitnow", self._search_arbeitnow),
            ("Remotive", self._search_remotive),
            ("Jobicy", self._search_jobicy),
        ]
        
        # Add India-focused API if prioritizing India
        if prioritize_india or country == 'in':
            sources.insert(0, ("IndianAPI", self._search_indianapi))
        
        # Add DevITjobs for tech jobs or UK location
        if country in ['uk', 'gb'] or 'developer' in query.lower() or 'engineer' in query.lower():
            sources.append(("DevITjobs", self._search_devitjobs))
        
        # Add APIs with keys if configured
        # Prioritize Adzuna for India if country is 'in'
        if self.adzuna_app_id and self.adzuna_app_key:
            sources.insert(0, ("Adzuna", self._search_adzuna))
        
        if self.rapidapi_key:
            sources.insert(0, ("JSearch (Indeed/LinkedIn/Glassdoor)", self._search_jsearch))
        
        # Reed UK only for UK jobs
        if self.reed_api_key and country in ['uk', 'gb']:
            sources.append(("Reed UK", self._search_reed))
        
        # USAJobs only for US jobs
        if self.usajobs_api_key and country == 'us':
            sources.append(("USAJobs", self._search_usajobs))
        
        for source_name, search_func in sources:
            try:
                jobs = search_func(query, location, country, max_results // len(sources) + 2)
                print(f"✅ Found {len(jobs)} jobs from {source_name}")
                all_jobs.extend(jobs)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"⚠️  Error fetching from {source_name}: {e}")
        
        # Deduplicate jobs
        all_jobs = self._deduplicate_jobs(all_jobs)
        
        # Prioritize India jobs if requested
        if prioritize_india:
            india_jobs = [j for j in all_jobs if self._is_india_job(j)]
            other_jobs = [j for j in all_jobs if not self._is_india_job(j)]
            
            print(f"🇮🇳 Found {len(india_jobs)} jobs from India")
            print(f"🌍 Found {len(other_jobs)} jobs from other locations")
            
            # Return India jobs first, then others
            all_jobs = india_jobs + other_jobs
        
        # Return top results (NO ATS SCORING - just raw job data)
        return all_jobs[:max_results]
    
    def _search_adzuna(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search Adzuna API."""
        if not self.adzuna_app_id or not self.adzuna_app_key:
            return []
        
        url = f"{self.adzuna_base}/{country}/search/1"
        params = {
            'app_id': self.adzuna_app_id,
            'app_key': self.adzuna_app_key,
            'what': query,
            'where': location,
            'results_per_page': min(max_results, 20),
            'content-type': 'application/json',
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        for result in data.get('results', []):
            # Clean and format description
            raw_desc = result.get('description', '')
            description = clean_html(raw_desc, max_length=300)
            
            jobs.append({
                'title': result.get('title', 'Unknown'),
                'company': result.get('company', {}).get('display_name', 'Unknown Company'),
                'location': result.get('location', {}).get('display_name', location),
                'description': description,
                'url': result.get('redirect_url', ''),
                'salary': result.get('salary_max', 0) or result.get('salary_min', 0),
                'salary_max': result.get('salary_max', 0),
                'salary_min': result.get('salary_min', 0),
                'posted_date': result.get('created', ''),
                'source': 'Adzuna',
                'job_type': 'Full-time',
            })
        
        return jobs
    
    def _search_muse(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search The Muse API."""
        try:
            # The Muse public API - no key required, but don't send api_key param
            params = {
                'page': 1,
                'descending': 'true',
            }
            
            # Add level filter to get more results
            if 'senior' in query.lower():
                params['level'] = 'Senior Level'
            elif 'entry' in query.lower() or 'junior' in query.lower():
                params['level'] = 'Entry Level'
            else:
                params['level'] = 'Mid Level'
            
            if location.lower() == 'remote':
                params['location'] = 'Flexible / Remote'
            
            response = self.session.get(self.muse_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('results', [])[:max_results]:
                company = result.get('company', {})
                locations = result.get('locations', [])
                location_str = locations[0].get('name', 'Remote') if locations else 'Remote'
                
                # Clean description
                raw_desc = result.get('contents', '')
                description = clean_html(raw_desc, max_length=300) if raw_desc else 'No description available'
                
                jobs.append({
                    'title': result.get('name', 'Unknown'),
                    'company': company.get('name', 'Unknown Company'),
                    'location': location_str,
                    'description': description,
                    'url': result.get('refs', {}).get('landing_page', ''),
                    'salary': 0,
                    'posted_date': result.get('publication_date', ''),
                    'source': 'The Muse',
                    'job_type': result.get('type', 'Full-time'),
                })
            
            return jobs
        except Exception as e:
            print(f"The Muse API error: {e}")
            return []
    
    def _search_remoteok(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search RemoteOK API."""
        try:
            response = self.session.get(self.remoteok_base, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Filter jobs by query
            query_lower = query.lower()
            filtered_jobs = []
            
            for result in data[1:]:  # Skip first element (metadata)
                if not isinstance(result, dict):
                    continue
                
                title = result.get('position', '').lower()
                tags = ' '.join(result.get('tags', [])).lower()
                
                # Simple relevance check
                if query_lower in title or any(word in title for word in query_lower.split()):
                    company = result.get('company', 'Unknown Company')
                    
                    # Clean description
                    raw_desc = result.get('description', '')
                    description = clean_html(raw_desc, max_length=300)
                    
                    filtered_jobs.append({
                        'title': result.get('position', 'Unknown'),
                        'company': company,
                        'location': 'Remote',
                        'description': description,
                        'url': result.get('url', f"https://remoteok.com/remote-jobs/{result.get('id', '')}"),
                        'salary': result.get('salary_max', 0) or 0,
                        'salary_max': result.get('salary_max', 0),
                        'salary_min': result.get('salary_min', 0),
                        'posted_date': result.get('date', ''),
                        'source': 'RemoteOK',
                        'job_type': 'Remote',
                    })
                
                if len(filtered_jobs) >= max_results:
                    break
            
            return filtered_jobs
        
        except Exception as e:
            print(f"RemoteOK API error: {e}")
            return []
    
    def _search_jsearch(self, query: str, location: str, country: str, max_results: int) -> List[Dict]:
        """
        Search JSearch API (RapidAPI) - aggregates Indeed, LinkedIn, Glassdoor.
        Uses http.client for reliable connection handling.
        """
        if not self.rapidapi_key:
            print("⚠️ JSearch API key not found")
            return []
        
        try:
            import http.client
            import json
            import urllib.parse
            
            # Build search query
            search_query = query
            if location and location.lower() not in ["", "any", "anywhere", "remote"]:
                search_query = f"{query} in {location}"
            
            # URL encode the query
            encoded_query = urllib.parse.quote(search_query)
            
            # Build endpoint with parameters
            endpoint = f"/search?query={encoded_query}&page=1&num_pages=1"
            
            # Add country filter if specified
            if country == "in" or (location and "india" in location.lower()):
                endpoint += "&country=in"
            elif country == "us":
                endpoint += "&country=us"
            
            # Add remote filter
            if location and location.lower() == "remote":
                endpoint += "&remote_jobs_only=true"
            
            # Add date filter for recent jobs
            endpoint += "&date_posted=month"
            
            print(f"🔍 Searching JSearch for: {search_query}")
            
            # Create HTTPS connection
            conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
            
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': "jsearch.p.rapidapi.com"
            }
            
            # Make request
            conn.request("GET", endpoint, headers=headers)
            
            res = conn.getresponse()
            data = res.read()
            
            if res.status != 200:
                print(f"⚠️ JSearch API error: Status {res.status}")
                print(f"Response: {data.decode('utf-8')[:200]}")
                conn.close()
                return []
            
            result = json.loads(data.decode("utf-8"))
            jobs_data = result.get('data', [])
            
            if not jobs_data:
                print("⚠️ No jobs found from JSearch")
                conn.close()
                return []
            
            print(f"✅ JSearch returned {len(jobs_data)} jobs")
            
            jobs = []
            for job in jobs_data[:max_results]:
                # Extract job details
                title = job.get('job_title', 'Unknown')
                company = job.get('employer_name', 'Unknown Company')
                
                # Format location
                job_city = job.get('job_city', '')
                job_state = job.get('job_state', '')
                job_country = job.get('job_country', '')
                
                if job_city and job_state:
                    location_str = f"{job_city}, {job_state}"
                elif job_city:
                    location_str = job_city
                elif job_state:
                    location_str = job_state
                elif job_country:
                    location_str = job_country
                else:
                    location_str = 'Remote' if job.get('job_is_remote', False) else 'Not Specified'
                
                # Get description
                raw_desc = job.get('job_description', '')
                description = clean_html(raw_desc, max_length=500)
                
                # Get salary
                salary_min = job.get('job_min_salary', 0) or 0
                salary_max = job.get('job_max_salary', 0) or 0
                salary_avg = (salary_min + salary_max) / 2 if (salary_min and salary_max) else (salary_min or salary_max)
                
                # Get job highlights
                highlights = job.get('job_highlights', {})
                qualifications = highlights.get('Qualifications', []) if highlights else []
                responsibilities = highlights.get('Responsibilities', []) if highlights else []
                benefits = highlights.get('Benefits', []) if highlights else []
                
                # Enhance description with highlights
                enhanced_desc = description
                if qualifications:
                    enhanced_desc += f"\n\nQualifications: {', '.join(qualifications[:3])}"
                if responsibilities:
                    enhanced_desc += f"\n\nResponsibilities: {', '.join(responsibilities[:3])}"
                
                # Get apply URL
                apply_url = job.get('job_apply_link') or job.get('job_google_link', '')
                
                # Get posted date
                posted_date = job.get('job_posted_at_datetime_utc', '')
                if posted_date:
                    posted_date = posted_date[:10]  # Get YYYY-MM-DD
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location_str,
                    'description': enhanced_desc or f"{title} position at {company}",
                    'url': apply_url,
                    'salary': int(salary_avg),
                    'salary_max': int(salary_max),
                    'salary_min': int(salary_min),
                    'posted_date': posted_date,
                    'source': 'JSearch (Indeed/LinkedIn/Glassdoor)',
                    'job_type': job.get('job_employment_type', 'Full-time'),
                    'is_remote': job.get('job_is_remote', False),
                    'company_logo': job.get('employer_logo', ''),
                    'qualifications': qualifications[:5] if qualifications else [],
                    'responsibilities': responsibilities[:5] if responsibilities else [],
                    'benefits': benefits[:3] if benefits else [],
                })
            
            conn.close()
            return jobs
            
        except Exception as e:
            print(f"⚠️ JSearch API error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _search_reed(self, query: str, location: str, country: str, max_results: int) -> List[Dict]:
        """Search Reed UK Jobs API."""
        if not self.reed_api_key:
            return []
        
        headers = {
            "Authorization": f"Basic {self.reed_api_key}"
        }
        
        params = {
            "keywords": query,
            "resultsToTake": min(max_results, 20)
        }
        
        if location.lower() != "remote":
            params["locationName"] = location
        
        try:
            response = self.session.get(self.reed_base, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('results', []):
                # Clean description
                raw_desc = result.get('jobDescription', '')
                description = clean_html(raw_desc, max_length=300)
                
                jobs.append({
                    'title': result.get('jobTitle', 'Unknown'),
                    'company': result.get('employerName', 'Unknown Company'),
                    'location': result.get('locationName', 'Remote'),
                    'description': description,
                    'url': result.get('jobUrl', ''),
                    'salary': result.get('maximumSalary', 0) or result.get('minimumSalary', 0) or 0,
                    'salary_max': result.get('maximumSalary', 0),
                    'salary_min': result.get('minimumSalary', 0),
                    'posted_date': result.get('date', ''),
                    'source': 'Reed UK',
                    'job_type': result.get('jobType', 'Full-time'),
                })
            return jobs
        except Exception as e:
            print(f"Reed API error: {e}")
            return []
    
    def _search_usajobs(self, query: str, location: str, country: str, max_results: int) -> List[Dict]:
        """Search USAJobs API (US Government jobs)."""
        if not self.usajobs_api_key:
            return []
        
        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": self.usajobs_user_agent,
            "Authorization-Key": self.usajobs_api_key
        }
        
        params = {
            "Keyword": query,
            "ResultsPerPage": min(max_results, 25)
        }
        
        if location.lower() != "remote":
            params["LocationName"] = location
        
        try:
            response = self.session.get(self.usajobs_base, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('SearchResult', {}).get('SearchResultItems', []):
                job_data = result.get('MatchedObjectDescriptor', {})
                
                # Clean description
                raw_desc = job_data.get('QualificationSummary', '')
                description = clean_html(raw_desc, max_length=300)
                
                jobs.append({
                    'title': job_data.get('PositionTitle', 'Unknown'),
                    'company': job_data.get('OrganizationName', 'US Government'),
                    'location': job_data.get('PositionLocationDisplay', 'Washington DC'),
                    'description': description,
                    'url': job_data.get('PositionURI', ''),
                    'salary': 0,
                    'posted_date': job_data.get('PublicationStartDate', ''),
                    'source': 'USAJobs',
                    'job_type': 'Full-time',
                })
            return jobs
        except Exception as e:
            print(f"USAJobs API error: {e}")
            return []
    
    def _search_arbeitnow(self, query: str, location: str, country: str, max_results: int) -> List[Dict]:
        """Search Arbeitnow API (European remote jobs)."""
        try:
            response = self.session.get(self.arbeitnow_base, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            query_lower = query.lower()
            filtered_jobs = []
            
            for result in data.get('data', []):
                title = result.get('title', '').lower()
                tags = ' '.join(result.get('tags', [])).lower()
                
                if query_lower in title or any(word in title or word in tags for word in query_lower.split()):
                    # Clean description
                    raw_desc = result.get('description', '')
                    description = clean_html(raw_desc, max_length=300)
                    
                    filtered_jobs.append({
                        'title': result.get('title', 'Unknown'),
                        'company': result.get('company_name', 'Unknown Company'),
                        'location': result.get('location', 'Remote'),
                        'description': description,
                        'url': result.get('url', ''),
                        'salary': 0,
                        'posted_date': result.get('created_at', ''),
                        'source': 'Arbeitnow',
                        'job_type': 'Remote',
                    })
                
                if len(filtered_jobs) >= max_results:
                    break
            
            return filtered_jobs
        except Exception as e:
            print(f"Arbeitnow API error: {e}")
            return []
    
    def _search_remotive(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search Remotive Remote Jobs API."""
        try:
            url = self.remotive_base
            params = {
                'search': query,
                'limit': min(max_results, 50),
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('jobs', [])[:max_results]:
                description = clean_html(result.get('description', ''), max_length=300)
                
                jobs.append({
                    'title': result.get('title', 'Unknown'),
                    'company': result.get('company_name', 'Unknown Company'),
                    'location': result.get('candidate_required_location', 'Remote'),
                    'description': description,
                    'url': result.get('url', ''),
                    'salary': result.get('salary', 0),
                    'posted_date': result.get('publication_date', ''),
                    'source': 'Remotive',
                    'job_type': result.get('job_type', 'Remote'),
                    'tags': result.get('tags', []),
                })
            
            return jobs
        except Exception as e:
            print(f"Remotive API error: {e}")
            return []
    
    def _search_jobicy(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search Jobicy Remote Jobs API."""
        try:
            url = self.jobicy_base
            params = {
                'search': query,
                'count': min(max_results, 50),
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('jobs', [])[:max_results]:
                description = clean_html(result.get('jobDescription', ''), max_length=300)
                
                jobs.append({
                    'title': result.get('jobTitle', 'Unknown'),
                    'company': result.get('companyName', 'Unknown Company'),
                    'location': result.get('jobGeo', 'Remote'),
                    'description': description,
                    'url': result.get('url', ''),
                    'salary': 0,
                    'posted_date': result.get('pubDate', ''),
                    'source': 'Jobicy',
                    'job_type': result.get('jobType', 'Remote'),
                })
            
            return jobs
        except Exception as e:
            print(f"Jobicy API error: {e}")
            return []
    
    def _search_devitjobs(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search DevITjobs UK API for tech jobs."""
        try:
            url = f"{self.devitjobs_base}/search"
            params = {
                'q': query,
                'limit': min(max_results, 50),
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for result in data.get('data', [])[:max_results]:
                description = clean_html(result.get('description', ''), max_length=300)
                
                jobs.append({
                    'title': result.get('title', 'Unknown'),
                    'company': result.get('company', 'Unknown Company'),
                    'location': result.get('location', 'UK'),
                    'description': description,
                    'url': result.get('url', ''),
                    'salary': result.get('salary', 0),
                    'posted_date': result.get('posted_at', ''),
                    'source': 'DevITjobs',
                    'job_type': result.get('type', 'Full-time'),
                })
            
            return jobs
        except Exception as e:
            print(f"DevITjobs API error: {e}")
            return []
    
    def _search_indianapi(
        self,
        query: str,
        location: str,
        country: str,
        max_results: int,
    ) -> List[Dict]:
        """Search IndianAPI for jobs (India-focused)."""
        try:
            url = self.indianapi_base
            params = {
                'keyword': query,
                'location': location if location != 'remote' else 'India',
                'limit': min(max_results, 50),
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            job_list = data.get('data', []) if isinstance(data, dict) else data
            
            for result in job_list[:max_results]:
                description = clean_html(result.get('description', ''), max_length=300)
                
                jobs.append({
                    'title': result.get('title', 'Unknown'),
                    'company': result.get('company', 'Unknown Company'),
                    'location': result.get('location', 'India'),
                    'description': description,
                    'url': result.get('url', '') or result.get('apply_link', ''),
                    'salary': result.get('salary', 0),
                    'posted_date': result.get('posted_date', ''),
                    'source': 'IndianAPI',
                    'job_type': result.get('job_type', 'Full-time'),
                })
            
            return jobs
        except Exception as e:
            print(f"IndianAPI error: {e}")
            return []
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company."""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _is_india_job(self, job: Dict) -> bool:
        """Check if a job is based in India."""
        location = job.get('location', '').lower()
        india_keywords = ['india', 'bangalore', 'bengaluru', 'mumbai', 'delhi', 'hyderabad', 
                          'pune', 'chennai', 'kolkata', 'ahmedabad', 'noida', 'gurugram', 
                          'gurgaon', 'chandigarh', 'jaipur', 'kochi', 'indore', 'in']
        
        return any(keyword in location for keyword in india_keywords)
    
    def get_job_details(self, job_url: str) -> Optional[Dict]:
        """Fetch detailed job information from URL."""
        # This would require web scraping which is more complex
        # For now, return None
        return None


def get_web_job_scraper() -> WebJobScraper:
    """Get singleton instance of WebJobScraper."""
    if not hasattr(get_web_job_scraper, '_instance'):
        get_web_job_scraper._instance = WebJobScraper()
    return get_web_job_scraper._instance


# CLI testing
if __name__ == "__main__":
    scraper = WebJobScraper()
    jobs = scraper.search_jobs("Software Engineer", location="remote", max_results=10)
    
    print(f"\n🔍 Found {len(jobs)} jobs:\n")
    for idx, job in enumerate(jobs, 1):
        print(f"{idx}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Source: {job['source']}")
        print(f"   URL: {job['url']}")
        print()
