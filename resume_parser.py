import os
import glob
import json
import hashlib
from PyPDF2 import PdfReader
from groq import Groq
from config import CACHE_DIR, GROQ_API_KEY

def get_latest_resume() -> str | None:
    resumes = glob.glob("*resume*.pdf") + glob.glob("*.pdf")
    resumes = list(set(resumes))
    if not resumes:
        return None
    return max(resumes, key=os.path.getmtime)

def hash_file(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def extract_pdf_text(filepath: str) -> str:
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Failed to read PDF: {e}")
        return ""

def generate_ai_profile(pdf_path: str) -> dict:
    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY not found. Falling back to generic query.")
        return {"query": "Software Engineer II", "keywords": []}

    file_hash = hash_file(pdf_path)
    base_cache_path = os.path.join(CACHE_DIR, file_hash)
    os.makedirs(base_cache_path, exist_ok=True)
    
    json_path = os.path.join(base_cache_path, "profile.json")
    md_path = os.path.join(base_cache_path, "context.md")

    if os.path.exists(json_path) and os.path.exists(md_path):
        print(f"Loaded cached AI profile from {base_cache_path}")
        with open(json_path, 'r') as f:
            return json.load(f)

    print(f"Building context map from {pdf_path} utilizing Groq AI...")
    text = extract_pdf_text(pdf_path)[:8000]

    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are an expert technical recruiter analyzing a candidate's resume.
    Provide two things based on the resume:
    1. A short markdown text describing the candidate's core strengths, years of experience, and optimal roles.
    2. A structured JSON containing:
       - "query": The best 3-word base search query (e.g. "Backend Engineer Java").
       - "keywords": An array of 10 positive core technologies the candidate knows.
       
    Output exactly in this format separating the two with "---JSON_START---":
    <markdown summary>
    ---JSON_START---
    <json payload>
    
    Resume Text:
    {text}
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2,
        )
        
        response_text = completion.choices[0].message.content.strip()
        parts = response_text.split("---JSON_START---")
        
        markdown_ctx = parts[0].strip() if len(parts) > 1 else "Context un-parsable."
        json_str = parts[1].strip() if len(parts) > 1 else "{}"
        
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        profile_data = json.loads(json_str)
        
        with open(json_path, 'w') as f:
            json.dump(profile_data, f)
        with open(md_path, 'w') as f:
            f.write(markdown_ctx)
            
        print(f"Profile generated strictly! Search baseline is '{profile_data.get('query')}'")
        return profile_data

    except Exception as e:
        print(f"Groq Context Generation Failed: {e}")
        return {"query": "Software Engineer II", "keywords": []}


def evaluate_semantic_match(pdf_path: str, job_title: str, job_desc: str) -> dict:
    if not GROQ_API_KEY:
        return {"score": 100, "reasoning": "Groq Key missing, assumed 100%."}
        
    file_hash = hash_file(pdf_path)
    md_path = os.path.join(CACHE_DIR, file_hash, "context.md")
    
    context_text = "Standard Software Engineer"
    if os.path.exists(md_path):
        with open(md_path, 'r') as f:
            context_text = f.read()
            
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    Evaluate the fit between the Candidate Profile and the Job Description.
    Output ONLY a raw JSON object with no markdown block formatting, in exactly this schema:
    {{
      "score": <int between 0 and 100 representing percentage match>,
      "reasoning": "<string 1 sentence explaining why>"
    }}
    
    Candidate Context:
    {context_text}
    
    Job Title: {job_title}
    Job Description:
    {job_desc}
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON-only response bot. Provide only pure JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        return res
    except Exception as e:
        print(f"Match evaluation failed: {e}")
        return {"score": 0, "reasoning": "Error evaluating semantic match."}
