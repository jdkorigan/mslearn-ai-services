"""
Azure Text Analytics Language Detection Client

This script uses the Azure Text Analytics SDK to detect the language of input text.
It requires Azure Cognitive Services credentials stored in a .env file.

Environment Variables:
    AI_SERVICE_ENDPOINT: The endpoint URL for the Azure Text Analytics service
    AI_SERVICE_KEY: The API key for authentication

Example:
    $ python sdk-client.py
    Enter some text ("quit" to stop)
    Hello
    Language: English
"""

from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import AzureError
import sys
from typing import Optional, Tuple
from dataclasses import dataclass

class ConfigurationError(Exception):
    """Raised when there's an issue with the configuration."""
    pass

class InputError(Exception):
    """Raised when there's an issue with the input text."""
    pass

@dataclass
class Config:
    """Configuration settings for the language detector."""
    endpoint: str
    key: str

    @classmethod
    def from_env(cls) -> 'Config':
        """
        Creates a Config instance from environment variables.
        
        Returns:
            Config: The configuration object.
            
        Raises:
            ConfigurationError: If environment variables are missing or invalid.
        """
        load_dotenv()
        endpoint: Optional[str] = os.getenv('AI_SERVICE_ENDPOINT')
        key: Optional[str] = os.getenv('AI_SERVICE_KEY')
        
        if not endpoint or not key:
            raise ConfigurationError("Missing required environment variables: AI_SERVICE_ENDPOINT and/or AI_SERVICE_KEY")
        
        if not endpoint.startswith('https://'):
            raise ConfigurationError("AI_SERVICE_ENDPOINT must start with 'https://'")
        
        return cls(endpoint=endpoint, key=key)

class TextValidator:
    """Handles text validation for language detection."""
    
    MAX_TEXT_LENGTH = 5000  # Azure Text Analytics limit
    
    @classmethod
    def validate(cls, text: str) -> None:
        """
        Validates the input text.
        
        Args:
            text: The text to validate.
            
        Raises:
            InputError: If the text is empty or too long.
        """
        if not text.strip():
            raise InputError("Text cannot be empty")
        if len(text) > cls.MAX_TEXT_LENGTH:
            raise InputError(f"Text length exceeds maximum of {cls.MAX_TEXT_LENGTH} characters")

class LanguageDetector:
    """Handles language detection using Azure Text Analytics."""
    
    def __init__(self, config: Config):
        """
        Initializes the language detector with Azure credentials.
        
        Args:
            config: The configuration settings.
        """
        self.credential = AzureKeyCredential(config.key)
        self.client = TextAnalyticsClient(endpoint=config.endpoint, credential=self.credential)
    
    def detect_language(self, text: str) -> str:
        """
        Detects the language of the given text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            str: The name of the detected language.
            
        Raises:
            AzureError: If the Azure service call fails.
        """
        try:
            detected_language = self.client.detect_language(documents=[text])[0]
            return detected_language.primary_language.name
        except AzureError as ae:
            raise AzureError(f"Failed to detect language: {ae}")

# Check if running in debug mode
is_debug: bool = sys.gettrace() is not None
if is_debug:
    print("\n=== DEBUG MODE ===")
    print("Script location:", os.path.abspath(__file__))
    print("Initial working directory:", os.getcwd())

# Get the directory where the script is located
script_dir: str = os.path.dirname(os.path.abspath(__file__))
# Change to that directory
os.chdir(script_dir)

if is_debug:
    print("New working directory:", os.getcwd())
    print("Environment file exists:", os.path.exists('.env'))
    print("=== END DEBUG INFO ===\n")

def main() -> None:
    """
    Main function that handles the language detection service.
    
    This function:
    1. Loads environment variables from .env file
    2. Prompts user for text input
    3. Detects language for each input
    4. Continues until user enters 'quit'
    
    Raises:
        ConfigurationError: If environment variables are missing or invalid
        InputError: If input text is invalid
        AzureError: If Azure service call fails
        Exception: For any other unexpected errors
    """
    try:
        # Get configuration and initialize detector
        config = Config.from_env()
        detector = LanguageDetector(config)

        # Get user input (until they enter "quit")
        user_text: str = ''
        while user_text.lower() != 'quit':
            try:
                user_text = input('\nEnter some text ("quit" to stop)\n')
                if user_text.lower() != 'quit':
                    TextValidator.validate(user_text)
                    language: str = detector.detect_language(user_text)
                    print('Language:', language)
            except InputError as ie:
                print(f"Input error: {ie}")
                continue  # Continue to next input
            except AzureError as ae:
                print(f"Azure service error: {ae}")
                continue  # Continue to next input
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue  # Continue to next input

    except ConfigurationError as ce:
        print(f"Configuration error: {ce}")
        raise  # Re-raise configuration errors as they are fatal
    except Exception as ex:
        print(f"Fatal error: {ex}")
        raise  # Re-raise unexpected errors as they are fatal

if __name__ == "__main__":
    main()