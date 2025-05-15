# src/agents/form_analyzer.py
import dagger
import google.generativeai as genai
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv

from models.data_models import FormAnalysis, FormField

class FormAnalyzerAgent(dagger.Agent):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.model = None
        
        # Register capabilities
        self.register_capability(
            "analyze_application_form",
            "Analyze job application forms using Gemini API",
            self.analyze_application_form
        )
        
    def setup_browser(self):
        """Setup headless browser for form analysis"""
        if self.driver is not None:
            return
            
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def setup_gemini(self):
        load_dotenv()
        """Setup Gemini API"""
        if self.model is not None:
            return
            
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Replace with your actual API key
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    async def analyze_application_form(self, url: str) -> FormAnalysis:
        """Analyze a job application form using Gemini API"""
        self.setup_browser()
        self.setup_gemini()
        
        try:
            self.log(f"Analyzing application form at {url}")
            self.driver.get(url)
            time.sleep(3)  # Allow page to load
            
            page_content = self.driver.page_source
            soup = BeautifulSoup(page_content, "html.parser")
            
            # Extract visible text content
            text_content = soup.get_text()
            
            # Also extract form elements
            form_elements = []
            for form in soup.find_all("form"):
                form_elements.append(str(form))
            
            # Ask Gemini to extract application form details
            prompt = f"""
            Analyze this job application page content and identify:
            1. Required form fields (name, email, phone, etc.)
            2. Where to upload resume
            3. Submit button identifier
            
            Page content excerpt: {text_content[:3000]}...
            
            Form elements found: {form_elements[:3000] if form_elements else "None found"}
            
            Return as JSON with this structure:
            {{
                "form_fields": [
                    {{
                        "field_id": "string", 
                        "field_type": "string", 
                        "label": "string", 
                        "required": boolean
                    }}
                ],
                "resume_upload_id": "string or null",
                "submit_button_id": "string or null"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                analysis_dict = json.loads(response.text)
                
                # Convert to our data model
                form_fields = []
                for field in analysis_dict.get("form_fields", []):
                    form_fields.append(FormField(
                        field_id=field["field_id"],
                        field_type=field["field_type"],
                        label=field["label"],
                        required=field.get("required", False)
                    ))
                
                form_analysis = FormAnalysis(
                    form_fields=form_fields,
                    resume_upload_id=analysis_dict.get("resume_upload_id"),
                    submit_button_id=analysis_dict.get("submit_button_id")
                )
                
                return form_analysis
                
            except Exception as e:
                self.log(f"Error parsing Gemini response: {str(e)}")
                return None
            
        except Exception as e:
            self.log(f"Error analyzing page {url}: {str(e)}")
            return None
            
    async def shutdown(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()