# Project Structure & Workflow: Global Tax Engine

This document outlines the architecture, automated data pipeline, and deployment-ready distribution of the Global Tax Engine.

## 📂 Project Structure

```text
automation/
├── .agent/              # AI Agent configuration and workflows
│   └── workflows/       # Specialized automation steps
├── brain/               # Project memory and documentation artifacts (v3)
├── dist/                # 📦 PRODUCTION ROOT (Deployment Folder)
│   ├── index.html       # 🚀 Main App (SEO Optimized + JSON-LD + Hreflang)
│   ├── privacy-policy.html # ⚖️ Legal Compliance (AdSense Ready)
│   ├── terms-of-service.html # ⚖️ Legal Compliance (AdSense Ready)
│   ├── global_tax_config.json # 📊 Verified Tax Data Source
│   ├── sitemap.xml          # 🗺️ SEO Sitemap
│   ├── robots.txt           # 🤖 Crawl Instructions
│   └── ads.txt              # 💰 AdSense Authorization
├── public/              # Static assets (Vite)
├── src/                 # Development source (Vite structure)
├── scraper.py           # 🕷️ Live Tax Scraper & Data Generator
├── preflight_check.py   # 🛡️ Data Integrity Guardrail
├── indexer.py           # 🚀 Google Indexing API Automation
├── package.json         # Build & Script configuration
├── STRUCTURE.md         # 📘 This document
└── .gitignore           # Root protection rules
```

---

## ✨ Core Features

### 🌍 Global Tax & Currency
- **Multi-Country Logic**: Precision 2025/26 tax logic for **UK, USA, AU, and CA**.
- **Live Currency Converter**: Real-time rates via **Frankfurter API**.
- **Dynamic Localization**: Automagically updates terminology and tax guides per region.

### 🛡️ Technical SEO (Senior Level)
- **Indexing Automation**: Integrated `indexer.py` for instant Google Search updates via API.
- **Multi-Region Targeting**: Implemented **hreflang** and dynamic **canonical** tags for global SEO equity.
- **Crawl Optimization**: Optimized `robots.txt` and `sitemap.xml` for maximum indexing efficiency.
- **Compliance Engine**: Built-in Privacy Policy and Terms of Service for Google AdSense approval.
- **AdSense Ready**: Verified `ads.txt` structure for rapid monetization.
- **JSON-LD Schema**: Integrated `SoftwareApplication` and `FAQPage` for rich search results.

### 💎 Premium Interface
- **Custom UI Components**: Glassmorphism dropdowns, high-contrast Dark Mode, and clean inputs (no spinners).
- **Interactive Visuals**: Animated doughnut charts powered by **Chart.js**.

---

## 🔄 Development Workflow

### 1. Data Refresh & Verification
To update tax rates and ensure production stability:
```bash
python3 scraper.py
python3 preflight_check.py
```

### 2. Search Indexing (Optional)
If you have a `service_account.json` configured, notify Google of the updates:
```bash
python3 indexer.py
# Use --force to index regardless of date
python3 indexer.py --force
```
> [!IMPORTANT]
> **Fixing 403 Forbidden Error:** 
> If you see "Permission denied. Failed to verify the URL ownership", you must:
> 1. Open your `service_account.json` and copy the `client_email`.
> 2. Go to **Google Search Console** > **Settings** > **Users and Permissions**.
> 3. Click **Add User** and paste the email.
> 4. Set the Permission to **Owner**.

### 3. Frontend Preview
To run the production-ready frontend locally:
```bash
npm run dev
```

---

## 🛠 Tech Stack
- **Frontend**: HTML5, Tailwind CSS (V4), JavaScript (ES6+).
- **APIs**: Frankfurter API, Google Indexing API.
- **Data Pipeline**: Python async Playwright, BeautifulSoup4.
- **Validation**: Strict Integrity Testing via `preflight_check.py`.

---

## 📋 Maintenance Checklist
- [ ] **Verify UK Brackets**: Check GOV.UK regularly.
- [ ] **Scraper Health**: Ensure official tax portals haven't changed HTML structures.
- [ ] **Preflight Success**: Never deploy if `preflight_check.py` fails.
- [ ] **Technical SEO**: Audit Search Console for hreflang errors.
