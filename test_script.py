import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.main import analyze_skills, InformalSkillInput
from backend.database import SessionLocal

db = SessionLocal()

payload = InformalSkillInput(
    description="I scan items at grocery store",
    region=None
)

result = analyze_skills(payload, db)
print("Standardized Skills:", result.standardized_skills)
print("Automation Risk Score:", result.automation_risk_score)
print("Adjacent Skills Suggested (Euclidean task distance):", result.adjacent_skills_suggested)
print("Mapping Method:", result.mapping_method)
