# Frontend Integration Guide

## API Integration

### Base URL
```
https://your-render-url.onrender.com
```

### Endpoints

#### 1. Analyze Website
```typescript
POST /analyze

// Request Body
{
  "url": string,          // The website URL to analyze
  "analysis_type"?: string, // Optional: "general" by default
  "enable_web_search"?: boolean, // Optional: enables web search for up-to-date info
  "search_context_size"?: string, // Optional: "low", "medium", or "high"
  "user_location"?: {     // Optional: location for better search results
    "country"?: string,   // Two-letter ISO country code
    "city"?: string,      // City name
    "region"?: string,    // Region/state name
    "timezone"?: string   // IANA timezone
  }
}

// Response Structure
{
  "url": string,
  "analysis": string,     // AI-generated analysis
  "styles": {
    "colors": string[],   // Array of hex colors
    "fonts": string[],    // Array of font families
    "layout": {
      "main_width": number,
      "main_height": number,
      "components": any[]
    }
  },
  "screenshots": [
    {
      "type": string,     // "full_page" or "viewport"
      "data": string      // base64 encoded image
    }
  ],
  "citations": [          // Only present when web_search is enabled
    {
      "url": string,      // Source URL
      "title": string,    // Source title
      "start_index": number, // Start position in analysis text
      "end_index": number    // End position in analysis text
    }
  ],
  "timestamp": string     // ISO timestamp
}
```

### Example Integration

```typescript
// Example using fetch with web search
async function analyzeWebsiteWithSearch(url: string, enableSearch: boolean = false) {
  try {
    const response = await fetch('https://your-render-url.onrender.com/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url,
        enable_web_search: enableSearch,
        search_context_size: "medium",
        user_location: {
          country: "US",
          city: "San Francisco",
          region: "California"
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

## Implementation Guidelines

### 1. Loading States
- Implement a loading indicator during analysis
- Analysis typically takes 5-15 seconds depending on the website
- Consider showing step-by-step progress:
  - "Analyzing website..."
  - "Capturing screenshots..."
  - "Generating insights..."

```typescript
// Example Loading State Management
const [isAnalyzing, setIsAnalyzing] = useState(false);
const [analysisStep, setAnalysisStep] = useState('');

async function handleAnalysis() {
  setIsAnalyzing(true);
  try {
    setAnalysisStep('Analyzing website...');
    const result = await analyzeWebsite(url);
    // Handle result
  } catch (error) {
    // Handle error
  } finally {
    setIsAnalyzing(false);
  }
}
```

### 2. Error Handling
Implement error handling for these scenarios:

```typescript
type APIError = {
  message: string;
  code: string;
  details?: any;
}

