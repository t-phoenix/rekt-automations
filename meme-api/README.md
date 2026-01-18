# Meme Generation API

Fast and powerful API for generating viral meme text using AI. Built with FastAPI and powered by Google Gemini.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
cd meme-api
python3 -m venv venv
(rm -rf venv) ## To remove virtual environment
lsof -ti:8001 | xargs kill ## To kill process running on port 8001
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. **Run the server:**
```bash
python app.py
# Or with uvicorn directly:
uvicorn app:app --reload --port 8001
```

4. **Test the API:**
```bash
# Visit the interactive docs
open http://localhost:8001/docs

# Or test with curl
curl -X POST http://localhost:8001/api/meme/generate \
  -F "topic=When you finally understand DeFi" \
  -F "template_image=@path/to/template.jpg"
```

## 📡 API Endpoints

### `POST /api/meme/generate`
Generate top 3 meme text options from topic and template image.

> [!IMPORTANT]
> **Rate Limited**: 1 request per 2 minutes per IP address

**Request:**
- `topic` (string, **required**): Topic text or full Twitter post
- `is_twitter_post` (boolean, optional): True if input is a full Twitter post, False if short topic (default: false)
- `tone` (string, optional): Tone (edgy, professional, casual)
- `humor_type` (string, optional): Humor type (sarcastic, witty, ironic)
- `template_image` (file, **required**): Meme template image (JPEG, PNG, WebP)

**Response:**
Returns **top 3 ranked options** with detailed scoring:
```json
{
  "options": [
    {
      "top_text": "WHEN YOU FINALLY",
      "bottom_text": "UNDERSTAND DEFI",
      "ranking_score": 0.89,
      "virality_score": 0.85,
      "image_coherence_score": 0.92,
      "text_alignment_score": 0.87,
      "humor_pattern_used": "triumphant_flex"
    },
    {
      "top_text": "ME EXPLAINING DEFI",
      "bottom_text": "TO MY CAT",
      "ranking_score": 0.84,
      "virality_score": 0.80,
      "image_coherence_score": 0.88,
      "text_alignment_score": 0.82,
      "humor_pattern_used": "absurdist"
    },
    {
      "top_text": "DEFI BE LIKE",
      "bottom_text": "IT'S COMPLICATED",
      "ranking_score": 0.81,
      "virality_score": 0.78,
      "image_coherence_score": 0.85,
      "text_alignment_score": 0.79,
      "humor_pattern_used": "relatable_struggle"
    }
  ],
  "metadata": {
    "dominant_emotion": "confidence",
    "humor_type": "witty",
    "meme_format": "top_bottom_classic",
    "total_options_considered": 10,
    "weighting": "60% text input, 40% image coherence"
  }
}
```

**How Selection Works:**
- **Node 3**: Generates 10 diverse options with different humor patterns
- **Node 4**: Ranks using 60/40 weighting (60% text input alignment, 40% image coherence)
- Returns top 3 best-ranked options

---

### `GET /api/meme/health`
Health check endpoint.


## 🌐 Deployment

### Render.com (Recommended)

1. **Connect your repository** to Render
2. **Create a new Web Service**
3. **Use the following settings:**
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
4. **Set environment variables:**
   - `GOOGLE_API_KEY`: Your Google AI API key
   - `CORS_ORIGINS`: Your frontend URL
5. **Deploy!**

Alternatively, use the included `render.yaml` for automated deployment.

### Docker

```bash
# Build
docker build -t meme-api .

# Run
docker run -p 8001:8001 \
  -e GOOGLE_API_KEY=your_key \
  -e CORS_ORIGINS=http://localhost:3000 \
  meme-api
```

## 🔧 Configuration

All configuration is done via environment variables. See `.env.example` for full list.

**Key variables:**
- `GOOGLE_API_KEY` or `OPENAI_API_KEY` - At least one required
- `CORS_ORIGINS` - Comma-separated list of allowed frontend URLs
- `MAX_FILE_SIZE_MB` - Maximum upload file size (default: 10MB)

**Rate Limiting:**
- **Meme Text Generation** (`/api/meme/generate`): 1 request per 2 minutes per IP
- Rate limit errors return HTTP 429 (Too Many Requests)
- Uses `slowapi` for IP-based rate limiting


## 🧪 Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

## 🔗 Frontend Integration

### JavaScript/TypeScript Example

```typescript
async function generateMeme(topic: string, templateFile: File) {
  const formData = new FormData();
  formData.append('topic', topic);
  formData.append('template_image', templateFile);
  
  const response = await fetch('https://your-api.onrender.com/api/meme/generate', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  // Returns top 3 options
  return data.options.map(option => ({
    topText: option.top_text,
    bottomText: option.bottom_text,
    rankingScore: option.ranking_score
  }));
}
```

### React Example

```typescript
import { useState } from 'react';

function MemeGenerator() {
  const [options, setOptions] = useState([]);
  
  const handleGenerate = async (topic: string, image: File) => {
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('template_image', image);
    
    const res = await fetch(`${API_URL}/api/meme/generate`, {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    setOptions(data.options); // Array of 3 options
  };
  
  return (
    // Your UI here - render all 3 options
  );
}
```
Generate AI-branded meme template by intelligently blending brand elements.

> [!IMPORTANT]
> **Rate Limited**: 1 request per 3 minutes per IP address (AI image generation costs)

**Request:**
- `template_image` (file, **required**): Meme template image (JPEG, PNG, WebP)
- `brand_name` (string, **required**): Brand name (1-50 characters)
- `primary_color` (string, **required**): Primary brand color in hex format (e.g., `#00D4FF`)
- `user_prompt` (string, **required**): How to blend brand (10-500 characters, e.g., "make character wear branded hoodie")
- `secondary_color` (string, optional): Secondary brand color in hex format
- `logo_image` (file, optional): Brand logo image

