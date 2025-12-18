import time
from typing import Any
from .base_agent import SFNAgent
from sfn_blueprint.config.model_config import MODEL_CONFIG
from sfn_blueprint.utils.llm_handler import SFNAIHandler
from sfn_blueprint.utils.logging import setup_logger

class SFNValidateAndRetryAgent(SFNAgent):
    """
    Agent for validating agent responses with automatic retry functionality.
    
    This agent provides a validation framework for other agents by executing
    tasks, validating their responses using LLM models, and automatically
    retrying failed attempts. Ensures robust and reliable agent operations.
    
    Supported LLM providers: OpenAI, Anthropic, Cortex
    """
    
    def __init__(self, llm_provider: str, for_agent: str):
        """
        Initialize the Validation and Retry Agent.
        
        Args:
            llm_provider (str): Name of the LLM provider to use
                             (e.g., 'openai', 'anthropic', 'cortex')
            for_agent (str): Name of the agent to validate (must match
                           agent name in prompts_config.json)
                           
        Sets up the agent with validation configuration and LLM handler.
        """
        super().__init__(name="Validation Agent", role="Validator")
        # here for_agent name should be exact same, agent name specified in prompt_config.json file
        self.for_agent = for_agent
        self.logger, _ = setup_logger(f"SFNValidationAgent for -{for_agent}-")
        self.model_config = MODEL_CONFIG["validator"]
        self.llm_provider = llm_provider
        self.ai_handler = SFNAIHandler()

    def complete(self, agent_to_validate: Any, task: Any, validation_task: Any,
                             method_name: str, get_validation_params: str, max_retries: int = 3, retry_delay: float = 3.0):
        """
        Execute a task with validation and automatic retry logic.
        
        Orchestrates the complete validation workflow by executing the primary
        task, validating the response, and retrying failed attempts until success
        or maximum retries are reached.

        Args:
            agent_to_validate (Any): The agent object to execute and validate
            task (Any): The primary task to execute on the agent
            validation_task (Any): Task object containing validation context
            method_name (str): Name of the method to execute on agent_to_validate
            get_validation_params (str): Name of method to get validation parameters
            max_retries (int): Maximum number of retry attempts (default: 3)
            retry_delay (float): Delay between retries in seconds (default: 3.0)

        Returns:
            tuple: (response, message, success_flag) where:
                - response: Result from the agent execution
                - message: Validation message or error description
                - success_flag (bool): True if validation passed, False otherwise

        Note:
            If all retries fail, returns the last response with failure flag.
        """
        for attempt in range(max_retries):
            self.logger.info(f"Attempt {attempt + 1}: Executing {method_name}")
            
            # Execute the primary task
            method_to_call = getattr(agent_to_validate, method_name)
            response = method_to_call(task)
            self.logger.info(f'Executed primary task of agent:{agent_to_validate}')

            # Get validation parameters
            get_validation_method = getattr(agent_to_validate, get_validation_params)
            validation_prompts = get_validation_method(response, validation_task)
            self.logger.info(f'Received validation prompts:{validation_prompts}')

            # Validate the response
            is_valid, message = self.validate(validation_prompts)
            
            if is_valid:
                self.logger.info("Validation successful")
                return response, message, True
            
            self.logger.warning(f"Validation failed: {message}")
            if attempt == max_retries - 1:
                message = 'Validation failed:' + message
                return response, message, False
                
            time.sleep(retry_delay)

    def validate(self, validation_prompts: dict) -> tuple:
        """
        Validate agent responses using LLM-based validation prompts.
        
        Sends validation prompts to LLM to determine if the agent's response
        meets the required criteria and quality standards.

        Args:
            validation_prompts (dict): Dictionary containing:
                - system_prompt (str): System prompt for validation
                - user_prompt (str): User prompt with response to validate

        Returns:
            tuple: (is_valid, message) where:
                - is_valid (bool): True if validation passes, False otherwise
                - message (str): Validation explanation or error description

        Raises:
            Exception: If LLM API call fails during validation
        """
        configuration = {
            "messages": [
                {"role": "system", "content": validation_prompts["system_prompt"]},
                {"role": "user", "content": validation_prompts["user_prompt"]}
            ],
            "temperature": self.model_config[self.llm_provider]["temperature"],
            "max_tokens": self.model_config[self.llm_provider]["max_tokens"]
        }

        try:
            validation_result, _ = self.ai_handler.route_to(
                self.llm_provider,
                configuration,
                self.model_config[self.llm_provider]["model"]
            )
            
            return self._parse_validation_result(validation_result)
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False, str(e)

    def _parse_validation_result(self, result: str) -> tuple:
        """
        Parse LLM validation response into boolean and message.
        
        Extracts the validation decision and explanation from the LLM response.
        Expected format: "TRUE/FALSE\n[explanation]"

        Args:
            result (str): Raw validation response from LLM

        Returns:
            tuple: (is_valid, message) where:
                - is_valid (bool): True if first line is "TRUE", False otherwise
                - message (str): Remaining lines as explanation or error message

        Note:
            Handles parsing errors gracefully by returning False with error description.
        """
        try:
            parts = result.strip().split('\n', 1)
            is_valid = parts[0].upper() == "TRUE"
            message = parts[1] if len(parts) > 1 else ""
            return is_valid, message.strip()
        except Exception as e:
            return False, f"Error parsing validation result: {e}"
