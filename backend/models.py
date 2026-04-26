from sqlalchemy import Column, String, Float
from .database import Base

class IscoSkill(Base):
    __tablename__ = "isco_skills"
    
    level = Column(Float) # Or Integer, but SQLite might parse BIGINT into larger int/float
    isco_08_code = Column(String, primary_key=True, index=True) # Even if it's BIGINT in DB, pandas might have created it as such, but string is safer for codes
    title_en = Column(String)
    definition = Column(String)
    tasks_include = Column(String)
    included_occupations = Column(String)
    excluded_occupations = Column(String)
    notes = Column(String)
    cleaned_code = Column(String)
    parent_code = Column(String)
    hierarchy_level = Column(String)

class FreyOsborneLmic(Base):
    __tablename__ = "frey_osborne_lmic"
    
    soc_code = Column(String)
    isco_code = Column(String, primary_key=True, index=True)
    occupation = Column(String)
    fo_probability = Column(Float)
    task_routine = Column(Float)
    task_cognitive = Column(Float)
    task_manual = Column(Float)
    lmic_note = Column(String)
    risk_category = Column(String)
    region = Column(String, primary_key=True, index=True)
    lmic_calibration_factor = Column(Float)
    lmic_adjusted_probability = Column(Float)
    lmic_risk_category = Column(String)

class FreyOsborneIsco(Base):
    __tablename__ = "frey_osborne_isco"
    
    soc_code = Column(String)
    isco_code = Column(String, primary_key=True, index=True)
    occupation = Column(String)
    fo_probability = Column(Float)
    task_routine = Column(Float)
    task_cognitive = Column(Float)
    task_manual = Column(Float)
    lmic_note = Column(String)
    risk_category = Column(String)

class LmicAutomationCalibration(Base):
    __tablename__ = "lmic_automation_calibration_full"
    
    country = Column(String, primary_key=True)
    iso3 = Column(String)
    iso_num = Column(Float)
    region = Column(String)
    subregion = Column(String)
    fo_discount_factor = Column(Float)
    internet_penetration_pct = Column(Float)
    mobile_per_100 = Column(Float)
    informal_economy_pct = Column(Float)
    avg_wage_usd_month = Column(Float)
    tech_adoption_index = Column(Float)
    lmic_automation_note = Column(String)
    automation_arrival_index = Column(Float)

class LmicSectorAutomationRisk(Base):
    __tablename__ = "lmic_sector_automation_risk_full"
    
    country = Column(String, primary_key=True)
    iso3 = Column(String)
    region = Column(String)
    subregion = Column(String)
    sector = Column(String, primary_key=True)
    fo_base_score = Column(Float)
    lmic_calibrated_score = Column(Float)
    calibration_factor = Column(Float)
    risk_label_global = Column(String)
    risk_label_lmic = Column(String)
    task_routine = Column(Float)
    task_cognitive = Column(Float)
    task_manual = Column(Float)
    informal_economy_pct = Column(Float)
    internet_penetration_pct = Column(Float)
    avg_wage_usd_month = Column(Float)
    source = Column(String)

class WicAutomationCombined(Base):
    __tablename__ = "wic_automation_combined_full"
    
    country = Column(String, primary_key=True)
    iso3 = Column(String)
    iso_num = Column(Float)
    region = Column(String)
    subregion = Column(String)
    year = Column(Float, primary_key=True)
    pct_no_education = Column(Float)
    pct_primary = Column(Float)
    pct_secondary = Column(Float)
    pct_post_secondary = Column(Float)
    youth_pop_thousands = Column(Float)
    scenario = Column(String)
    age_group = Column(String)
    source = Column(String)
    pct_secondary_plus = Column(Float)
    skill_gap_index = Column(Float)
    exposed_youth_thousands = Column(Float)
    fo_discount_factor = Column(Float)
    informal_economy_pct = Column(Float)
    tech_adoption_index = Column(Float)
    automation_arrival_index = Column(Float)
    lmic_automation_note = Column(String)
    protected_youth_thousands = Column(Float)
    skill_automation_gap = Column(Float)

class WittgensteinEducationProjections(Base):
    __tablename__ = "wittgenstein_education_projections_full"
    
    country = Column(String, primary_key=True)
    iso3 = Column(String)
    iso_num = Column(Float)
    region = Column(String)
    subregion = Column(String)
    year = Column(Float, primary_key=True)
    pct_no_education = Column(Float)
    pct_primary = Column(Float)
    pct_secondary = Column(Float)
    pct_post_secondary = Column(Float)
    youth_pop_thousands = Column(Float)
    scenario = Column(String)
    age_group = Column(String)
    source = Column(String)
    pct_secondary_plus = Column(Float)
    skill_gap_index = Column(Float)
    exposed_youth_thousands = Column(Float)