// Example error handling
function handleAPIError(error: APIError) {
  switch (error.code) {
    case 'INVALID_URL':
      return 'Please enter a valid website URL';
    case 'TIMEOUT':
      return 'Website took too long to respond';
    case 'ACCESS_DENIED':
      return 'Website blocked automated access';
    default:
      return 'An unexpected error occurred';
  }
}
```

### 3. Display Guidelines

#### Colors
- Display color swatches with hex values
- Consider showing color usage context
- Allow copying color codes

#### Fonts
- Show font previews
- Group by usage (headings, body, etc.)
- Link to font sources where available

#### Screenshots
- Implement image lazy loading
- Provide zoom/pan capabilities
- Consider a side-by-side comparison view

#### Citations
- Display citations as hyperlinks with superscript numbers
- Show citation source information in a reference section
- Allow clicking citations to navigate to the source

```typescript
// Example Citation Component
function CitationDisplay({ analysis, citations }) {
  // Create a map of citation positions
  const citationMap = citations.reduce((map, citation) => {
    map[citation.start_index] = citation;
    return map;
  }, {});
  
  // Split text and insert citation links
  let lastIndex = 0;
  const segments = [];
  let citationCounter = 1;
  
  Object.keys(citationMap).sort((a, b) => Number(a) - Number(b)).forEach(startIndex => {
    const citation = citationMap[startIndex];
    
    // Add text before citation
    segments.push(analysis.substring(lastIndex, citation.start_index));
    
    // Add citation superscript
    segments.push(
      <sup key={`citation-${citationCounter}`}>
        <a href={citation.url} target="_blank" rel="noopener noreferrer">
          [{citationCounter}]
        </a>
      </sup>
    );
    
    lastIndex = citation.end_index;
    citationCounter++;
  });
  
  // Add remaining text
  segments.push(analysis.substring(lastIndex));
  
  return (
    <div>
      {segments}
      {citations.length > 0 && (
        <div className="citations-section">
          <h3>References</h3>
          <ol>
            {citations.map((citation, index) => (
              <li key={`ref-${index + 1}`}>
                <a href={citation.url} target="_blank" rel="noopener noreferrer">
                  {citation.title}
                </a>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
```

### 4. Rate Limiting
- Implement request throttling
- Add retry logic with exponential backoff
- Cache results when possible

```typescript
// Example rate limiting
const rateLimiter = {
  lastRequest: 0,
  minInterval: 1000, // 1 second

  async throttle() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;
    
    if (timeSinceLastRequest < this.minInterval) {
      await new Promise(resolve => 
        setTimeout(resolve, this.minInterval - timeSinceLastRequest)
      );
    }
    
    this.lastRequest = Date.now();
  }
};
```

### 5. Performance Tips
- Use WebP format for screenshot display when supported
- Implement virtual scrolling for long analyses
- Cache analysis results locally
- Consider implementing a preview mode with reduced data

## Best Practices

1. **Progressive Enhancement**
   - Start with basic URL input
   - Add features based on API response
   - Fallback gracefully when features aren't available

2. **Accessibility**
   - Add ARIA labels for dynamic content
   - Ensure keyboard navigation
   - Provide text alternatives for visual elements

3. **Mobile Considerations**
   - Optimize screenshot display for mobile
   - Implement touch-friendly controls
   - Consider reduced data mode for mobile

4. **User Experience**
   - Show immediate feedback on user actions
   - Provide clear error messages
   - Include retry options for failed requests
   - Save analysis history if relevant

## Example UI Components

Here's a suggested component structure:

```typescript
interface AnalysisResult {
  url: string;
  analysis: string;
  styles: {
    colors: string[];
    fonts: string[];
    layout: any;
  };
  screenshots: Array<{
    type: string;
    data: string;
  }>;
  citations?: Array<{
    url: string;
    title: string;
    start_index: number;
    end_index: number;
  }>;
  timestamp: string;
}

function AnalysisDisplay({ result }: { result: AnalysisResult }) {
  return (
    <div className="analysis-container">
      <header>
        <h1>Analysis Results</h1>
        <p>Analyzed: {new Date(result.timestamp).toLocaleString()}</p>
      </header>

      <section className="color-palette">
        <h2>Color Scheme</h2>
        {result.styles.colors.map(color => (
          <ColorSwatch key={color} hex={color} />
        ))}
      </section>

      <section className="typography">
        <h2>Typography</h2>
        {result.styles.fonts.map(font => (
          <FontDisplay key={font} family={font} />
        ))}
      </section>

      <section className="screenshots">
        <h2>Screenshots</h2>
        {result.screenshots.map(screenshot => (
          <Screenshot 
            key={screenshot.type}
            type={screenshot.type}
            data={screenshot.data}
          />
        ))}
      </section>

      <section className="analysis">
        <h2>Design Analysis</h2>
        {result.citations ? 
          <CitationDisplay analysis={result.analysis} citations={result.citations} /> :
          <p>{result.analysis}</p>
        }
      </section>
      
      {/* Search toggle for re-analyzing with web search */}
      <div className="web-search-toggle">
        <label>
          <input 
            type="checkbox" 
            onChange={(e) => {
              // Re-fetch analysis with web search enabled/disabled
              // Implementation depends on your state management
            }} 
          />
          Enable web search for enhanced analysis
        </label>
        
        {/* Context size selector */}
        <select 
          onChange={(e) => {
            // Update context size for web search
            // Implementation depends on your state management
          }}
        >
          <option value="low">Low (Faster)</option>
          <option value="medium">Medium (Balanced)</option>
          <option value="high">High (More Comprehensive)</option>
        </select>
      </div>
    </div>
  );
}
```

## Web Search Feature Implementation

### 1. Toggle Control
Add a toggle in your UI to enable/disable web search:

```typescript
function WebSearchToggle({ enabled, onToggle }) {
  return (
    <div className="web-search-toggle">
      <label className="switch">
        <input 
          type="checkbox" 
          checked={enabled}
          onChange={() => onToggle(!enabled)} 
        />
        <span className="slider round"></span>
      </label>
      <span>Enable web search for latest information</span>
      
      {enabled && (
        <div className="search-options">
          <label>Search depth:</label>
          <select onChange={(e) => onContextSizeChange(e.target.value)}>
            <option value="low">Low - Faster results</option>
            <option value="medium" selected>Medium - Balanced</option>
            <option value="high">High - More comprehensive</option>
          </select>
        </div>
      )}
    </div>
  );
}
```

### 2. Handling Citations
When web search is enabled, the API may return citations. Implement a citation display component:

```typescript
function formatTextWithCitations(text, citations) {
  if (!citations || citations.length === 0) return text;
  
  let formattedText = text;
  let offset = 0;
  
  // Sort citations by their starting position
  const sortedCitations = [...citations].sort((a, b) => a.start_index - b.start_index);
  
  sortedCitations.forEach((citation, index) => {
    const superscript = `<sup class="citation">[${index + 1}]</sup>`;
    
    // Adjust indices based on previously added HTML
    const adjustedStartIndex = citation.start_index + offset;
    
    // Insert superscript at the end of the cited text
    formattedText = 
      formattedText.slice(0, adjustedStartIndex) + 
      superscript + 
      formattedText.slice(adjustedStartIndex);
    
    // Update offset for next citation
    offset += superscript.length;
  });
  
  return formattedText;
}
```

### 3. References Section
Add a section to display all the citation sources:

```typescript
function ReferencesSection({ citations }) {
  if (!citations || citations.length === 0) return null;
  
  return (
    <div className="references-section">
      <h3>References</h3>
      <ol>
        {citations.map((citation, index) => (
          <li key={`ref-${index}`}>
            <a 
              href={citation.url} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              {citation.title || citation.url}
            </a>
          </li>
        ))}
      </ol>
    </div>
  );
}
```

## Need Help?

If you encounter any issues or need clarification, please:
1. Check the API documentation
2. Test with the provided example code
3. Contact the API team for support

Remember to handle your API keys securely and never expose them in client-side code. 