
# Web Scraping Project: El País Opinion Section

This project demonstrates web scraping, API integration, text processing, and cross-browser testing skills. The script fetches articles from the "Opinión" section of **El País**, extracts article titles, content, images, translates titles to English using RapidAPI, analyzes repeated words, and performs cross-browser parallel testing using **BrowserStack**.

---

## 🚀 Features

- **Web Scraping** using Selenium (Python)
- **Translation API Integration** (RapidAPI)
- **Text Analysis** for repeated words
- **Cross-Browser Parallel Testing** (BrowserStack)
- **Headless browser support** for automated scraping
- Automatic **image downloading** and storing locally

---

## ✅ Requirements

- Python 3.x
- Chrome browser (for local scraping)
- A **RapidAPI Key** for translations ([Rapid Translate Multi Traduction API](https://rapidapi.com/))
- **BrowserStack Account** for parallel testing ([BrowserStack](https://www.browserstack.com/))

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/web-scraping.git
cd web-scraping

```

### 2. Set up a virtual environment

Using a virtual environment is recommended:

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate

```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Install dependencies

```bash
pip install -r requirements.txt

```

### 4. Configure environment variables (`.env` file)

Create a `.env` file in your project root:

```bash
RAPIDAPI_KEY=your-rapidapi-key
RAPIDAPI_HOST=rapid-translate-multi-traduction.p.rapidapi.com
BROWSERSTACK_USERNAME=your-browserstack-username
BROWSERSTACK_ACCESS_KEY=your-browserstack-access-key

```

Replace placeholders with your actual credentials.

---

## 🛠️ Running the Program

### 🔸 Scraping and Translation (Locally)

Run the main scraping script:

```bash
python scraper.py

```

**Output includes:**

- Titles of articles (Spanish)
- Snippets of article content
- Translated titles (English)
- Analysis of repeated words across translated titles
- Images saved in `images/` folder

---

### 🌐 Cross-Browser Testing (BrowserStack)

Run cross-browser tests using BrowserStack parallel threads:

```bash
python browsersack_test.py

```

**This script performs parallel scraping tests across:**

| Device Type | Browser | OS/Device |
| --- | --- | --- |
| Desktop | Chrome | Windows 10 |
| Desktop | Firefox | macOS Monterey |
| Mobile | Safari | iPhone 13 (iOS 15) |
| Mobile | Chrome | Samsung Galaxy S22 (Android 12) |
| Tablet | Safari | iPad Pro 12.9" (iOS 15) |

---

## 🗂️ Project Structure

```
web-scraping/
│
├── images/                     # Saved article images
├── scraper.py                  # Main scraping script
├── browsersack_test.py         # BrowserStack parallel testing script
├── .env                        # Environment variables (API keys)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation (this file)
└── .gitignore                  # Git ignore rules

```

---

## 📌 Dependencies

Your `requirements.txt` should include at minimum:

```
nginx
CopyEdit
selenium
webdriver-manager
beautifulsoup4
python-dotenv
requests

```

---

## 🧑‍💻 Notes & Troubleshooting

- Ensure your BrowserStack credentials have appropriate permissions.
- Ensure RapidAPI quotas and limits are sufficient for your usage.
- BrowserStack tests can fail if your internet connection is unstable.