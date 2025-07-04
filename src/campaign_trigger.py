# Campaign trigger script for lead generation system
# Monitors Airtable for campaign triggers and simulates sending emails/SMS

import os
import sys
import logging
import time
from typing import Dict, List

# Add the parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from src.airtable_client import airtable_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campaign_triggers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CampaignManager:
    # Manages email and SMS campaigns based on Airtable triggers
    
    def __init__(self):
        # Initialize the campaign manager
        self.sms_sent = 0
        self.email_sent = 0
        self.skipped_dnc = 0
        self.errors = 0
        
        logger.info("Initializing Campaign Manager")
        
        # Validate configuration
        if not config.validate():
            raise RuntimeError("Configuration validation failed")
    
    def run_campaign_check(self) -> Dict[str, int]:
        # Check for campaign triggers and execute campaigns
        # Returns: Dict[str, int] - Summary of campaign execution
        logger.info("Starting campaign trigger check")
        
        # Get all records with campaign triggers
        leads = airtable_client.get_campaign_ready_leads()
        
        if not leads:
            logger.info("No leads with active campaign triggers found")
            return self._get_summary()
        
        logger.info(f"Found {len(leads)} leads with campaign triggers")
        
        # Process each lead
        for lead in leads:
            try:
                self._process_lead_campaigns(lead)
            except Exception as e:
                logger.error(f"Error processing lead {lead.get('id', 'unknown')}: {e}")
                self.errors += 1
        
        # Log summary
        summary = self._get_summary()
        logger.info(f"Campaign check completed. Summary: {summary}")
        return summary
    
    def _process_lead_campaigns(self, lead: Dict) -> None:
        # Process campaign triggers for a single lead
        # Args: lead (Dict) - Lead record from Airtable
        record_id = lead['id']
        fields = lead['fields']
        
        # Extract lead information
        business_name = fields.get('Business Name', 'Unknown Business')
        owner_name = fields.get('Owner Name', 'Unknown Owner')
        email = fields.get('Email')
        mobile_number = fields.get('Mobile Number')
        do_not_contact = fields.get('Do Not Contact', False)
        send_sms = fields.get('Send SMS', False)
        send_email = fields.get('Send Email', False)
        
        logger.info(f"Processing campaigns for: {business_name} (ID: {record_id})")
        
        # Check if lead is marked as Do Not Contact
        if do_not_contact:
            logger.warning(f"Lead {business_name} marked as Do Not Contact, skipping all campaigns")
            self.skipped_dnc += 1
            self._clear_campaign_flags(record_id, send_sms, send_email)
            return
        
        # Process SMS campaign
        if send_sms:
            if mobile_number:
                self._send_sms_simulation(business_name, owner_name, mobile_number)
                self.sms_sent += 1
            else:
                logger.warning(f"SMS requested for {business_name} but no mobile number available")
            
            # Clear SMS flag
            self._clear_sms_flag(record_id)
        
        # Process Email campaign
        if send_email:
            if email:
                self._send_email_simulation(business_name, owner_name, email)
                self.email_sent += 1
            else:
                logger.warning(f"Email requested for {business_name} but no email address available")
            
            # Clear Email flag
            self._clear_email_flag(record_id)
    
    def _send_sms_simulation(self, business_name: str, owner_name: str, mobile_number: str) -> None:
        # Simulate sending an SMS message
        # Args: business_name (str) - Name of the business
        #       owner_name (str) - Name of the business owner
        #       mobile_number (str) - Mobile phone number
        sms_message = f"Hello {owner_name}, we have an opportunity regarding {business_name}. Please contact us to learn more."
        
        print(f"\n{'='*60}")
        print("📱 SIMULATING SMS SEND")
        print(f"{'='*60}")
        print(f"To: {mobile_number}")
        print(f"Recipient: {owner_name}")
        print(f"Business: {business_name}")
        print(f"Message: {sms_message}")
        print(f"{'='*60}\n")
        
        logger.info(f"SMS simulated to {mobile_number} for {business_name}")
        
        # Simulate processing delay
        time.sleep(0.5)
    
    def _send_email_simulation(self, business_name: str, owner_name: str, email: str) -> None:
        # Simulate sending an email message
        # Args: business_name (str) - Name of the business
        #       owner_name (str) - Name of the business owner
        #       email (str) - Email address
        subject = f"An Opportunity for {business_name}"
        body = f"""Dear {owner_name},

We hope this message finds you well. We have identified a potential opportunity that may be relevant to {business_name}.

Our team specializes in helping businesses like yours navigate complex situations and would like to discuss how we might be able to assist you.

Would you be available for a brief conversation this week? We can work around your schedule.

Best regards,
Lead Generation Team

P.S. If you prefer not to receive future communications, please reply with "UNSUBSCRIBE" and we will remove you from our contact list immediately."""
        
        print(f"\n{'='*60}")
        print("📧 SIMULATING EMAIL SEND")
        print(f"{'='*60}")
        print(f"To: {email}")
        print(f"Recipient: {owner_name}")
        print(f"Business: {business_name}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"{'='*60}\n")
        
        logger.info(f"Email simulated to {email} for {business_name}")
        
        # Simulate processing delay
        time.sleep(0.5)
    
    def _clear_campaign_flags(self, record_id: str, clear_sms: bool, clear_email: bool) -> None:
        # Clear campaign flags for a lead
        # Args: record_id (str) - Airtable record ID
        #       clear_sms (bool) - Whether to clear SMS flag
        #       clear_email (bool) - Whether to clear email flag
        update_data = {}
        
        if clear_sms:
            update_data['send_sms'] = False
        
        if clear_email:
            update_data['send_email'] = False
        
        if update_data:
            success = airtable_client.update_lead(record_id, update_data)
            if success:
                logger.info(f"Cleared campaign flags for record {record_id}")
            else:
                logger.error(f"Failed to clear campaign flags for record {record_id}")
    
    def _clear_sms_flag(self, record_id: str) -> None:
        # Clear SMS campaign flag
        success = airtable_client.update_lead(record_id, {'send_sms': False})
        if success:
            logger.info(f"Cleared SMS flag for record {record_id}")
        else:
            logger.error(f"Failed to clear SMS flag for record {record_id}")
    
    def _clear_email_flag(self, record_id: str) -> None:
        # Clear email campaign flag
        success = airtable_client.update_lead(record_id, {'send_email': False})
        if success:
            logger.info(f"Cleared email flag for record {record_id}")
        else:
            logger.error(f"Failed to clear email flag for record {record_id}")
    
    def _get_summary(self) -> Dict[str, int]:
        # Get campaign execution summary
        return {
            'sms_sent': self.sms_sent,
            'emails_sent': self.email_sent,
            'skipped_dnc': self.skipped_dnc,
            'errors': self.errors,
            'total_actions': self.sms_sent + self.email_sent + self.skipped_dnc
        }

def run_continuous_monitoring(check_interval: int = 300) -> None:
    # Run continuous monitoring for campaign triggers
    # Args: check_interval (int) - Interval between checks in seconds (default: 5 minutes)
    logger.info(f"Starting continuous campaign monitoring (check every {check_interval} seconds)")
    
    try:
        while True:
            logger.info("Running scheduled campaign check")
            
            campaign_manager = CampaignManager()
            summary = campaign_manager.run_campaign_check()
            
            if summary['total_actions'] > 0:
                print(f"\nCampaign Summary: {summary['sms_sent']} SMS, {summary['emails_sent']} emails, {summary['skipped_dnc']} skipped (DNC)")
            
            logger.info(f"Next check in {check_interval} seconds")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info("Continuous monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error in continuous monitoring: {e}")

def main():
    # Main entry point
    import argparse
    
    parser = argparse.ArgumentParser(description="Lead Generation Campaign Trigger")
    parser.add_argument(
        '--continuous', 
        action='store_true', 
        help='Run continuous monitoring for campaign triggers'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=300, 
        help='Check interval in seconds for continuous mode (default: 300)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("CAMPAIGN TRIGGER SYSTEM STARTING")
    logger.info("=" * 50)
    
    try:
        if args.continuous:
            run_continuous_monitoring(args.interval)
        else:
            # Single run
            campaign_manager = CampaignManager()
            summary = campaign_manager.run_campaign_check()
            
            # Print final summary
            print("\n" + "=" * 50)
            print("CAMPAIGN CHECK COMPLETE")
            print("=" * 50)
            print(f"SMS messages sent: {summary['sms_sent']}")
            print(f"Emails sent: {summary['emails_sent']}")
            print(f"Leads skipped (DNC): {summary['skipped_dnc']}")
            print(f"Errors encountered: {summary['errors']}")
            print(f"Total actions taken: {summary['total_actions']}")
            print("=" * 50)
            
            return 0 if summary['errors'] == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Campaign trigger interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Campaign trigger failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 