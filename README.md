# Website Design Analyzer API

This API analyzes websites and provides insights about their design, content, and structure.

## Features

- Website content analysis
- Design pattern detection
- Color scheme analysis
- Typography analysis
- Layout analysis
- Screenshot generation
- Company insights
- Web search integration for up-to-date information

## How to Use

### Prerequisites

- Python 3.7+
- FastAPI
- Selenium
- OpenAI API key

### Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key
```

### Running the API

```bash
python main.py
```

The API will start running on `http://localhost:8000`

### Example Usage

Here's a simple example of how to use the API:

```python
import requests
import json

def analyze_website(url, enable_web_search=False, search_context_size="medium"):
    # API endpoint
    api_url = "http://localhost:8000/analyze"
    
    # Request payload
    payload = {
        "url": url,
        "analysis_type": "general",  # optional
        "enable_web_search": enable_web_search,
        "search_context_size": search_context_size
    }
    
    # Make the request
    response = requests.post(api_url, json=payload)
    
    # Check if request was successful
    if response.status_code == 200:
        result = response.json()
        
        # Print the analysis
        print("Analysis Results:")
        print("----------------")
        print(f"URL: {result['url']}")
        print(f"Analysis: {result['analysis']}")
        print(f"Colors used: {result['styles']['colors']}")
        print(f"Fonts used: {result['styles']['fonts']}")
        print(f"Timestamp: {result['timestamp']}")
        
        # Print citations if available
        if "citations" in result:
            print("\nWeb Search Citations:")
            for citation in result["citations"]:
                print(f"- {citation['title']}: {citation['url']}")
        
        # Save screenshots if needed
        for screenshot in result['screenshots']:
            print(f"Screenshot type: {screenshot['type']}")
            # You can save the base64 image data if needed
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Example usage
analyze_website("https://www.example.com")

# Example usage with web search
analyze_website("https://www.example.com", enable_web_search=True, search_context_size="high")
```

### API Response Structure

The API returns a JSON object with the following structure:

```json
{
    "url": "https://www.example.com",
    "analysis": "Detailed analysis of the website...",
    "styles": {
        "colors": ["#000000", "#ffffff", ...],
        "fonts": ["Arial", "Helvetica", ...],
        "layout": {
            "main_width": 1200,
            "main_height": 800
        },
        "components": []
    },
    "screenshots": [
        {
            "type": "full_page",
            "data": "base64_encoded_image_data"
        },
        {
            "type": "viewport",
            "data": "base64_encoded_image_data"
        }
    ],
    "citations": [
        {
            "url": "https://source.com/article",
            "title": "Source Article Title",
            "start_index": 120,
            "end_index": 145
        }
    ],
    "timestamp": "2024-03-21T12:00:00.000Z"
}
```

## API Endpoints

- `POST /analyze`: Main endpoint for website analysis
  - Parameters:
    - `url` (required): The website URL to analyze
    - `analysis_type` (optional): Type of analysis to perform
    - `enable_web_search` (optional): Set to true to use web search for enhanced analysis
    - `search_context_size` (optional): Web search context size (low, medium, high)
    - `user_location` (optional): User location for location-specific search results
- `GET /`: Health check endpoint
- `GET /health`: Alternative health check endpoint

## Web Search Integration

The API includes web search functionality powered by OpenAI's web search tools. This enhances the analysis with the latest information about the websites being analyzed.

### Web Search Features

- Up-to-date company information
- Current market trends affecting the website's industry
- Recent design pattern recognition
- Enhanced content analysis with citation links

### Web Search Parameters

- `enable_web_search`: Boolean flag to enable/disable web search (default: false)
- `search_context_size`: Amount of context for the search (options: "low", "medium", "high", default: "medium")
- `user_location`: Geographic context for location-specific search results
  ```json
  {
    "country": "US",  // Two-letter ISO country code
    "city": "San Francisco",  // Free text
    "region": "California",  // Free text
    "timezone": "America/Los_Angeles"  // IANA timezone
  }
  ```

## Error Handling

The API includes proper error handling for:
- Invalid URLs
- Timeout issues
- Website access problems
- Analysis failures

## Notes

- Make sure the API server is running before making requests
- The API requires an active internet connection
- Some websites may block automated access
- Processing time may vary depending on the website size and complexity

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

## Deployment

### Deploying to Render

1. Create a new Web Service on Render
2. Connect your repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:10000`
   - Python Version: 3.9 or higher

Make sure your `requirements.txt` includes:
```
fastapi
uvicorn
gunicorn
```

The service will be automatically deployed and available at your Render URL.

## Development

The project uses:
- FastAPI for the web framework
- Selenium for web scraping and screenshots
- BeautifulSoup4 for HTML parsing
- OpenAI's GPT-4 for analysis
- ChromeDriver for browser automation

## License

MIT License 