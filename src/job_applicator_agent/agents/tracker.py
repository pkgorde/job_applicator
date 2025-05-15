# src/agents/tracker.py
import dagger
from typing import List
import os
import pandas as pd
from datetime import datetime

from models.data_models import ApplicationResult

class TrackerAgent(dagger.Agent):
    def __init__(self):
        super().__init__()
        self.applications = []
        
        # Register capabilities
        self.register_capability(
            "record_application",
            "Record job application result",
            self.record_application
        )
        
        self.register_capability(
            "get_all_applications",
            "Get all recorded applications",
            self.get_all_applications
        )
        
    async def record_application(self, result: ApplicationResult):
        """Record a job application result"""
        self.applications.append(result)
        self.log(f"Recorded application for {result.job.title}: {'Success' if result.success else 'Failed'}")
        
        # Save to file regularly
        await self.save_applications()
        
    async def get_all_applications(self) -> List[ApplicationResult]:
        """Get all recorded applications"""
        return self.applications
        
    async def save_applications(self):
        """Save applications to file"""
        if not self.applications:
            return
            
        # Convert to dict for DataFrame
        apps_dict = []
        for app in self.applications:
            apps_dict.append({
                "url": app.job.url,
                "domain": app.job.domain,
                "title": app.job.title,
                "success": app.success,
                "timestamp": app.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "notes": app.notes
            })
            
        # Save as CSV
        df = pd.DataFrame(apps_dict)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"successful_applications_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        # Also save as text file
        with open(filename.replace('.csv', '.txt'), 'w') as f:
            for app in apps_dict:
                f.write(f"Title: {app['title']}\n")
                f.write(f"URL: {app['url']}\n")
                f.write(f"Domain: {app['domain']}\n")
                f.write(f"Success: {app['success']}\n")
                f.write(f"Timestamp: {app['timestamp']}\n")
                f.write(f"Notes: {app['notes']}\n")
                f.write("-" * 50 + "\n")
                
        self.log(f"Saved {len(self.applications)} application records to {filename}")