import pandas as pd
import numpy as np
import textblob
import sklearn
import nltk
import spacy
from sfn_blueprint.utils.logging import setup_logger

class CodeExecutor:
    """
    Tool for executing Python code in a controlled environment.
    
    This tool provides a secure sandbox for executing dynamically generated
    Python code on pandas DataFrames. It includes common data science libraries
    and ensures safe execution with proper error handling and logging.
    
    Available libraries in execution environment:
    - pandas (pd)
    - numpy (np) 
    - textblob
    - sklearn
    - nltk
    - spacy
    """
    
    def __init__(self):
        """
        Initialize the Code Executor tool.
        
        Sets up the tool with logging capabilities and prepares the execution
        environment with pre-imported data science libraries.
        """
        self.logger, _ = setup_logger(logger_name="CodeExecutor")

    def execute(self, task) -> pd.DataFrame:
        """
        Execute the provided Python code in a controlled environment.

        Executes Python code on a DataFrame with access to common data science
        libraries. The code is executed in a sandboxed environment with the
        input DataFrame available as 'df'.

        Args:
            task: Task object containing:
                - code (str): Python code to execute
                - data (pd.DataFrame): Input DataFrame to process

        Returns:
            pd.DataFrame: Modified DataFrame after code execution

        Raises:
            Exception: If code execution fails
            KeyError: If 'df' is not found in execution environment after execution

        Note:
            The code must modify the 'df' variable in-place or reassign it.
            Only the final state of 'df' is returned.
        """
        self.logger.info(f"Executing task with provided code: {task.code[:100]}...")  # Log first 100 characters of the code
        local_env = {
            'pd': pd,
            'np': np,
            'textblob': textblob,
            'sklearn': sklearn,
            'nltk': nltk,
            'spacy': spacy,
            'df': task.data
        }
        
        try:
            self.logger.info("Executing code...")
            exec(task.code, local_env)
            self.logger.info("Code execution successful")
        except Exception as e:
            self.logger.error(f"Error during code execution: {str(e)}")
            raise e  # Optionally re-raise the error after logging

        if 'df' in local_env:
            self.logger.info("Returning modified DataFrame")
            return local_env['df']
        else:
            self.logger.error("'df' key DataFrame not found in local environment after code execution")
            raise KeyError("'df' key DataFrame not  found in the local environment after code execution")