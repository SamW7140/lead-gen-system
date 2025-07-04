# Configuration module for lead generation system
# Loads and validates environment variables from .env file

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    # Configuration class to manage environment variables
    
    def __init__(self):
        # Initialize configuration and validate required variables
        self.openai_api_key = self._get_required_env('OPENAI_API_KEY')
        self.airtable_api_key = self._get_required_env('AIRTABLE_API_KEY')
        self.airtable_base_id = self._get_required_env('AIRTABLE_BASE_ID')
        self.airtable_table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Leads')
        self.tesseract_cmd_path = os.getenv('TESSERACT_CMD_PATH')
        
        # Set tesseract path if provided
        if self.tesseract_cmd_path:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd_path
            except ImportError:
                print("Warning: pytesseract not installed, OCR functionality will not work")
    
    @staticmethod
    def _get_required_env(var_name: str) -> str:
        # Get required environment variable or raise error if missing
        value = os.getenv(var_name)
        if not value or value == "":
            raise ValueError(f"Required environment variable {var_name} is not set")
        if value.endswith("..."):
            raise ValueError(f"Environment variable {var_name} appears to be a template value")
        return value
    
    def validate(self) -> bool:
        # Validate all configuration values
        try:
            # Test OpenAI API key format
            if not self.openai_api_key.startswith('sk-'):
                print("Warning: OpenAI API key doesn't start with 'sk-'")
            
            # Test Airtable API key format
            if not self.airtable_api_key.startswith('key'):
                print("Warning: Airtable API key doesn't start with 'key'")
            
            # Test Airtable base ID format
            if not self.airtable_base_id.startswith('app'):
                print("Warning: Airtable base ID doesn't start with 'app'")
            
            print("✓ Configuration validation passed")
            return True
            
        except Exception as e:
            print(f"✗ Configuration validation failed: {e}")
            return False

# Global configuration instance
config = Config() 