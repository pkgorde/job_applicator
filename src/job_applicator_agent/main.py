# src/job_applicator_agent/main.py
import os
import sys
import json

def main():
    """
    Main entry point for the Job Application Agent
    
    This script is designed to be run within a Dagger container and
    coordinates the job application process using multiple containerized
    agents.
    """
    print("Job Application Agent starting...")
    
    # Parse input arguments
    if len(sys.argv) > 1:
        # Load configuration from file if specified
        config_file = sys.argv[1]
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"Loaded configuration from {config_file}")
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            sys.exit(1)
    else:
        # Default configuration
        config = {
            "user_details": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "555-123-4567",
                "resume_path": "/app/data/resume.pdf"
            },
            "job_criteria": {
                "title": "Software Engineer",
                "location": "San Francisco",
                "experience": 1
            },
            "domains": [
                "greenhouse.io",
                "lever.co"
            ],
            "output_dir": "/app/output"
        }
    
    # Create output directory if it doesn't exist
    os.makedirs(config.get("output_dir", "/app/output"), exist_ok=True)
    
    # Execute the job application pipeline
    try:
        # 1. Execute job search agent
        print("Starting job search...")
        job_results = run_job_search(config)
        
        if not job_results:
            print("No job listings found. Exiting.")
            sys.exit(0)
            
        # 2. Process each job listing
        successful_applications = []
        for job in job_results:
            # Analyze form
            form_analysis = run_form_analysis(job, config)
            
            if not form_analysis:
                print(f"Could not analyze form for {job['url']}")
                continue
                
            # Fill application
            application_result = run_form_filler(job, form_analysis, config)
            
            if application_result.get("success", False):
                successful_applications.append(application_result)
                
        # 3. Track results
        track_applications(successful_applications, config)
        
        print(f"Job application process completed. {len(successful_applications)} successful applications.")
        
    except Exception as e:
        print(f"Error executing job application pipeline: {str(e)}")
        sys.exit(1)
        
# Helper functions to simulate the agent processes
def run_job_search(config):
    """Simulates the job search agent process"""
    print("Job Search Agent: Finding job listings...")
    
    # In a real implementation, this would search for jobs
    # For demo purposes, return some mock results
    return [
        {
            "url": "https://boards.greenhouse.io/example/jobs/4567890",
            "domain": "greenhouse.io",
            "title": config["job_criteria"]["title"]
        },
        {
            "url": "https://jobs.lever.co/example/job-12345",
            "domain": "lever.co",
            "title": config["job_criteria"]["title"]
        }
    ]
    
def run_form_analysis(job, config):
    """Simulates the form analysis agent process"""
    print(f"Form Analyzer Agent: Analyzing application form at {job['url']}...")
    
    # In a real implementation, this would analyze the form
    # For demo purposes, return mock form analysis
    return {
        "form_fields": [
            {"field_id": "name", "field_type": "text", "label": "Full Name", "required": True},
            {"field_id": "email", "field_type": "email", "label": "Email Address", "required": True},
            {"field_id": "phone", "field_type": "tel", "label": "Phone Number", "required": True}
        ],
        "resume_upload_id": "resume",
        "submit_button_id": "submit-application"
    }
    
def run_form_filler(job, form_analysis, config):
    """Simulates the form filler agent process"""
    print(f"Form Filler Agent: Filling application for {job['title']} at {job['url']}...")
    
    # In a real implementation, this would fill the form
    # For demo purposes, return a successful result
    return {
        "job": job,
        "success": True,
        "timestamp": "2025-05-14T12:34:56",
        "notes": "Application form filled (demo mode - not actually submitted)"
    }
    
def track_applications(applications, config):
    """Tracks and records successful applications"""
    print(f"Tracker Agent: Recording {len(applications)} applications...")
    
    # Save as JSON
    output_file = os.path.join(config.get("output_dir", "/app/output"), "successful_applications.json")
    with open(output_file, 'w') as f:
        json.dump(applications, f, indent=2)
        
    # Also save as text file
    text_file = os.path.join(config.get("output_dir", "/app/output"), "successful_applications.txt")
    with open(text_file, 'w') as f:
        for app in applications:
            f.write(f"Title: {app['job']['title']}\n")
            f.write(f"URL: {app['job']['url']}\n")
            f.write(f"Domain: {app['job']['domain']}\n")
            f.write(f"Success: {app['success']}\n")
            f.write(f"Timestamp: {app['timestamp']}\n")
            f.write(f"Notes: {app['notes']}\n")
            f.write("-" * 50 + "\n")
            
    print(f"Saved application records to {output_file} and {text_file}")

if __name__ == "__main__":
    main()