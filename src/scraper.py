import pandas as pd
import config
import settings
import requests
import re
import html
from io import BytesIO
from database import Database

logger = settings.logging.getLogger("scraper")

def decode_hex_and_entities(text):
    # Decode hex encoded characters
    def hex_replace(match):
        return bytes.fromhex(match.group(1)).decode('utf-8')

    # Replace all hex patterns (like \x61 for 'a')
    text = re.sub(r'\\x([0-9a-fA-F]{2})', hex_replace, text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    return text

def scrape_perks(url):
    try:
        # Download the Excel file from the given URL
        response = requests.get(url)
        response.raise_for_status()

        # Log content-type to verify file format
        logger.info(f"Content-Type: {response.headers['Content-Type']}")

        # Ensure the content is an Excel file
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' not in response.headers['Content-Type']:
            logger.error("The URL does not point to a valid Excel file.")
            return []

        # Read the Excel file
        excel_data = BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl')

        # Extract specific columns
        required_columns = ['Name', 'Type', 'Specialization', 'Specialization Effects']
        if not all(column in df.columns for column in required_columns):
            logger.error("The required columns are not present in the Excel file.")
            return []

        # Decode hex and HTML entities in the required columns
        for column in required_columns:
            df[column] = df[column].apply(lambda x: decode_hex_and_entities(x) if isinstance(x, str) else x)

        # Extract the required columns
        perks = df[required_columns].dropna().to_dict(orient='records')
        logger.info("Perks scraped from the online Excel file.")
        return perks
    except requests.RequestException as e:
        logger.error(f"Error fetching perks from {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error processing the Excel file: {e}")
        return []

def update_perks():
    perks = scrape_perks(config.PERKS_URL)
    if perks:
        db = Database()
        db.update_perks(perks)

if __name__ == '__main__':
    update_perks()