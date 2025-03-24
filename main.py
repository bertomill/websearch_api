from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from openai import OpenAI
import time
import platform
import json
import base64
from datetime import datetime
import re
import logging
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Website Design Analyzer API",
    description="API for analyzing website designs and generating insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Configure OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"  # Explicitly set the base URL
)

class WebsiteRequest(BaseModel):
    url: HttpUrl
    analysis_type: Optional[str] = "general"

def extract_styles(driver, soup):
    """Extract styling information from the website"""
    try:
        styles = {
            "colors": set(),
            "fonts": set(),
            "layout": {},
            "components": []
        }
        
        # Extract colors from CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:
                # Extract hex colors
                hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', style.string)
                styles["colors"].update(hex_colors)
                
                # Extract font families
                font_families = re.findall(r'font-family:\s*([^;]+)', style.string)
                styles["fonts"].update(font_families)
        
        # Extract inline styles
        for element in soup.find_all(style=True):
            style_attr = element.get('style', '')
            hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', style_attr)
            styles["colors"].update(hex_colors)
            
            font_families = re.findall(r'font-family:\s*([^;]+)', style_attr)
            styles["fonts"].update(font_families)
        
        # Extract layout information
        try:
            main_content = driver.find_element(By.TAG_NAME, "main")
            styles["layout"]["main_width"] = main_content.size["width"]
            styles["layout"]["main_height"] = main_content.size["height"]
        except:
            pass
        
        # Convert sets to lists for JSON serialization
        styles["colors"] = list(styles["colors"])
        styles["fonts"] = list(styles["fonts"])
        
        return styles
    except Exception as e:
        logger.error(f"Error extracting styles: {str(e)}")
        return {"colors": [], "fonts": [], "layout": {}, "components": []}

def take_screenshots(driver, url):
    """Take screenshots of different parts of the website"""
    screenshots = []
    
    try:
        # Take full page screenshot
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        screenshot = driver.get_screenshot_as_base64()
        screenshots.append({
            "type": "full_page",
            "data": screenshot
        })
        
        # Take viewport screenshot
        driver.set_window_size(1920, 1080)
        screenshot = driver.get_screenshot_as_base64()
        screenshots.append({
            "type": "viewport",
            "data": screenshot
        })
        
        # Take screenshot of main content if available
        try:
            main_content = driver.find_element(By.TAG_NAME, "main")
            screenshot = main_content.screenshot_as_base64
            screenshots.append({
                "type": "main_content",
                "data": screenshot
            })
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error taking screenshots: {str(e)}")
    
    return screenshots

def setup_selenium():
    """Set up Selenium WebDriver with appropriate options"""
    options = webdriver.ChromeOptions()
    
    # Add arguments for headless operation and DNS configuration
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--disable-features=NetworkService')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    service = Service()
    
    try:
        driver = webdriver.Chrome(
            service=service,
            options=options
        )
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        logger.error(f"Error setting up ChromeDriver: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze")
async def analyze_website(request: WebsiteRequest):
    """
    Analyze a company website using Selenium and OpenAI
    """
    driver = None
    try:
        # Initialize Selenium
        driver = setup_selenium()
        logger.info("ChromeDriver initialized successfully")
        
        # Navigate to the website with timeout
        logger.info(f"Navigating to {request.url}")
        driver.get(str(request.url))
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get page content
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text()
        logger.info("Content extracted successfully")
        
        # Extract styles
        styles = extract_styles(driver, soup)
        logger.info("Styles extracted successfully")
        
        # Take screenshots
        screenshots = take_screenshots(driver, str(request.url))
        logger.info("Screenshots taken successfully")
        
        # Analyze content with OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a business analyst and web design expert. Analyze the following website content, styles, and provide insights about the company and its design approach."},
                {"role": "user", "content": f"""
                Please analyze this website and provide:
                1. Company insights
                2. Design analysis including:
                   - Color scheme analysis
                   - Typography analysis
                   - Layout analysis
                   - Design patterns used
                3. A design prompt that could be used to recreate a similar design
                
                Website content: {text_content[:4000]}
                Styles: {json.dumps(styles)}
                """}
            ]
        )
        
        return {
            "url": str(request.url),
            "analysis": response.choices[0].message.content,
            "styles": styles,
            "screenshots": screenshots,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TimeoutException:
        logger.error("Timeout while loading website")
        raise HTTPException(status_code=408, detail="Timeout while loading website")
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to access website: {str(e)}")
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 