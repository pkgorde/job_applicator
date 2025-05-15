# src/main.py
import asyncio
import dagger
import streamlit as st
import os
import time
from datetime import datetime
import pandas as pd

from models.data_models import UserDetails, JobCriteria
from agents.coordinator import CoordinatorAgent
from agents.job_search import JobSearchAgent
from agents.form_analyzer import FormAnalyzerAgent
from agents.form_filler import FormFillerAgent
from agents.tracker import TrackerAgent

async def run_job_application_system(user_details, job_criteria, domains):
    # Create runtime
    runtime = dagger.Runtime()
    
    # Register all agents
    runtime.register_agent("coordinator", CoordinatorAgent())
    runtime.register_agent("job_search", JobSearchAgent())
    runtime.register_agent("form_analyzer", FormAnalyzerAgent())
    runtime.register_agent("form_filler", FormFillerAgent())
    runtime.register_agent("tracker", TrackerAgent())
    
    # Start the runtime
    await runtime.start()
    
    try:
        # Get coordinator
        coordinator = await runtime.get_agent("coordinator")
        
        # Run job application process
        results = await coordinator.coordinate_job_applications(
            user_details,
            job_criteria,
            domains
        )
        
        return results
        
    finally:
        # Shutdown runtime
        await runtime.shutdown()

def create_streamlit_ui():
    st.set_page_config(
        page_title="Multi-Agent Job Application System",
        page_icon="💼",
        layout="wide"
    )
    
    st.title("Automated Job Application Agent")
    st.write("Enter your details and job criteria to automate your job applications")
    
    with st.expander("👤 Personal Details", expanded=True):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        
        # Save uploaded resume temporarily
        resume_path = None
        if resume:
            resume_path = f"temp_resume_{int(time.time())}.pdf"
            with open(resume_path, "wb") as f:
                f.write(resume.getbuffer())
    
    with st.expander("🔍 Job Criteria", expanded=True):
        job_title = st.text_input("Job Title", placeholder="Software Engineer")
        location = st.text_input("Location", placeholder="San Francisco, CA")
        experience = st.number_input("Years of Experience", min_value=0, max_value=30, value=3)
        
        domains_default = "greenhouse.io, lever.co, workday.com"
        domains = st.text_area("Job Board Domains (comma-separated)", 
                               value=domains_default)
        domains_list = [d.strip() for d in domains.split(",") if d.strip()]
    
    if st.button("Start Job Search & Application", type="primary"):
        if not (name and email and phone and resume_path and job_title and location and domains_list):
            st.error("Please fill in all required fields")
        else:
            user_details = UserDetails(
                name=name,
                email=email,
                phone=phone,
                resume_path=resume_path,
                experience_years=experience
            )
            
            job_criteria = JobCriteria(
                title=job_title,
                location=location,
                experience=experience
            )
            
            with st.spinner("Multi-Agent system searching for jobs and applying..."):
                # Run the async function in the streamlit environment
                results = asyncio.run(run_job_application_system(
                    user_details, 
                    job_criteria, 
                    domains_list
                ))
                
                if results:
                    successful = [r for r in results if r.success]
                    st.success(f"Successfully processed {len(successful)} out of {len(results)} job applications!")
                    
                    # Display results
                    st.subheader("Application Results")
                    
                    for app in results:
                        status = "✅ Success" if app.success else "❌ Failed"
                        st.write(f"**{app.job.title}** - {app.job.domain} - {status}")
                        st.write(f"[Application Link]({app.job.url})")
                        st.write(f"Applied: {app.timestamp}")
                        if app.notes:
                            st.write(f"Notes: {app.notes}")
                        st.divider()
                        
                    # Provide download links
                    csv_file = f"job_applications_{int(time.time())}.csv"
                    
                    # Convert to dict for DataFrame
                    apps_dict = []
                    for app in results:
                        apps_dict.append({
                            "url": app.job.url,
                            "domain": app.job.domain,
                            "title": app.job.title,
                            "success": app.success,
                            "timestamp": app.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "notes": app.notes
                        })
                        
                    pd.DataFrame(apps_dict).to_csv(csv_file, index=False)
                    
                    with open(csv_file, "rb") as file:
                        st.download_button(
                            label="Download Results (CSV)",
                            data=file,
                            file_name=csv_file,
                            mime="text/csv"
                        )
                else:
                    st.warning("No applications processed. Try adjusting your search criteria.")
                    
            # Clean up temporary file
            if resume_path and os.path.exists(resume_path):
                os.remove(resume_path)

if __name__ == "__main__":
    create_streamlit_ui()