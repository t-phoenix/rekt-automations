# Meme Generation API Reference

Complete API documentation for the Meme Generation service.

## Base URL

- **Local**: `http://localhost:8001`
- **Production**: `https://your-app.onrender.com`

## Authentication

Currently no authentication required. Consider adding API keys for production.

---

## Endpoints

### Generate Meme Text

Generate top and bottom text for a meme based on content or topic.

**Endpoint:** `POST /api/meme/generate`

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string | No* | Pre-written content text for the meme |
| `topic` | string | No* | Topic to generate meme content about |
| `tone` | string | No | Tone for generation (edgy, professional, casual) |
| `humor_type` | string | No | Humor type (sarcastic, witty, ironic, relatable) |
| `template_image` | file | No | Meme template image (JPEG, PNG, WebP) |

*At least one of `content` or `topic` must be provided.

**File Upload Limits:**
- Max size: 10MB (configurable)
- Formats: JPEG, PNG, WebP

**Example Request (curl):**

```bash
curl -X POST http://localhost:8001/api/meme/generate \
  -F "content=When you finally understand DeFi" \
  -F "tone=edgy" \
  -F "template_image=@stonks.jpg"
```

**Example Request (JavaScript):**

```javascript
const formData = new FormData();
formData.append('content', 'When you finally understand DeFi');
formData.append('template_image', fileInput.files[0]);

const response = await fetch('http://localhost:8001/api/meme/generate', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.top_text, data.bottom_text);
```

**Success Response (200 OK):**

```json
{
  "top_text": "WHEN YOU FINALLY",
  "bottom_text": "UNDERSTAND DEFI",
  "metadata": {
    "dominant_emotion": "confidence",
    "humor_type": "relatable",
    "virality_score": 0.85,
    "meme_format": "top_bottom_classic",
    "image_coherence_score": 0.92
  }
}
```

**Error Responses:**

```json
// 400 Bad Request - Missing required fields
{
  "detail": "Either 'content' or 'topic' must be provided"
}

// 400 Bad Request - Invalid file format
{
  "detail": "Invalid file format. Allowed: image/jpeg, image/png, image/webp"
}

// 400 Bad Request - File too large
{
  "detail": "File too large. Maximum size: 10MB"
}

// 500 Internal Server Error
{
  "detail": "Failed to generate meme text"
}
```

---

### List Templates

Get a list of available meme templates.

**Endpoint:** `GET /api/meme/templates`

**Example Request:**

```bash
curl http://localhost:8001/api/meme/templates
```

**Success Response (200 OK):**

```json
{
  "templates": [
    {
      "name": "stonks",
      "path": "/path/to/stonks.png",
      "category": "success_failure",
      "tags": ["success_failure"]
    },
    {
      "name": "drake",
      "path": "/path/to/drake.png",
      "category": "reaction_memes",
      "tags": ["reaction_memes"]
    }
  ],
  "total": 2
}
```

---

### Health Check

Check if the service is healthy and LLM is available.

**Endpoint:** `GET /api/meme/health`

**Example Request:**

```bash
curl http://localhost:8001/api/meme/health
```

**Success Response (200 OK):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_available": true
}
```

---

## Response Models

### MemeTextResponse

```typescript
interface MemeTextResponse {
  top_text: string;
  bottom_text: string;
  metadata?: MemeTextMetadata;
}
```

### MemeTextMetadata

```typescript
interface MemeTextMetadata {
  dominant_emotion?: string;
  humor_type?: string;
  virality_score?: number;      // 0-1
  meme_format?: string;
  image_coherence_score?: number;  // 0-1
}
```

### TemplateListResponse

```typescript
interface TemplateListResponse {
  templates: TemplateInfo[];
  total: number;
}

interface TemplateInfo {
  name: string;
  path: string;
  category?: string;
  tags?: string[];
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

**Common HTTP Status Codes:**

- `200` - Success
- `400` - Bad Request (validation error, missing fields)
- `422` - Unprocessable Entity (invalid data format)
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting. Consider implementing for production:

```python
# Example with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/meme/generate")
@limiter.limit("10/minute")
async def generate_meme(...):
    ...
```

---

## CORS Configuration

Configure allowed origins via `CORS_ORIGINS` environment variable:

```bash
CORS_ORIGINS=https://myapp.com,https://staging.myapp.com
```

---

## Best Practices

### 1. Error Handling

```typescript
try {
  const response = await fetch('/api/meme/generate', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('Meme generation failed:', error);
  // Handle error
}
```

### 2. File Validation (Client-side)

```typescript
function validateImage(file: File): boolean {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  if (!validTypes.includes(file.type)) {
    alert('Invalid file type');
    return false;
  }
  
  if (file.size > maxSize) {
    alert('File too large');
    return false;
  }
  
  return true;
}
```

### 3. Loading States

```typescript
const [loading, setLoading] = useState(false);

const generateMeme = async () => {
  setLoading(true);
  try {
    const result = await fetch(...);
    // Handle result
  } finally {
    setLoading(false);
  }
};
```

---

## Advanced Usage

### Custom Business Context

To use custom business context instead of minimal defaults, you would need to modify the `meme_service.py` to accept additional parameters.

### Batch Processing

For batch meme generation, call the endpoint multiple times:

```typescript
async function generateMultipleMemes(contents: string[]) {
  const promises = contents.map(content => 
    generateMeme(content, templateFile)
  );
  
  return await Promise.all(promises);
}
```

---

## Support

For issues or questions, please refer to the main README.md or open an issue on the repository.
