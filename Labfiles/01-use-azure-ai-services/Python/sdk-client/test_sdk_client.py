import unittest
from unittest.mock import patch, MagicMock
from sdk_client import main, GetLanguage
import os

class TestSDKClient(unittest.TestCase):
    @patch('sdk_client.load_dotenv')
    @patch('sdk_client.os.getenv')
    def test_main_with_valid_input(self, mock_getenv, mock_load_dotenv):
        # Setup mock environment variables
        mock_getenv.side_effect = lambda x: {
            'AI_SERVICE_ENDPOINT': 'https://test-endpoint.com',
            'AI_SERVICE_KEY': 'test-key'
        }.get(x)
        
        # Mock user input
        with patch('builtins.input', side_effect=['Hello', 'quit']):
            with patch('sdk_client.GetLanguage', return_value='English'):
                main()
                
        mock_load_dotenv.assert_called_once()
        mock_getenv.assert_any_call('AI_SERVICE_ENDPOINT')
        mock_getenv.assert_any_call('AI_SERVICE_KEY')

    @patch('sdk_client.AzureKeyCredential')
    @patch('sdk_client.TextAnalyticsClient')
    def test_get_language(self, mock_client_class, mock_credential):
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_detected_language = MagicMock()
        mock_detected_language.primary_language.name = 'English'
        mock_client.detect_language.return_value = [mock_detected_language]

        # Test the function
        result = GetLanguage('Hello')
        
        self.assertEqual(result, 'English')
        mock_client.detect_language.assert_called_once_with(documents=['Hello'])

    @patch('sdk_client.load_dotenv')
    @patch('sdk_client.os.getenv')
    def test_main_with_missing_env_vars(self, mock_getenv, mock_load_dotenv):
        # Setup mock environment variables to return None
        mock_getenv.return_value = None
        
        with self.assertRaises(Exception):
            main()

    @patch('sdk_client.AzureKeyCredential')
    @patch('sdk_client.TextAnalyticsClient')
    def test_get_language_with_empty_text(self, mock_client_class, mock_credential):
        # Test with empty text
        with self.assertRaises(Exception):
            GetLanguage('')

if __name__ == '__main__':
    unittest.main() 