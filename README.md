# AI-Powered Semantic Job Matcher

A serverless, automated job alerting pipeline that tracks customized roles from Tier-1 companies natively. It uses a Two-Stage Hybrid AI Filtering Engine powered by Groq's high-speed Llama models to analyze your personal resume context and rigorously filter irrelevant roles, sending only perfect matches straight to your Discord Server.

## Key Features

- **Resume Context Integration**: Dynamically hashes and parses your local resume PDF, querying an LLM to map out an exact JSON profile consisting of your core role, positive strength tags, and negative red-flags.
- **Intelligent Local Caching**: Saves API tokens. It saves a readable context markdown and your target parameters under an ignored cache directory locally. If your resume file doesn't change, it leverages the instant cache. 
- **Two-Stage Hybrid Filtering Mechanism**:
  1. **Pre-flight Python Check**: Instantly filters incoming raw SerpApi roles against your generated keyword mapping natively.
  2. **Deep Semantic LLM Check**: Passes the job descriptions of promising roles back into LLM memory alongside your context mapping. Evaluates a literal Match Score (0-100%) before pushing to Discord.
- **Serverless GitHub Actions**: Fully ready-to-deploy GitHub Actions workflow to run silently on a schedule using cloud execution clusters.

## Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/Anand-rahul/JobAlert.git
cd JobAlert
```

2. **Install Requirements**  
Ensure you have Python 3.11+ installed.
```bash
pip install -r requirements.txt
```

3. **Configure the Environment**  
Create a `.env` file in the root directory and map the critical credentials:
```env
DISCORD_WEBHOOK_URL="your-discord-webhook"
JOB_API_KEY="your-serpapi-key"
GROQ_API_KEY="your-groq-key"
```

4. **Drop in your Resume**  
Place your resume anywhere in the root directory. Ensure it has "resume" in the filename, or ends with ".pdf".

## Local Execution

Simply execute the script via python:
```bash
python main.py
```
*Note: Depending on configuration, it may stagger Groq API calls 2 seconds per query to protect your rate limits. Your `seen_jobs.txt` file maps jobs it has evaluated so they never hit your terminal or discord twice.*

## Configuration Defaults

If you need to tighten or loosen the Discord alert threshold, you can modify `MATCH_THRESHOLD` inside `config.py` (Default: 40). Any score below this evaluated natively by Groq gets rejected natively to save Discord noise.

## Setting Up Cloud Automation (GitHub Actions)

This repository comes pre-packaged with a GitHub Actions YAML that can be scheduled to run permanently without a local machine.

1. Go to your GitHub repository -> Settings -> Secrets and variables -> Actions.
2. Save your API credentials as standard Repository Secrets:
   - `DISCORD_WEBHOOK_URL`
   - `JOB_API_KEY`
   - `GROQ_API_KEY`
3. Edit `.github/workflows/job_alerts.yml` and explicitly uncomment the schedule block depending on your cadence preference.
4. Push your changes.
