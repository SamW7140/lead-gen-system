# What it does

1. **Reads any filing** – PDF or scanned image, state liens or court complaints.
2. **Understands the text** – GPT-4 figures out who's involved, the case/lien ID, when it was filed, and why.
3. **Fills in the blanks** – A mock enrichment step adds an owner name, email, and phone number so you can see the full flow without paying for data just yet.
4. **Keeps you compliant** – Randomly flags ~20 % of numbers as *Do-Not-Call* so the DNC logic is proven.
5. **Drops everything into Airtable** – Each lead shows up with status, contact fields, and two checkboxes: *Send SMS* or *Send Email*.
6. **Fires campaigns on demand** – Tick a box in Airtable, run the campaign script, and a "pretend" text or email is printed. Swap in Twilio / SendGrid later and you're live.

<br>
## Tech Stack 

• Python 3.
• pdfplumber + PyPDF2 + Tesseract OCR for document ingestion.  
• OpenAI GPT-4 API for AI data extraction.  
• Mock Apollo/Clearbit and DNC services (easily swapped for live APIs).  
• airtable-python-api for storage/dashboard.  
• Twilio / SendGrid hooks ready for real messaging.  
• Robust logging, duplicate protection, and error handling baked in.

<br>

## Quick Start

```bash
# Clone & enter project
$ git clone...
$ cd lead-gen-system

# Install deps (create a venv first if you like)
$ pip install -r requirements.txt

# Copy env template and drop in your keys
$ cp env_template.txt .env
#  - OpenAI key (sk-...)
#  - Airtable API key (key...)
#  - Airtable Base ID (app...)

# Toss a few PDFs or images in /data
$ python src/main.py      # process documents
$ python src/campaign_trigger.py   # simulate outreach
```

Everything ends up in your Airtable base:

```
Business Name | Case/Lien ID | Filing Date | Owner | Email | Mobile | DNC | Send SMS | Send Email | Status
--------------|-------------|------------|-------|-------|--------|-----|----------|-----------|-------
```

**License**: MIT