import json
import os
import requests
from typing import List, Dict, Any
from config import JOB_API_KEY, SEEN_JOBS_FILE

def load_companies(filepath: str = "companies.json") -> List[str]:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_seen_jobs(filepath: str = SEEN_JOBS_FILE) -> set:
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        return set()

def save_seen_job(job_id: str, filepath: str = SEEN_JOBS_FILE):
    with open(filepath, 'a') as f:
        f.write(f"{job_id}\n")

def fetch_jobs(query: str, company: str) -> List[Dict[str, Any]]:
    print(f"Fetching jobs for query: '{query}'")
    if not JOB_API_KEY:
        print("Error: JOB_API_KEY is not set.")
        return []

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_jobs",
            "q": query,
            "hl": "en",
            "location": "Bengaluru, Karnataka, India", 
            "api_key": JOB_API_KEY
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        jobs_results = data.get("jobs_results", [])
        parsed_jobs = []
        for job in jobs_results:
            job_id = job.get("job_id")
            if not job_id:
                continue

            apply_options = job.get("apply_options", [])
            url_link = apply_options[0].get("link", "#") if apply_options else job.get("share_link", "#")

            description = job.get("description", "")
            extensions = job.get("extensions", [])
            
            parsed_jobs.append({
                "job_id": job_id,
                "title": job.get("title", "Job Role"),
                "company_name": job.get("company_name", company),
                "location": job.get("location", "Unknown"),
                "url": url_link,
                "job_type": extensions[0] if extensions else "N/A",
                "via": job.get("via", "Direct"),
                "full_description": description,
                "snippet": description[:200] + "..." if len(description) > 200 else description
            })
        return parsed_jobs
    except Exception as e:
        print(f"Job fetch failed for {company}: {e}")
        return []
