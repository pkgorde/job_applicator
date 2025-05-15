# src/agents/form_filler.py
import dagger
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

from models.data_models import JobListing, UserDetails, FormAnalysis, ApplicationResult

class FormFillerAgent(dagger.Agent):
    def __init__(self):
        super().__init__()
        self.driver = None
        
        # Register capabilities
        self.register_capability(
            "fill_application",
            "Fill out job applications",
            self.fill_application
        )
        
    def setup_browser(self):
        """Setup browser for form filling"""
        if self.driver is not None:
            return
            
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # For hackathon, you might want this visible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    async def fill_application(self, 
                              job: JobListing, 
                              user_details: UserDetails, 
                              form_analysis: FormAnalysis) -> ApplicationResult:
        """Fill out a job application"""
        self.setup_browser()
        
        try:
            self.log(f"Filling application for {job.title} at {job.url}")
            self.driver.get(job.url)
            time.sleep(3)  # Allow page to load
            
            # Fill form fields
            for field in form_analysis.form_fields:
                value = None
                field_id = field.field_id
                
                # Map form fields to user details
                if any(key in field.label.lower() for key in ["name", "full name"]):
                    value = user_details.name
                elif "email" in field.label.lower():
                    value = user_details.email
                elif any(key in field.label.lower() for key in ["phone", "telephone", "mobile"]):
                    value = user_details.phone
                
                if value:
                    try:
                        element = self.driver.find_element(By.ID, field_id)
                        element.send_keys(value)
                        self.log(f"Filled field: {field.label}")
                    except:
                        try:
                            element = self.driver.find_element(By.NAME, field_id)
                            element.send_keys(value)
                            self.log(f"Filled field: {field.label}")
                        except:
                            self.log(f"Could not find element {field_id}")
            
            # Upload resume if possible
            if form_analysis.resume_upload_id and user_details.resume_path:
                try:
                    upload_element = self.driver.find_element(By.ID, form_analysis.resume_upload_id)
                    upload_element.send_keys(os.path.abspath(user_details.resume_path))
                    self.log("Uploaded resume")
                except:
                    self.log("Could not upload resume")
            
            # For hackathon demo, we'll consider this a successful application
            # In a real implementation, you would click the submit button
            # if form_analysis.submit_button_id:
            #     try:
            #         submit_button = self.driver.find_element(By.ID, form_analysis.submit_button_id)
            #         submit_button.click()
            #         time.sleep(2)  # Wait for submission
            #         self.log("Submitted application")
            #     except:
            #         self.log("Could not click submit button")
            
            # Create successful result
            result = ApplicationResult(
                job=job,
                success=True,
                timestamp=datetime.now(),
                notes="Application form filled (demo mode - not actually submitted)"
            )
            
            return result
            
        except Exception as e:
            self.log(f"Error filling application {job.url}: {str(e)}")
            
            # Create failed result
            result = ApplicationResult(
                job=job,
                success=False,
                timestamp=datetime.now(),
                notes=f"Failed: {str(e)}"
            )
            
            return result
            
    async def shutdown(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()