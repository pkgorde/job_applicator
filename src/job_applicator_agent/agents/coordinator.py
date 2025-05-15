# src/agents/coordinator.py
import dagger
from typing import List
from models.data_models import UserDetails, JobCriteria, JobListing, ApplicationResult

class CoordinatorAgent(dagger.Agent):
    def __init__(self):
        super().__init__()
        # Register capabilities
        self.register_capability(
            "coordinate_job_applications",
            "Orchestrate the entire job application process",
            self.coordinate_job_applications
        )
        
    async def coordinate_job_applications(self, 
                                         user_details: UserDetails, 
                                         job_criteria: JobCriteria, 
                                         domains: List[str]) -> List[ApplicationResult]:
        """Orchestrate the entire job application process"""
        
        # Step 1: Find job listings
        job_search_agent = await self.get_agent("job_search")
        jobs = await job_search_agent.find_jobs(job_criteria, domains)
        self.log(f"Found {len(jobs)} potential job listings")
        
        results = []
        
        # Step 2: Process each job
        for job in jobs:
            # Step 2a: Analyze the application form
            form_analyzer = await self.get_agent("form_analyzer")
            form_analysis = await form_analyzer.analyze_application_form(job.url)
            
            if not form_analysis:
                self.log(f"Could not analyze form for {job.url}")
                continue
                
            # Step 2b: Fill out the application
            form_filler = await self.get_agent("form_filler")
            application_result = await form_filler.fill_application(
                job, 
                user_details, 
                form_analysis
            )
            
            # Step 3: Track the result
            tracker = await self.get_agent("tracker")
            await tracker.record_application(application_result)
            
            results.append(application_result)
            
        # Step 4: Get final report of all applications
        final_results = await tracker.get_all_applications()
        
        return final_results