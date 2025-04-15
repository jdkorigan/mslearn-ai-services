"""
Azure Text Analytics Language Detection Client (REST API)

This script uses the Azure Text Analytics REST API to detect the language of input text.
It requires Azure Cognitive Services credentials stored in a .env file.

Environment Variables:
    AI_SERVICE_ENDPOINT: The endpoint URL for the Azure Text Analytics service
    AI_SERVICE_KEY: The API key for authentication

Example:
    $ python rest-client.py
    Enter some text ("quit" to stop)
    Hello
    Language: English
"""

from dotenv import load_dotenv
import os
import http.client, base64, json, urllib
from urllib import request, parse, error
import sys

class ConfigurationError(Exception):
    """Raised when there's an issue with the configuration."""
    pass

class InputError(Exception):
    """Raised when there's an issue with the input text."""
    pass

class APIError(Exception):
    """Raised when there's an issue with the API call."""
    pass

# Check if running in debug mode
is_debug = sys.gettrace() is not None
if is_debug:
    print("\n=== DEBUG MODE ===")
    print("Script location:", os.path.abspath(__file__))
    print("Initial working directory:", os.getcwd())

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Change to that directory
os.chdir(script_dir)

if is_debug:
    print("New working directory:", os.getcwd())
    print("Environment file exists:", os.path.exists('.env'))
    print("=== END DEBUG INFO ===\n")

def validate_configuration() -> tuple[str, str]:
    """
    Validates the configuration settings.
    
    Returns:
        tuple[str, str]: The endpoint and key from environment variables.
        
    Raises:
        ConfigurationError: If environment variables are missing or invalid.
    """
    load_dotenv()
    endpoint = os.getenv('AI_SERVICE_ENDPOINT')
    key = os.getenv('AI_SERVICE_KEY')
    
    if not endpoint or not key:
        raise ConfigurationError("Missing required environment variables: AI_SERVICE_ENDPOINT and/or AI_SERVICE_KEY")
    
    if not endpoint.startswith('https://'):
        raise ConfigurationError("AI_SERVICE_ENDPOINT must start with 'https://'")
    
    return endpoint, key

def validate_text(text: str) -> None:
    """
    Validates the input text.
    
    Args:
        text: The text to validate.
        
    Raises:
        InputError: If the text is empty or too long.
    """
    if not text.strip():
        raise InputError("Text cannot be empty")
    if len(text) > 5000:  # Azure Text Analytics limit
        raise InputError("Text length exceeds maximum of 5000 characters")

def main():
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
        APIError: If API call fails
        Exception: For any other unexpected errors
    """
    try:
        # Get and validate configuration
        endpoint, key = validate_configuration()

        # Get user input (until they enter "quit")
        userText = ''
        while userText.lower() != 'quit':
            try:
                userText = input('Enter some text ("quit" to stop)\n')
                if userText.lower() != 'quit':
                    validate_text(userText)
                    GetLanguage(endpoint, key, userText)
            except InputError as ie:
                print(f"Input error: {ie}")
                continue  # Continue to next input
            except APIError as ae:
                print(f"API error: {ae}")
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

def GetLanguage(endpoint: str, key: str, text: str) -> None:
    """
    Detects the language of the given text using Azure Text Analytics REST API.
    
    Args:
        endpoint: The Azure service endpoint.
        key: The API key for authentication.
        text: The text to analyze for language detection.
        
    Raises:
        APIError: If the API call fails or returns an error.
        
    The function:
    1. Constructs a JSON request body
    2. Makes an HTTP POST request to the Azure service
    3. Processes the response to extract the detected language
    4. Prints the results
    """
    try:
        # Construct the JSON request body
        jsonBody = {
            "documents":[
                {"id": 1,
                 "text": text}
            ]
        }

        # Let's take a look at the JSON we'll send to the service
        print(json.dumps(jsonBody, indent=2))

        # Make an HTTP request to the REST interface
        uri = endpoint.rstrip('/').replace('https://', '')
        conn = http.client.HTTPSConnection(uri)

        # Add the authentication key to the request header
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': key
        }

        # Use the Text Analytics language API
        conn.request("POST", "/text/analytics/v3.1/languages?", str(jsonBody).encode('utf-8'), headers)

        # Send the request
        response = conn.getresponse()
        data = response.read().decode("UTF-8")

        # If the call was successful, get the response
        if response.status == 200:
            # Display the JSON response in full (just so we can see it)
            results = json.loads(data)
            print(json.dumps(results, indent=2))

            # Extract the detected language name for each document
            for document in results["documents"]:
                print("\nLanguage:", document["detectedLanguage"]["name"])
        else:
            # Something went wrong, raise an API error
            raise APIError(f"API returned status {response.status}: {data}")

        conn.close()

    except json.JSONDecodeError as je:
        raise APIError(f"Failed to parse API response: {je}")
    except http.client.HTTPException as he:
        raise APIError(f"HTTP error occurred: {he}")
    except Exception as ex:
        raise APIError(f"Unexpected error during API call: {ex}")

if __name__ == "__main__":
    main()