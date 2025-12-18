"""
Task module for SFN Blueprint framework.

Provides a standardized data structure for passing work items between agents.
"""

from typing import Any, Optional


class Task:
    """
    Standardized task object for SFN Blueprint framework.
    
    Represents a unit of work to be processed by agents, containing
    description, data, and metadata for task execution.
    
    Args:
        description: Human-readable description of the task
        data: Task data (DataFrame, dict, file content, etc.)
        path: Optional file path associated with the task
        task_type: Type of task (e.g., 'feature_suggestion', 'data_quality')
        category: Domain category of the data/task
        analysis: Analysis results or metadata
        code: Generated or executable code
    """
    
    def __init__(
        self, 
        description: str, 
        data: Optional[Any] = None, 
        path: Optional[str] = None, 
        task_type: Optional[str] = None, 
        category: Optional[str] = None, 
        analysis: Optional[Any] = None, 
        code: Optional[str] = None
    ):
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")
            
        self.description = description
        self.data = data
        self.path = path
        self.task_type = task_type
        self.category = category
        self.analysis = analysis
        self.code = code
    
    def __str__(self) -> str:
        """String representation of task."""
        return f"Task(description='{self.description}', type='{self.task_type}', category='{self.category}')"