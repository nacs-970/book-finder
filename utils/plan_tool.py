"""
Reading planner helper
"""
import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class PlanTool:

    @staticmethod
    def avg_page_per_day(pages:int, days:int):
        day_avg = pages/days
        return {
            "per_day": day_avg,
            "per_month": day_avg * 30,
            "per_year": day_avg * 365
        }

    @classmethod
    def get_schemas(cls):
        """Return the function schemas for all tools in this class"""
        return [
                {
                    "type": "function",
                    "function": {
                        "name": "avg_page_per_day",
                        "description": "Calculate the average number of pages to read per day and extrapolate to months and years",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pages": {
                                    "type": "integer",
                                    "description": "Total number of pages in the book"
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days to complete the book"
                                }
                            },
                            "required": ["pages", "days"]
                        }
                    }
                }
        ]
    
    def register_all_tools(self, executor):
        """Register all tools in this class with the executor"""
        schemas = self.get_schemas()
        executor.register_tool("avg_page_per_day", self.avg_page_per_day, schemas[0])
