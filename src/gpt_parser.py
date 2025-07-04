# GPT-4 parsing module for lead generation system
# Uses OpenAI API to parse document text and extract structured data

import json
import logging
from typing import Dict, Optional
from openai import OpenAI
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=config.openai_api_key)

def parse_document_with_gpt(text_content: str, source_type: str) -> Optional[Dict]:
    # Parse document text using GPT-4 to extract structured lead data
    # Args: text_content (str) - The extracted text from the document
    #       source_type (str) - Type of document ("Court Filing" or "Lien Database")
    # Returns: Optional[Dict] - Parsed data as dictionary or None if parsing fails
    if not text_content or not text_content.strip():
        logger.error("No text content provided for parsing")
        return None
    
    logger.info(f"Parsing {source_type} document with GPT-4 ({len(text_content)} characters)")
    
    try:
        # Create the prompt
        prompt = _create_parsing_prompt(text_content, source_type)
        
        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": _get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=1000
        )
        
        # Extract the response
        gpt_response = response.choices[0].message.content
        logger.info("Received response from GPT-4")
        
        # Parse JSON response
        parsed_data = _parse_gpt_response(gpt_response)
        
        if parsed_data:
            logger.info("Successfully parsed document data")
            return parsed_data
        else:
            logger.error("Failed to parse GPT-4 response as valid JSON")
            return None
            
    except Exception as e:
        logger.error(f"Error calling GPT-4 API: {e}")
        return None

def _get_system_prompt() -> str:
    # Get the system prompt for GPT-4
    return """You are an expert legal document parser specializing in extracting business information from court filings and lien documents. 

Your task is to analyze document text and extract key business information in a structured format. You must return ONLY valid JSON, with no additional text, explanations, or formatting.

Focus on identifying:
- Business names (including trade names, DBA names, and corporate entities)
- Case or lien identification numbers
- Filing dates
- Brief document summaries

If information is unclear or missing, use null for that field. Be conservative and accurate in your extractions."""

def _create_parsing_prompt(text_content: str, source_type: str) -> str:
    # Create the parsing prompt for GPT-4
    # Args: text_content (str) - Document text to parse
    #       source_type (str) - Type of source document
    # Returns: str - Formatted prompt for GPT-4
    prompt = f"""From the following document text, which is a '{source_type}', please extract the following information in a structured JSON format.
If a piece of information is not present, use null for its value.

Required fields:
- business_name: The name of the primary business or defendant involved (string)
- case_or_lien_id: The unique identifier for the court case or lien filing (string)
- filing_date: The date the document was filed in YYYY-MM-DD format (string or null)
- document_summary: A brief, one-sentence summary of the document's purpose (string)

Document Text:
---
{text_content}
---

Return only valid JSON with these exact field names:"""
    
    return prompt

def _parse_gpt_response(gpt_response: str) -> Optional[Dict]:
    # Parse GPT-4 response and extract JSON data
    # Args: gpt_response (str) - Raw response from GPT-4
    # Returns: Optional[Dict] - Parsed JSON data or None if parsing fails
    try:
        # Clean the response - remove any code block markers
        cleaned_response = gpt_response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        
        cleaned_response = cleaned_response.strip()
        
        # Parse JSON
        parsed_data = json.loads(cleaned_response)
        
        # Validate required fields
        required_fields = ['business_name', 'case_or_lien_id', 'filing_date', 'document_summary']
        
        if not isinstance(parsed_data, dict):
            logger.error("GPT response is not a valid JSON object")
            return None
        
        # Ensure all required fields are present
        for field in required_fields:
            if field not in parsed_data:
                logger.warning(f"Missing required field: {field}")
                parsed_data[field] = None
        
        # Clean up the data
        parsed_data = _clean_parsed_data(parsed_data)
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response as JSON: {e}")
        logger.error(f"Response was: {gpt_response}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing GPT response: {e}")
        return None

def _clean_parsed_data(data: Dict) -> Dict:
    # Clean and validate the parsed data
    # Args: data (Dict) - Raw parsed data
    # Returns: Dict - Cleaned data
    cleaned = {}
    
    # Clean business_name
    business_name = data.get('business_name')
    if business_name and isinstance(business_name, str):
        cleaned['business_name'] = business_name.strip()
    else:
        cleaned['business_name'] = None
    
    # Clean case_or_lien_id
    case_id = data.get('case_or_lien_id')
    if case_id and isinstance(case_id, str):
        cleaned['case_or_lien_id'] = case_id.strip()
    else:
        cleaned['case_or_lien_id'] = None
    
    # Clean filing_date
    filing_date = data.get('filing_date')
    if filing_date and isinstance(filing_date, str) and filing_date.strip():
        cleaned['filing_date'] = filing_date.strip()
    else:
        cleaned['filing_date'] = None
    
    # Clean document_summary
    summary = data.get('document_summary')
    if summary and isinstance(summary, str):
        cleaned['document_summary'] = summary.strip()
    else:
        cleaned['document_summary'] = None
    
    return cleaned 