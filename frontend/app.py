import streamlit as st
import requests

# Define the backend URL
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="UNMAPPED", page_icon="🌍", layout="wide")

st.title("UNMAPPED: Skills Signal Engine")
st.markdown("Translating informal skills into recognized labor market signals.")

# Sidebar for Context Configuration (The "Country-Agnostic" Requirement)
st.sidebar.header("Configuration")
region = st.sidebar.selectbox(
    "Region", 
    ["Global (Default)", "Sub-Saharan Africa", "South Asia", "East Africa", "Southeast Asia", "Latin America", "MENA"]
)

# Main Input Form
st.subheader("Enter Informal Experience")
informal_experience = st.text_area(
    "Describe your skills, side-hustles, or daily work:",
    placeholder="e.g., I repair phones at the market, manage my own inventory, and speak English and Swahili.",
    height=150
)

if st.button("Analyze Skills & Assess Risk"):
    if informal_experience:
        with st.spinner("Mapping to standard taxonomies..."):
            
            # Prepare payload for API
            payload = {
                "description": informal_experience,
                "region": None if region == "Global (Default)" else region
            }
            
            # Call the FastAPI Backend
            try:
                response = requests.post(f"{API_URL}/analyze-skills", json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Display Results
                st.success(f"Analysis Complete! (Mapped using: {data.get('mapping_method', 'Unknown')})")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📋 Recognized Skills (ESCO/O*NET)")
                    for skill in data["standardized_skills"]:
                        st.markdown(f"- {skill}")
                        
                    st.markdown("### 💡 Recommended Adjacent Skills")
                    for skill in data["adjacent_skills_suggested"]:
                        st.markdown(f"- **{skill}**")
                        
                with col2:
                    st.markdown("### 🤖 Automation Risk (Frey-Osborne)")
                    risk_score = data["automation_risk_score"]
                    
                    # Visual risk indicator
                    st.metric(label="Displacement Risk", value=f"{risk_score}%")
                    st.progress(risk_score / 100)
                    if risk_score > 70:
                        st.error("High risk of automation in routine tasks.")
                    else:
                        st.info("Moderate/Low risk. Your skills are relatively durable.")
                        
                    if data.get("risk_analysis"):
                        st.markdown("### 🧠 AI Risk Analysis")
                        st.write(data["risk_analysis"])
                        
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend API. Please ensure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter your informal experience.")

st.markdown("---")