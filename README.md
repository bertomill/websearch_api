# Website Design Analyzer API

This API analyzes company websites to extract design elements, take screenshots, and generate design insights using OpenAI's GPT-4.

## Features

- Website content analysis
- Design element extraction (colors, fonts, layout)
- Screenshot capture (full page, viewport, main content)
- AI-powered design analysis and prompt generation
- Company insights generation

## Local Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd websearch_api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your OpenAI API key to the `.env` file

5. Run the API:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /
Health check endpoint

### POST /analyze
Analyze a company website

Request body:
```json
{
  "url": "https://example.com",
  "analysis_type": "general"  // optional
}
```

Response:
```json
{
  "url": "https://example.com",
  "analysis": "Detailed analysis of the website...",
  "styles": {
    "colors": ["#000000", "#ffffff"],
    "fonts": ["Arial", "Helvetica"],
    "layout": {
      "main_width": 1200,
      "main_height": 800
    }
  },
  "screenshots": [
    {
      "type": "full_page",
      "data": "base64_encoded_image"
    }
  ]
}
```

## Deployment to Render

1. Push your code to GitHub

2. Create a new Web Service on Render:
   - Connect your GitHub repository
   - Set the following:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python main.py`
     - Environment Variables:
       - `OPENAI_API_KEY`: Your OpenAI API key

3. Deploy!

## Development

The project uses:
- FastAPI for the web framework
- Selenium for web scraping and screenshots
- BeautifulSoup4 for HTML parsing
- OpenAI's GPT-4 for analysis
- ChromeDriver for browser automation

## License

MIT License 