#!/usr/bin/env python
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from simple_researcher.crew import SimpleResearcherCrew

def run():
    inputs = {
        "topic": "AI"
    }
    result = SimpleResearcherCrew().crew().kickoff(inputs=inputs)
    print("got result: ", result.model_dump_json(), type(result))
    
