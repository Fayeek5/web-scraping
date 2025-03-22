# Web Scraping Project: El País Opinion Section

This project is a web scraping script that fetches articles from the "Opinión" section of **El País** (a Spanish news website). It extracts article titles, content, images, translates the titles to English, and analyzes repeated words.

## Requirements

- Python 3.x
- Internet connection
- A browser (Google Chrome) installed
- A **RapidAPI Key** for translation API access

## Installation

### 1. Clone the repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/web-scraping.git
cd web-scraping

```

### 2. Set up a virtual environment

It's recommended to use a virtual environment to manage dependencies.

### For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate

```

### For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Install required dependencies

Install the necessary Python packages:

```bash
pip install -r requirements.txt

```

### 4. Set up **.env** file

Create a `.env` file in the root directory and add the following variables:

```
RAPIDAPI_KEY=your-rapidapi-key
RAPIDAPI_HOST=rapid-translate-multi-traduction.p.rapidapi.com

```

Replace `your-rapidapi-key` with your actual RapidAPI key.

### 5. Install **WebDriverManager** (Optional)

You no longer need to manually download and install **ChromeDriver**. The program now uses **WebDriverManager**, which automatically handles downloading and managing ChromeDriver for you.

To install **WebDriverManager**, run the following:

```bash
pip install webdriver-manager

```

---

## Running the Program

### 1. Start the Program

To start the program, simply run the following command:

```bash
python scraper.py

```

This will begin scraping articles from **El País** and save the images to the `images` directory.

### 2. Output

The program will:

- Print the scraped article titles (in Spanish).
- Display a snippet of the article content.
- Save the images associated with each article in the `images` folder.
- Translate article titles from Spanish to English.
- Print any repeated words across the translated titles.

If no repeated words are found, the program will print: `No Repeated Words`.

---

## Project Structure

```
plaintext
Copy
web-scraping/
│
├── images/                # Folder to save article images
├── scraper.py             # Main Python script to run the scraping
├── .env                   # Environment file to store API keys
├── requirements.txt       # List of required Python packages
├── README.md              # Project documentation (this file)
├── .gitignore             # Git ignore file
└── image.png              # Image for directory reference (optional)

```
