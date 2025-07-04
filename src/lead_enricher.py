# Lead enrichment module for lead generation system
# Provides mock functions for lead enrichment and DNC checking

import random
import logging
import time
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data for realistic responses
MOCK_FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily",
    "James", "Ashley", "Christopher", "Amanda", "Matthew", "Jessica", "Joshua",
    "Jennifer", "Daniel", "Elizabeth", "Anthony", "Megan", "Mark", "Nicole"
]

MOCK_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson"
]

MOCK_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com",
    "company.com", "business.net", "enterprise.org", "corp.com", "group.co"
]

MOCK_AREA_CODES = [
    "555", "323", "213", "415", "212", "718", "646", "917", "310", "424",
    "202", "301", "703", "571", "954", "305", "786", "407", "321", "561"
]

def enrich_lead_mock(business_name: str) -> Dict[str, str]:
    # Mock function to simulate lead enrichment from Apollo/Clearbit APIs
    # Args: business_name (str) - Name of the business to enrich
    # Returns: Dict[str, str] - Mock enrichment data
    if not business_name:
        logger.warning("No business name provided for enrichment")
        return _generate_empty_enrichment()
    
    logger.info(f"Mock enriching lead: {business_name}")
    
    # Simulate API delay
    time.sleep(random.uniform(0.1, 0.5))
    
    # Randomly choose enrichment service
    service = random.choice(["Apollo (Mock)", "Clearbit (Mock)"])
    
    # Generate mock data
    first_name = random.choice(MOCK_FIRST_NAMES)
    last_name = random.choice(MOCK_LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    
    # Generate realistic email
    email = _generate_mock_email(first_name, last_name, business_name)
    
    # Generate mock phone number
    phone = _generate_mock_phone()
    
    # Sometimes return incomplete data to simulate real-world scenarios
    success_rate = 0.85  # 85% success rate
    if random.random() > success_rate:
        logger.info(f"Mock enrichment failed for {business_name}")
        return _generate_partial_enrichment(service)
    
    enrichment_data = {
        'owner_name': full_name,
        'email': email,
        'mobile_number': phone,
        'enrichment_service': service
    }
    
    logger.info(f"Mock enrichment successful: {enrichment_data}")
    return enrichment_data

def _generate_mock_email(first_name: str, last_name: str, business_name: str) -> str:
    # Generate a realistic mock email address
    # Clean business name for domain
    business_clean = ''.join(c.lower() for c in business_name if c.isalnum())[:10]
    
    # Choose email format
    formats = [
        f"{first_name.lower()}.{last_name.lower()}@{random.choice(MOCK_EMAIL_DOMAINS)}",
        f"{first_name.lower()}{last_name.lower()}@{random.choice(MOCK_EMAIL_DOMAINS)}",
        f"{first_name[0].lower()}{last_name.lower()}@{random.choice(MOCK_EMAIL_DOMAINS)}",
        f"{first_name.lower()}@{business_clean}.com" if business_clean else f"{first_name.lower()}@company.com"
    ]
    
    return random.choice(formats)

def _generate_mock_phone() -> str:
    # Generate a realistic mock phone number
    area_code = random.choice(MOCK_AREA_CODES)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    return f"+1{area_code}{exchange}{number}"

def _generate_empty_enrichment() -> Dict[str, Optional[str]]:
    # Generate empty enrichment data
    return {
        'owner_name': None,
        'email': None,
        'mobile_number': None,
        'enrichment_service': 'Failed'
    }

def _generate_partial_enrichment(service: str) -> Dict[str, Optional[str]]:
    # Generate partial enrichment data to simulate real-world API limitations
    first_name = random.choice(MOCK_FIRST_NAMES)
    last_name = random.choice(MOCK_LAST_NAMES)
    
    # Randomly provide only some fields
    data = {
        'owner_name': f"{first_name} {last_name}" if random.random() > 0.3 else None,
        'email': _generate_mock_email(first_name, last_name, "company") if random.random() > 0.5 else None,
        'mobile_number': _generate_mock_phone() if random.random() > 0.6 else None,
        'enrichment_service': service
    }
    
    return data

def check_dnc_status_mock(phone_number: Optional[str]) -> Dict[str, bool]:
    # Mock function to simulate DNC (Do Not Call) list checking
    # Args: phone_number (Optional[str]) - Phone number to check
    # Returns: Dict[str, bool] - DNC status result
    if not phone_number:
        logger.warning("No phone number provided for DNC check")
        return {'is_dnc': False}
    
    logger.info(f"Mock DNC check for: {phone_number}")
    
    # Simulate API delay
    time.sleep(random.uniform(0.1, 0.3))
    
    # 20% chance of being on DNC list
    is_dnc = random.random() < 0.2
    
    result = {'is_dnc': is_dnc}
    
    if is_dnc:
        logger.warning(f"Phone number {phone_number} is on DNC list")
    else:
        logger.info(f"Phone number {phone_number} is not on DNC list")
    
    return result

def enrich_lead_with_dnc_check(business_name: str) -> Dict:
    # Convenience function to perform both enrichment and DNC check
    # Args: business_name (str) - Business name to enrich
    # Returns: Dict - Combined enrichment and DNC data
    # Get enrichment data
    enrichment_data = enrich_lead_mock(business_name)
    
    # Check DNC status if we have a phone number
    dnc_data = check_dnc_status_mock(enrichment_data.get('mobile_number'))
    
    # Combine data
    combined_data = {
        **enrichment_data,
        'dnc_status': dnc_data['is_dnc']
    }
    
    return combined_data 