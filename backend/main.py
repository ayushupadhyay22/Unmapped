from fastapi import FastAPI, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from .models import IscoSkill, FreyOsborneLmic, FreyOsborneIsco
import difflib
import os
import json
from dotenv import load_dotenv

load_dotenv()

# OpenAI imports
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False



app = FastAPI(
    title="UNMAPPED API",
    description="Infrastructure layer mapping informal skills to economic opportunity.",
    version="1.0.0"
)

# ---- Pydantic Models for Input/Output ----
class InformalSkillInput(BaseModel):
    description: str
    region: Optional[str] = None

class SkillProfileOutput(BaseModel):
    standardized_skills: list[str]
    automation_risk_score: float
    adjacent_skills_suggested: list[str]
    mapping_method: str
    risk_analysis: Optional[str] = None

# ---- Endpoints ----
@app.post("/api/v1/analyze-skills", response_model=SkillProfileOutput)
def analyze_skills(payload: InformalSkillInput, db: Session = Depends(get_db)):
    """
    Module 1 & 2 Combined:
    Takes an informal skill description and context, maps it to standard ISCO skills,
    and calculates the automation risk based on the provided country/context.
    """
    
    # Fetch all available ISCO skills from DB
    all_isco = db.query(IscoSkill).all()
    available_skill_names = [skill.title_en for skill in all_isco if skill.title_en]
    
    if not available_skill_names:
        raise HTTPException(status_code=500, detail="Database not seeded with ISCO skills.")
    
    standardized_skills = []
    mapping_method = "unknown"
    
    # 1. Map Informal -> Standard Skills (RAG-lite or Fallback)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if HAS_OPENAI and api_key:
        # LLM RAG-lite Approach
        client = OpenAI(api_key=api_key)
        prompt = f"""
        The user has the following informal work experience:
        '{payload.description}'
        
        Here is a list of valid official ISCO skills from our database:
        {available_skill_names}
        
        Select the top 1 to 3 most relevant ISCO skills from the list above that match the user's experience.
        Return ONLY a JSON array of strings exactly matching the skill names.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini-2025-08-07",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            content = content.replace("```json", "").replace("```", "").strip()
            standardized_skills = json.loads(content)
            # Validate that the returned skills are actually in our database
            standardized_skills = [s for s in standardized_skills if s in available_skill_names]
            mapping_method = "LLM (OpenAI)"
        except Exception as e:
            print(f"LLM matching failed: {e}")
            
    if not standardized_skills:
        # Fallback Approach: Fuzzy String Matching against words
        words = payload.description.split()
        for word in words:
            if len(word) > 3:
                matches = difflib.get_close_matches(word.title(), available_skill_names, n=1, cutoff=0.5)
                if matches and matches[0] not in standardized_skills:
                    standardized_skills.append(matches[0])
                    
        #if not standardized_skills:
        #     standardized_skills = ["Customer Service Representative"]
        mapping_method = "Fuzzy String Match (Fallback)"
        
    standardized_skills = standardized_skills[:3]
    
    # 2. Query SQLite to calculate Automation Risk and find Adjacent Skills
    total_risk = 0.0
    adjacent_skills_set = set()
    valid_risk_count = 0
    matched_task_profiles = []
    
    for skill in standardized_skills:
        # First find the ISCO code for this skill
        isco_skill = db.query(IscoSkill).filter(IscoSkill.title_en == skill).first()
        
        if not isco_skill:
            continue
            
        isco_code = isco_skill.isco_08_code
        
        # Try to find risk in LMIC table based on region
        risk_record = None
        if payload.region:
            risk_record = db.query(FreyOsborneLmic).filter(
                FreyOsborneLmic.isco_code == isco_code,
                FreyOsborneLmic.region == payload.region
            ).first()
            if not risk_record and isco_skill.parent_code:
                risk_record = db.query(FreyOsborneLmic).filter(
                    FreyOsborneLmic.isco_code.startswith(isco_skill.parent_code),
                    FreyOsborneLmic.region == payload.region
                ).first()
            if not risk_record and len(isco_code) >= 2:
                risk_record = db.query(FreyOsborneLmic).filter(
                    FreyOsborneLmic.isco_code.startswith(isco_code[:2]),
                    FreyOsborneLmic.region == payload.region
                ).first()
        
        if risk_record:
            risk_val = risk_record.lmic_adjusted_probability * 100 if risk_record.lmic_adjusted_probability else 0
            total_risk += risk_val
            valid_risk_count += 1
            matched_task_profiles.append({
                "routine": risk_record.task_routine or 0.0,
                "cognitive": risk_record.task_cognitive or 0.0,
                "manual": risk_record.task_manual or 0.0
            })
        else:
            # Fallback to the global ISCO table if not from a specific region
            global_risk = db.query(FreyOsborneIsco).filter(FreyOsborneIsco.isco_code == isco_code).first()
            if not global_risk and isco_skill.parent_code:
                global_risk = db.query(FreyOsborneIsco).filter(
                    FreyOsborneIsco.isco_code.startswith(isco_skill.parent_code)
                ).first()
            if not global_risk and len(isco_code) >= 2:
                global_risk = db.query(FreyOsborneIsco).filter(
                    FreyOsborneIsco.isco_code.startswith(isco_code[:2])
                ).first()
                
            if global_risk:
                risk_val = global_risk.fo_probability * 100 if global_risk.fo_probability else 0
                total_risk += risk_val
                valid_risk_count += 1
                matched_task_profiles.append({
                    "routine": global_risk.task_routine or 0.0,
                    "cognitive": global_risk.task_cognitive or 0.0,
                    "manual": global_risk.task_manual or 0.0
                })
                        
    avg_risk_score = (total_risk / valid_risk_count) if valid_risk_count > 0 else 50.0
    
    # Euclidean distance recommendation logic to find adjacent skills
    if avg_risk_score > 50.0 and matched_task_profiles:
        import math
        avg_routine = sum(p["routine"] for p in matched_task_profiles) / len(matched_task_profiles)
        avg_cognitive = sum(p["cognitive"] for p in matched_task_profiles) / len(matched_task_profiles)
        avg_manual = sum(p["manual"] for p in matched_task_profiles) / len(matched_task_profiles)
        
        candidates = []
        if payload.region:
            other_jobs = db.query(FreyOsborneLmic).filter(FreyOsborneLmic.region == payload.region).all()
            for job in other_jobs:
                job_risk = job.lmic_adjusted_probability * 100 if job.lmic_adjusted_probability else 0
                if job_risk < avg_risk_score - 10:
                    dist = math.sqrt(
                        (avg_routine - (job.task_routine or 0.0))**2 +
                        (avg_cognitive - (job.task_cognitive or 0.0))**2 +
                        (avg_manual - (job.task_manual or 0.0))**2
                    )
                    if job.occupation and job.occupation not in standardized_skills:
                        candidates.append((dist, job.occupation))
        else:
            other_jobs = db.query(FreyOsborneIsco).all()
            for job in other_jobs:
                job_risk = job.fo_probability * 100 if job.fo_probability else 0
                if job_risk < avg_risk_score - 10:
                    dist = math.sqrt(
                        (avg_routine - (job.task_routine or 0.0))**2 +
                        (avg_cognitive - (job.task_cognitive or 0.0))**2 +
                        (avg_manual - (job.task_manual or 0.0))**2
                    )
                    if job.occupation and job.occupation not in standardized_skills:
                        candidates.append((dist, job.occupation))
                        
        candidates.sort(key=lambda x: x[0])
        # Add top 4 adjacent skills with the smallest task distance
        for dist, occ in candidates[:4]:
            adjacent_skills_set.add(occ)
    
    # 3. LLM Risk Analysis
    risk_analysis = None
    if HAS_OPENAI and api_key and standardized_skills:
        try:
            client = OpenAI(api_key=api_key)
            risk_prompt = f"""
            The user has an informal work experience described as: '{payload.description}'.
            We mapped this to the following standard skills: {standardized_skills}.
            The calculated automation risk score for these skills in their region ({payload.region or 'Global'}) is {round(avg_risk_score, 2)} out of 100.
            
            Provide a brief (2-3 sentences) analysis of this risk profile, explaining what this risk score means for their job security and what adjacent skills they might consider developing to mitigate this risk.
            """
            
            response = client.chat.completions.create(
                model="gpt-5-mini-2025-08-07",
                messages=[{"role": "user", "content": risk_prompt}],
                max_completion_tokens=150
            )
            risk_analysis = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM risk analysis failed: {e}")
            
    return SkillProfileOutput(
        standardized_skills=standardized_skills,
        automation_risk_score=round(avg_risk_score, 2),
        adjacent_skills_suggested=list(adjacent_skills_set)[:4],
        mapping_method=mapping_method,
        risk_analysis=risk_analysis
    )

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}
