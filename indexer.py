import json
import os
import sys
import datetime
import argparse
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Mapping config keys to URL path slugs
# If you add a new country to scraper.py, add its mapping here.
COUNTRY_SLUG_MAP = {
    "united_kingdom": "uk",
    "united_states": "us",
    "australia": "au",
    "canada": "ca",
    "indonesia": "id", # Future proofing
    "germany": "de",   # Future proofing
    "france": "fr",    # Future proofing
    "spain": "es",     # Future proofing
}

def get_indexing_service(service_account_file):
    """Authenticates and returns the Indexing API service."""
    scopes = ["https://www.googleapis.com/auth/indexing"]
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_file, scopes=scopes
        )
        return build("indexing", "v3", credentials=credentials)
    except Exception as e:
        print(f"❌ Error: Failed to authenticate with service account: {e}")
        return None

def trigger_indexing():
    parser = argparse.ArgumentParser(description="Automated Google Indexing API Trigger")
    parser.add_argument("--force", action="store_true", help="Force indexing regardless of last_updated date")
    args = parser.parse_args()

    config_path = 'dist/global_tax_config.json'
    service_account_file = 'service_account.json'
    base_url = "https://tax.errhub.xyz"
    
    # 1. Check if service account exists
    if not os.path.exists(service_account_file):
        print(f"⚠️ Warning: '{service_account_file}' not found. Indexing skipped.")
        print("   Please provide your Google Service Account JSON to enable automated indexing.")
        return

    # 2. Check if data config exists
    if not os.path.exists(config_path):
        print(f"❌ Error: {config_path} not found. Run scraper.py first.")
        return

    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            last_updated = config_data.get('metadata', {}).get('last_updated')
    except Exception as e:
        print(f"❌ Error: Failed to read tax data: {e}")
        return

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 3. Date Check (Skipped if --force is used)
    if not args.force:
        if last_updated != today:
            print(f"ℹ️ Info: Data last updated on {last_updated}. No indexing needed today ({today}).")
            print("   Use --force to override.")
            return
        else:
            print(f"🚀 Data refresh detected for {today}. Preparing to index...")
    else:
        print(f"🔧 Force mode enabled. Proceeding with indexing regardless of date...")

    # 4. Dynamic URL Generation
    urls = [f"{base_url}/"] # Always index homepage
    
    if 'data' in config_data:
        for key in config_data['data'].keys():
            if key in COUNTRY_SLUG_MAP:
                slug = COUNTRY_SLUG_MAP[key]
                urls.append(f"{base_url}/{slug}")
            else:
                print(f"⚠️ Warning: Check mapping for new country key: '{key}'")

    print(f"📋 Target URLs: {urls}")

    # 5. Trigger Indexing API
    service = get_indexing_service(service_account_file)
    if not service:
        return

    for url in urls:
        try:
            body = {
                "url": url,
                "type": "URL_UPDATED"
            }
            service.urlNotifications().publish(body=body).execute()
            print(f"✅ Success: Submitted {url} to Google Indexing API.")
        except Exception as e:
            print(f"❌ Error submitting {url}: {e}")

if __name__ == "__main__":
    trigger_indexing()