**Response:**
```json
{
  "branded_template_base64": "iVBORw0KGgoAAAANSUhEUgA...",
  "metadata": {
    "original_size": {"width": 800, "height": 600},
    "ai_strategy": "smart_integration",
    "recommended_integration": "apparel_branding",
    "refined_prompt": "Place MyCrypto logo on character's hoodie chest area, matching #00D4FF blue color",
    "user_prompt": "make character wear branded hoodie",
    "brand_colors": {
      "primary": "#00D4FF",
      "secondary": "#FF006E"
    },
    "processing_time_ms": 8234,
    "note": "Entire canvas available for meme text - branding is blended into image"
  }
}
```

**AI Workflow:**
1. **Image Analysis**: Vision LLM analyzes template and identifies placement opportunities (characters, objects, background)
2. **Prompt Refinement**: Text LLM improves user's prompt for better AI generation (considers text overlay compatibility)
3. **Image Editing**: OpenAI DALL-E 2 edits the image to integrate branding naturally

**Example cURL:**
```bash
curl -X POST http://localhost:8001/api/meme/template/brand \
  -F "template_image=@meme_template.jpg" \
  -F "brand_name=MyCrypto" \
  -F "primary_color=#00D4FF" \
  -F "secondary_color=#FF006E" \
  -F "user_prompt=make the character wear a blue hoodie with the brand logo" \
  -F "logo_image=@logo.png"
```

---

### `GET /api/meme/templates`
List available meme templates.

### `GET /api/meme/health`
Health check endpoint.


## 🌐 Deployment

### Render.com (Recommended)

1. **Connect your repository** to Render
2. **Create a new Web Service**
3. **Use the following settings:**
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
4. **Set environment variables:**
   - `GOOGLE_API_KEY`: Your Google AI API key
   - `CORS_ORIGINS`: Your frontend URL
5. **Deploy!**

Alternatively, use the included `render.yaml` for automated deployment.

### Docker

```bash
# Build
docker build -t meme-api .

# Run
docker run -p 8001:8001 \
  -e GOOGLE_API_KEY=your_key \
  -e CORS_ORIGINS=http://localhost:3000 \
  meme-api
```

## 🔧 Configuration

All configuration is done via environment variables. See `.env.example` for full list.

**Key variables:**
- `GOOGLE_API_KEY` or `OPENAI_API_KEY` - At least one required
- `CORS_ORIGINS` - Comma-separated list of allowed frontend URLs
- `MAX_FILE_SIZE_MB` - Maximum upload file size (default: 10MB)

**Rate Limiting:**
- **Meme Text Generation** (`/api/meme/generate`): 1 request per 2 minutes per IP
- **Branded Templates** (`/api/meme/template/brand`): 1 request per 3 minutes per IP (AI generation costs)
- Rate limit errors return HTTP 429 (Too Many Requests)
- Uses `slowapi` for IP-based rate limiting


## 🧪 Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

## 🔗 Frontend Integration

### JavaScript/TypeScript Example

```typescript
async function generateMeme(topic: string, templateFile: File) {
  const formData = new FormData();
  formData.append('topic', topic);
  formData.append('template_image', templateFile);
  
  const response = await fetch('https://your-api.onrender.com/api/meme/generate', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  // Returns top 3 options
  return data.options.map(option => ({
    topText: option.top_text,
    bottomText: option.bottom_text,
    rankingScore: option.ranking_score
  }));
}
```

### React Example

```typescript
import { useState } from 'react';

function MemeGenerator() {
  const [options, setOptions] = useState([]);
  
  const handleGenerate = async (topic: string, image: File) => {
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('template_image', image);
    
    const res = await fetch(`${API_URL}/api/meme/generate`, {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    setOptions(data.options); // Array of 3 options
  };
  
  return (
    // Your UI here - render all 3 options
  );
}
```

### Branded Template Example

```typescript
async function generateBrandedTemplate(
  templateFile: File,
  brandName: string,
  primaryColor: string,
  userPrompt: string,
  logoFile?: File
) {
  const formData = new FormData();
  formData.append('template_image', templateFile);
  formData.append('brand_name', brandName);
  formData.append('primary_color', primaryColor);
  formData.append('user_prompt', userPrompt);
  if (logoFile) {
    formData.append('logo_image', logoFile);
  }
  
  const response = await fetch(`${API_URL}/api/meme/template/brand`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  // Returns base64 encoded branded template
  return {
    imageBase64: data.branded_template_base64,
    aiStrategy: data.metadata.ai_strategy,
    processingTime: data.metadata.processing_time_ms
  };
}
```


## 📚 Documentation

- **Interactive API Docs**: `/docs` (Swagger UI)
- **Alternative Docs**: `/redoc` (ReDoc)
- **Detailed API Reference**: See `API.md`

## 🛠️ Architecture

The API wraps the LangGraph meme generation workflow:

1. **Node 1: Sentiment Analysis** - Analyzes user's topic/tweet for emotion and meme angle
2. **Node 2: Template Image Analysis** - Analyzes the template image for visual context
3. **Node 3: Text Generation** - Generates 10 diverse meme text options (NO brand context)
4. **Node 4: Text Selection** - Ranks options using 60/40 weighting and selects top 3

**Key Features:**
- Pure focus on user input + image (no brand hallucination)
- 10 different humor patterns for maximum variety
- Intelligent ranking with transparent scoring

## 📝 License

MIT

## 🙏 Credits

Built on top of the `content-meme-automation` LangGraph workflow.
