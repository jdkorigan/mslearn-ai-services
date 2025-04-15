import unittest
from unittest.mock import patch, MagicMock
from rest_client import main, GetLanguage
import json
import http.client

class TestRestClient(unittest.TestCase):
    @patch('rest_client.load_dotenv')
    @patch('rest_client.os.getenv')
    def test_main_with_valid_input(self, mock_getenv, mock_load_dotenv):
        # Setup mock environment variables
        mock_getenv.side_effect = lambda x: {
            'AI_SERVICE_ENDPOINT': 'https://test-endpoint.com',
            'AI_SERVICE_KEY': 'test-key'
        }.get(x)
        
        # Mock user input
        with patch('builtins.input', side_effect=['Hello', 'quit']):
            with patch('rest_client.GetLanguage'):
                main()
                
        mock_load_dotenv.assert_called_once()
        mock_getenv.assert_any_call('AI_SERVICE_ENDPOINT')
        mock_getenv.assert_any_call('AI_SERVICE_KEY')

    @patch('rest_client.http.client.HTTPSConnection')
    def test_get_language(self, mock_connection):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "documents": [{
                "detectedLanguage": {
                    "name": "English"
                }
            }]
        }).encode('utf-8')
        
        mock_connection.return_value.getresponse.return_value = mock_response

        # Test the function
        GetLanguage('Hello')
        
        # Verify the request was made correctly
        mock_connection.return_value.request.assert_called_once()
        args, kwargs = mock_connection.return_value.request.call_args
        self.assertEqual(args[0], 'POST')
        self.assertTrue('/text/analytics/v3.1/languages?' in args[1])
        self.assertIn('Ocp-Apim-Subscription-Key', kwargs['headers'])

    @patch('rest_client.load_dotenv')
    @patch('rest_client.os.getenv')
    def test_main_with_missing_env_vars(self, mock_getenv, mock_load_dotenv):
        # Setup mock environment variables to return None
        mock_getenv.return_value = None
        
        with self.assertRaises(Exception):
            main()

    @patch('rest_client.http.client.HTTPSConnection')
    def test_get_language_with_error_response(self, mock_connection):
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.read.return_value = b'Error message'
        
        mock_connection.return_value.getresponse.return_value = mock_response

        # Test the function
        GetLanguage('Hello')
        
        # Verify error handling
        mock_connection.return_value.close.assert_called_once()

if __name__ == '__main__':
    unittest.main() 