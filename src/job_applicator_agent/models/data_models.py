# src/models/data_models.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class UserDetails:
    name: str
    email: str
    phone: str
    resume_path: str
    skills: List[str] = None
    experience_years: int = 0
    
@dataclass
class JobCriteria:
    title: str
    location: str
    experience: int
    keywords: List[str] = None
    
@dataclass
class JobListing:
    url: str
    domain: str
    title: str
    description: str = ""
    
@dataclass
class FormField:
    field_id: str
    field_type: str
    label: str
    required: bool = False
    
@dataclass
class FormAnalysis:
    form_fields: List[FormField]
    resume_upload_id: Optional[str] = None
    submit_button_id: Optional[str] = None
    
@dataclass
class ApplicationResult:
    job: JobListing
    success: bool
    timestamp: datetime
    notes: str = ""