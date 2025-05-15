# src/agents/job_search.py
import dagger
from typing import List
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

from models.data_models import JobCriteria, JobListing

class JobSearchAgent(dagger.Agent):
    def __init__(self):
        super().__init__()
        self.driver = None
        # Register capabilities
        self.register_capability(
            "find_jobs",
            "Search for jobs based on criteria across specified domains",
            self.find_jobs
        )
        
    def setup_browser(self):
        """Setup headless browser for job search"""
        if self.driver is not None:
            return
            
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    async def find_jobs(self, criteria: JobCriteria, domains: List[str]) -> List[JobListing]:
        """Find jobs matching criteria across the provided domains"""
        self.setup_browser()
        all_jobs = []
        
        for domain in domains:
            try:
                self.log(f"Searching for jobs on {domain}")
                # Simple job search via Google
                search_query = f"site:{domain} {criteria.title} {criteria.location} {criteria.experience} apply"
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                
                self.driver.get(url)
                time.sleep(2)  # Allow page to load
                
                # Extract job listing URLs
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                search_results = soup.find_all("a")
                
                for result in search_results:
                    href = result.get("href")
                    if href and domain in href and "apply" in href.lower():
                        if href not in [job.url for job in all_jobs]:
                            job = JobListing(
                                url=href,
                                domain=domain,
                                title=criteria.title  # Default title match
                            )
                            
                            # Try to extract better title and description
                            try:
                                self.driver.get(href)
                                time.sleep(2)
                                job_page_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                                
                                # Find title (basic approach)
                                h1_tags = job_page_soup.find_all("h1")
                                if h1_tags:
                                    job.title = h1_tags[0].get_text().strip()
                                    
                                # Extract a short description
                                paragraphs = job_page_soup.find_all("p")
                                if paragraphs:
                                    job.description = paragraphs[0].get_text().strip()
                            except:
                                self.log(f"Could not extract detailed info for {href}")
                                
                            all_jobs.append(job)
                            
                            # Limit to 3 jobs per domain for the hackathon demo
                            if len([j for j in all_jobs if j.domain == domain]) >= 3:
                                break
                                
            except Exception as e:
                self.log(f"Error searching {domain}: {str(e)}")
                
        self.log(f"Found {len(all_jobs)} job listings")
        return all_jobs
        
    async def shutdown(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()