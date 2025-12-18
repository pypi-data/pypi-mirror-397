from abc import ABC, abstractmethod
from typing import Any

class SFNAgent:
    '''
    Base Class that Provides a common interface and structure for all agent implementations
    '''
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def execute_task(self, task):
        raise NotImplementedError("Subclasses must implement execute_task method")