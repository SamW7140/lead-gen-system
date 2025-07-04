# Main orchestrator script for lead generation system
# Processes documents from the data directory and stores results in Airtable

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional

# Add the parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from config import config
from src.document_processor import extract_text_from_file, get_processable_files
from src.gpt_parser import parse_document_with_gpt
from src.lead_enricher import enrich_lead_with_dnc_check
from src.airtable_client import airtable_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lead_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LeadGenerationPipeline:
    # Main pipeline for processing documents and generating leads
    
    def __init__(self, data_directory: str = "data"):
        # Initialize the pipeline
        # Args: data_directory (str) - Directory containing documents to process
        self.data_directory = data_directory
        self.processed_count = 0
        self.error_count = 0
        self.skipped_count = 0
        
        logger.info("Initializing Lead Generation Pipeline")
        
        # Validate configuration
        if not config.validate():
            raise RuntimeError("Configuration validation failed")
    
    def run(self) -> Dict[str, int]:
        # Run the complete lead generation pipeline
        # Returns: Dict[str, int] - Summary of processing results
        logger.info("Starting lead generation pipeline")
        
        # Get all processable files
        files = get_processable_files(self.data_directory)
        
        if not files:
            logger.warning(f"No processable files found in {self.data_directory}")
            return self._get_summary()
        
        logger.info(f"Found {len(files)} files to process")
        
        # Process each file
        for file_path in files:
            try:
                self._process_single_file(file_path)
            except Exception as e:
                logger.error(f"Unexpected error processing {file_path}: {e}")
                self.error_count += 1
        
        # Log summary
        summary = self._get_summary()
        logger.info(f"Pipeline completed. Summary: {summary}")
        return summary
    
    def _process_single_file(self, file_path: str) -> bool:
        # Process a single document file
        # Args: file_path (str) - Path to the file to process
        # Returns: bool - True if successful, False otherwise
        filename = os.path.basename(file_path)
        logger.info(f"Processing file: {filename}")
        
        try:
            # Step 1: Check if already processed
            existing_record = airtable_client.find_existing_lead(source_document=filename)
            if existing_record:
                logger.info(f"File {filename} already processed, skipping")
                self.skipped_count += 1
                return True
            
            # Step 2: Extract text from document
            logger.info(f"Extracting text from {filename}")
            text_content = extract_text_from_file(file_path)
            
            if not text_content:
                logger.error(f"Failed to extract text from {filename}")
                self._create_error_record(filename, "Text extraction failed")
                self.error_count += 1
                return False
            
            # Step 3: Determine source type
            source_type = self._determine_source_type(filename)
            
            # Step 4: Parse with GPT-4
            logger.info(f"Parsing document with GPT-4")
            parsed_data = parse_document_with_gpt(text_content, source_type)
            
            if not parsed_data:
                logger.error(f"Failed to parse document with GPT-4")
                self._create_error_record(filename, "GPT-4 parsing failed")
                self.error_count += 1
                return False
            
            # Step 5: Enrich lead data
            business_name = parsed_data.get('business_name')
            if business_name:
                logger.info(f"Enriching lead data for: {business_name}")
                enrichment_data = enrich_lead_with_dnc_check(business_name)
            else:
                logger.warning("No business name found, skipping enrichment")
                enrichment_data = {
                    'owner_name': None,
                    'email': None,
                    'mobile_number': None,
                    'enrichment_service': 'Skipped',
                    'dnc_status': False
                }
            
            # Step 6: Combine all data
            lead_data = self._combine_lead_data(
                filename, source_type, parsed_data, enrichment_data
            )
            
            # Step 7: Save to Airtable
            logger.info(f"Saving lead to Airtable")
            record_id = airtable_client.create_lead(lead_data)
            
            if record_id:
                logger.info(f"Successfully created lead record: {record_id}")
                self.processed_count += 1
                return True
            else:
                logger.error(f"Failed to create Airtable record")
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            self._create_error_record(filename, f"Processing error: {str(e)}")
            self.error_count += 1
            return False
    
    def _determine_source_type(self, filename: str) -> str:
        # Determine the source type based on filename
        # Args: filename (str) - Name of the file
        # Returns: str - Source type
        filename_lower = filename.lower()
        
        if 'court' in filename_lower or 'filing' in filename_lower:
            return "Court Filing"
        elif 'lien' in filename_lower:
            return "Lien Database"
        else:
            # Default based on file type
            if filename_lower.endswith('.pdf'):
                return "Court Filing"
            else:
                return "Lien Database"
    
    def _combine_lead_data(
        self, 
        filename: str, 
        source_type: str, 
        parsed_data: Dict, 
        enrichment_data: Dict
    ) -> Dict:
        # Combine all data into a single lead record
        # Args: filename (str) - Source document filename
        #       source_type (str) - Type of source document
        #       parsed_data (Dict) - Data from GPT-4 parsing
        #       enrichment_data (Dict) - Data from enrichment process
        # Returns: Dict - Combined lead data
        lead_data = {
            # Document info
            'source_document': filename,
            'source_type': source_type,
            'status': 'Processed',
            
            # Parsed data
            'business_name': parsed_data.get('business_name'),
            'case_or_lien_id': parsed_data.get('case_or_lien_id'),
            'filing_date': parsed_data.get('filing_date'),
            'document_summary': parsed_data.get('document_summary'),
            
            # Enrichment data
            'owner_name': enrichment_data.get('owner_name'),
            'email': enrichment_data.get('email'),
            'mobile_number': enrichment_data.get('mobile_number'),
            'enrichment_service': enrichment_data.get('enrichment_service'),
            'dnc_status': enrichment_data.get('dnc_status', False),
            
            # Campaign settings
            'send_sms': False,
            'send_email': False,
            'do_not_contact': enrichment_data.get('dnc_status', False)
        }
        
        return lead_data
    
    def _create_error_record(self, filename: str, error_message: str) -> None:
        # Create an error record in Airtable
        # Args: filename (str) - Source document filename
        #       error_message (str) - Error description
        try:
            error_data = {
                'source_document': filename,
                'status': 'Error',
                'document_summary': f"Processing failed: {error_message}",
                'business_name': None,
                'case_or_lien_id': None,
                'source_type': self._determine_source_type(filename),
                'do_not_contact': True  # Mark as do not contact due to error
            }
            
            airtable_client.create_lead(error_data)
            logger.info(f"Created error record for {filename}")
            
        except Exception as e:
            logger.error(f"Failed to create error record: {e}")
    
    def _get_summary(self) -> Dict[str, int]:
        # Get processing summary
        return {
            'processed': self.processed_count,
            'errors': self.error_count,
            'skipped': self.skipped_count,
            'total': self.processed_count + self.error_count + self.skipped_count
        }

def main():
    # Main entry point
    logger.info("=" * 50)
    logger.info("LEAD GENERATION SYSTEM STARTING")
    logger.info("=" * 50)
    
    try:
        # Initialize and run pipeline
        pipeline = LeadGenerationPipeline()
        summary = pipeline.run()
        
        # Print final summary
        print("\n" + "=" * 50)
        print("PROCESSING COMPLETE")
        print("=" * 50)
        print(f"Total files processed: {summary['processed']}")
        print(f"Files with errors: {summary['errors']}")
        print(f"Files skipped (already processed): {summary['skipped']}")
        print(f"Total files found: {summary['total']}")
        print("=" * 50)
        
        if summary['errors'] > 0:
            print("\nCheck the log file 'lead_generation.log' for error details.")
        
        return 0 if summary['errors'] == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 