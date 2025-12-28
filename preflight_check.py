import json
import os
import sys

def preflight_check():
    config_path = 'dist/global_tax_config.json'
    
    # Check if file exists
    if not os.path.exists(config_path):
        print(f"❌ Error: {config_path} not found. Run scraper.py first.")
        sys.exit(1)
        
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error: Failed to parse JSON: {e}")
        sys.exit(1)

    required_countries = ['united_kingdom', 'united_states', 'australia', 'canada']
    
    # 1. Check if all countries exist
    for country in required_countries:
        if country not in data:
            print(f"❌ Error: Missing required country data for '{country}'.")
            sys.exit(1)

    # 2. Validation Rules
    for country, config in data.items():
        # Check Personal Allowance / Basic Thresholds
        if country == 'united_kingdom':
            pa = config.get('income_tax', {}).get('personal_allowance')
            if not pa or pa <= 0:
                print(f"❌ Error: Invalid Personal Allowance for UK: {pa}")
                sys.exit(1)
        
        # Check Tax Bands and Rates
        bands = []
        if 'income_tax' in config:
            if 'bands' in config['income_tax']:
                bands = config['income_tax']['bands']
            elif 'federal_bands' in config['income_tax']:
                bands = config['income_tax']['federal_bands']
                
        if not bands:
            print(f"❌ Error: No tax bands found for {country}.")
            sys.exit(1)

        for band in bands:
            rate = band.get('rate')
            if rate is None or not (0.0 <= rate <= 0.6):
                print(f"❌ Error: Out of range tax rate for {country}: {rate}")
                sys.exit(1)

        # Check Social Security
        ss_rate = config.get('social_security', {}).get('rate')
        ss_rates = config.get('social_security', {}).get('rates')
        
        if not ss_rate and not ss_rates:
            # Some countries might have complex lists, but at least one should exist
            print(f"❌ Error: Missing Social Security info for {country}.")
            sys.exit(1)

    print("✅ Data Integrity Verified. Ready for Deployment.")
    sys.exit(0)

if __name__ == "__main__":
    preflight_check()
