# Airtable client module for lead generation system
# Handles all interactions with Airtable base for storing and retrieving leads

import logging
from typing import Dict, List, Optional
from airtable import Airtable
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirtableClient:
    # Client for interacting with Airtable API
    
    def __init__(self):
        # Initialize Airtable client with configuration
        self.base_id = config.airtable_base_id
        self.table_name = config.airtable_table_name
        self.api_key = config.airtable_api_key
        
        # Initialize Airtable connection
        self.airtable = Airtable(
            base_id=self.base_id,
            table_name=self.table_name,
            api_key=self.api_key
        )
        
        logger.info(f"Initialized Airtable client for base: {self.base_id}, table: {self.table_name}")
    
    def find_existing_lead(self, source_document: str = None, case_id: str = None) -> Optional[Dict]:
        # Check if a lead already exists in Airtable to prevent duplicates
        # Args: source_document (str) - Name of source document
        #       case_id (str) - Case or lien ID
        # Returns: Optional[Dict] - Existing record if found, None otherwise
        try:
            # Build search formula
            filters = []
            
            if source_document:
                filters.append(f"{{Source Document}} = '{source_document}'")
            
            if case_id:
                filters.append(f"{{Case or Lien ID}} = '{case_id}'")
            
            if not filters:
                logger.warning("No search criteria provided for duplicate check")
                return None
            
            # Create OR formula for multiple search criteria
            formula = " OR ".join([f"({f})" for f in filters])
            
            # Search for existing records
            records = self.airtable.search('', filter_by_formula=formula)
            
            if records:
                logger.info(f"Found existing record: {records[0]['id']}")
                return records[0]
            else:
                logger.info("No existing record found")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for existing lead: {e}")
            return None
    
    def create_lead(self, lead_data: Dict) -> Optional[str]:
        # Create a new lead record in Airtable
        # Args: lead_data (Dict) - Lead data to insert
        # Returns: Optional[str] - Record ID if successful, None otherwise
        try:
            # Map data to Airtable field names
            airtable_data = self._map_to_airtable_fields(lead_data)
            
            # Create record
            record = self.airtable.insert(airtable_data)
            
            record_id = record['id']
            logger.info(f"Successfully created lead record: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error creating lead in Airtable: {e}")
            return None
    
    def update_lead(self, record_id: str, update_data: Dict) -> bool:
        # Update an existing lead record in Airtable
        # Args: record_id (str) - Airtable record ID
        #       update_data (Dict) - Data to update
        # Returns: bool - True if successful, False otherwise
        try:
            # Map data to Airtable field names
            airtable_data = self._map_to_airtable_fields(update_data)
            
            # Update record
            self.airtable.update(record_id, airtable_data)
            
            logger.info(f"Successfully updated lead record: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating lead in Airtable: {e}")
            return False
    
    def get_all_leads(self) -> List[Dict]:
        # Retrieve all lead records from Airtable
        # Returns: List[Dict] - List of all lead records
        try:
            records = self.airtable.get_all()
            logger.info(f"Retrieved {len(records)} lead records from Airtable")
            return records
            
        except Exception as e:
            logger.error(f"Error retrieving leads from Airtable: {e}")
            return []
    
    def get_campaign_ready_leads(self) -> List[Dict]:
        # Get leads that have campaign checkboxes enabled
        # Returns: List[Dict] - Leads ready for campaigns
        try:
            # Filter for records with Send SMS or Send Email checked
            formula = "OR({Send SMS} = TRUE(), {Send Email} = TRUE())"
            records = self.airtable.search('', filter_by_formula=formula)
            
            logger.info(f"Found {len(records)} leads ready for campaigns")
            return records
            
        except Exception as e:
            logger.error(f"Error retrieving campaign-ready leads: {e}")
            return []
    
    def _map_to_airtable_fields(self, data: Dict) -> Dict:
        # Map internal data structure to Airtable field names
        # Args: data (Dict) - Internal data structure
        # Returns: Dict - Mapped data for Airtable
        field_mapping = {
            'business_name': 'Business Name',
            'case_or_lien_id': 'Case or Lien ID',
            'source_document': 'Source Document',
            'source_type': 'Source Type',
            'document_summary': 'Document Summary',
            'owner_name': 'Owner Name',
            'email': 'Email',
            'mobile_number': 'Mobile Number',
            'dnc_status': 'DNC Status',
            'enrichment_service': 'Enrichment Service',
            'status': 'Status',
            'send_sms': 'Send SMS',
            'send_email': 'Send Email',
            'do_not_contact': 'Do Not Contact',
            'filing_date': 'Filing Date'
        }
        
        mapped_data = {}
        for internal_key, airtable_field in field_mapping.items():
            if internal_key in data and data[internal_key] is not None:
                mapped_data[airtable_field] = data[internal_key]
        
        return mapped_data

# Global client instance
airtable_client = AirtableClient() 