from abc import ABC, abstractmethod

class Algorithm(ABC):
    def __init__(self, project):
        self.project = project

    @abstractmethod
    def calculate(self):
        """Implement the calculation for the algorithm."""
        pass
