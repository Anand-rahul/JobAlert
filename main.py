import time
from config import *
from notifier import send_discord_notification
from scraper import load_companies, get_seen_jobs, fetch_jobs, save_seen_job
from resume_parser import get_latest_resume, generate_ai_profile, evaluate_semantic_match

def is_local_keyword_match(job_text: str, keywords: list) -> bool:
    """Pre-filter: Checks if JD has at least ANY keywords before hitting Groq."""
    if not keywords:
        return True # If no context keywords, let it pass to AI by default
    text = job_text.lower()
    return any(kw.lower() in text for kw in keywords)

def main():
    companies = load_companies()
    if not companies:
        print("No companies loaded. Exiting.")
        return

    seen_jobs = get_seen_jobs()
    
    print("--- Constructing Candidate Intelligence ---")
    resume_path = get_latest_resume()
    profile_data = {"query": "Software Engineer II", "keywords": []}
    
    if resume_path:
        print(f"Parsing resume: {resume_path}")
        profile_data = generate_ai_profile(resume_path)
    else:
        print("No resume found. Using generic search.")

    base_query = profile_data.get("query", "Software Engineer II")
    keywords = profile_data.get("keywords", [])

    print("\n--- Scraping and Semantic Matching ---")
    
    for company in companies:
        dynamic_query = f"{base_query} {company}"
        jobs = fetch_jobs(dynamic_query, company)
        
        for job in jobs:
            job_id = job.get("job_id")
            if not job_id or job_id in seen_jobs:
                continue

            # Hybrid Stage 1: Fast Python Pre-filter
            job_text_bundle = f"{job['title']} {job['full_description']}"
            if not is_local_keyword_match(job_text_bundle, keywords):
                print(f"Skipping '{job['title']}': Failed Fast Local Keyword Match.")
                save_seen_job(job_id)
                seen_jobs.add(job_id)
                continue
            
            # Hybrid Stage 2: Deep LLM Semantic Evaluation
            if resume_path:
                print(f"Evaluating Semantic Fit via AI for: {job['title']}...")
                eval_payload = evaluate_semantic_match(resume_path, job['title'], job['full_description'])
                score = eval_payload.get("score", 0)
                job["match_score"] = score
                job["ai_reasoning"] = eval_payload.get("reasoning", "")
                
                if score < MATCH_THRESHOLD:
                    print(f"REJECTED '{job['title']}': Scored {score}% (Threshold: {MATCH_THRESHOLD}%)")
                    save_seen_job(job_id)
                    seen_jobs.add(job_id)
                    continue
                else:
                    print(f"ACCEPTED '{job['title']}': Scored {score}%!")
            else:
                job["match_score"] = 100
                job["ai_reasoning"] = "No context to verify. Passed implicitly."

            # Alert and Save
            send_discord_notification(job)
            save_seen_job(job_id)
            seen_jobs.add(job_id)
            
            # Stagger AI API calls to prevent rate limiting
            time.sleep(2)

if __name__ == "__main__":
    main()
