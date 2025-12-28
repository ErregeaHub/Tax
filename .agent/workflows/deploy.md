---
description: how to update tax data and deploy the application
---

# Global Tax Calculator Update Workflow

Follow these steps to ensure the calculator is using the most recent 2025/2026 tax data and is ready for production.

### 1. Update Scraper Dependencies
// turbo
```bash
pip install playwright beautifulsoup4 --break-system-packages && playwright install chromium
```

### 2. Execute Data Scraping
Run the modular scraper to fetch latest rates for UK, USA, AU, and CA.
// turbo
```bash
python3 scraper.py
```

### 3. Verify Data Quality
Open `global_tax_config.json` and ensure:
- `effective_year` is correct (e.g., 2025).
- No null rates or missing thresholds.

### 4. Sync index.html (Manual Step)
Ensure the `CONFIG` object in `index.html` matches the logic/values in `global_tax_config.json`. 
> [!NOTE]
> Future versions may automate this injection via a build script.

### 5. Local Build & Test
// turbo
```bash
npm run dev
```
Open `http://localhost:5173` and test:
- Country switching.
- Calculation accuracy for high, medium, and low incomes.
- Chart rendering.

### 6. Production Deployment
Build the optimized bundle:
// turbo
```bash
npm run build
```
Upload the `dist/` folder or the single `index.html` to your hosting provider.
