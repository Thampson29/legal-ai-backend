# Legal AI Backend - Deployment Guide

Complete guide for deploying the Legal AI Backend to various cloud platforms for mobile app access.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Deploy Options](#quick-deploy-options)
3. [Platform-Specific Guides](#platform-specific-guides)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment](#post-deployment)
6. [Security Considerations](#security-considerations)

---

## Prerequisites

Before deploying, ensure you have:
- ✅ Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))
- ✅ Git installed locally
- ✅ Code pushed to a GitHub repository
- ✅ ChromaDB vector database (`chroma_db_gemini/` folder)

---

## Quick Deploy Options

### 🚀 Option 1: Railway (Recommended - Easiest)

**Railway offers free tier with automatic deployments from GitHub.**

1. **Create Railway Account**
   - Go to [Railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

3. **Create New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the Procfile

4. **Configure Environment Variables**
   - Go to project → Variables
   - Add:
     ```
     GOOGLE_API_KEY=your_gemini_api_key_here
     CHROMA_DB_PATH=chroma_db_gemini
     CORS_ORIGINS=*
     ```

5. **Deploy**
   - Railway will automatically deploy
   - You'll get a URL like: `https://your-app.railway.app`

6. **Test Your API**
   ```bash
   curl https://your-app.railway.app/health
   ```

---

### 🚀 Option 2: Render.com (Free Tier Available)

**Render offers free web services with automatic SSL.**

1. **Create Render Account**
   - Go to [Render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Using Blueprint (Automatic)**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and configure automatically

3. **Or Manual Deploy**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Environment:** Python 3.11

4. **Add Environment Variables**
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   CHROMA_DB_PATH=chroma_db_gemini
   CORS_ORIGINS=*
   ```

5. **Deploy & Access**
   - Get your URL: `https://your-app.onrender.com`

---

### 🚀 Option 3: Heroku (Paid - No Free Tier)

**Heroku is production-ready but requires paid plan.**

1. **Install Heroku CLI**
   ```bash
   # Windows (PowerShell - Run as Administrator)
   winget install Heroku.HerokuCLI
   
   # Or download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login & Create App**
   ```bash
   heroku login
   heroku create your-legal-ai-backend
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set GOOGLE_API_KEY=your_gemini_api_key_here
   heroku config:set CHROMA_DB_PATH=chroma_db_gemini
   heroku config:set CORS_ORIGINS=*
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Access Your API**
   ```bash
   heroku open
   # Or visit: https://your-legal-ai-backend.herokuapp.com
   ```

---

### 🚀 Option 4: Docker (AWS, GCP, Azure)

**For containerized deployment on major cloud providers.**

#### Local Docker Test
```bash
# Build image
docker build -t legal-ai-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  -e CHROMA_DB_PATH=chroma_db_gemini \
  --name legal-ai-backend \
  legal-ai-backend

# Test
curl http://localhost:8000/health
```

#### Deploy to AWS ECS
1. Install AWS CLI and configure credentials
2. Push to ECR:
   ```bash
   aws ecr create-repository --repository-name legal-ai-backend
   docker tag legal-ai-backend:latest your-account.dkr.ecr.region.amazonaws.com/legal-ai-backend:latest
   docker push your-account.dkr.ecr.region.amazonaws.com/legal-ai-backend:latest
   ```
3. Create ECS Task Definition with environment variables
4. Create ECS Service with Application Load Balancer

#### Deploy to Google Cloud Run
```bash
# Install gcloud CLI
gcloud auth login

# Build and deploy
gcloud builds submit --tag gcr.io/your-project/legal-ai-backend
gcloud run deploy legal-ai-backend \
  --image gcr.io/your-project/legal-ai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key,CHROMA_DB_PATH=chroma_db_gemini
```

#### Deploy to Azure Container Instances
```bash
# Install Azure CLI
az login

# Create container
az container create \
  --resource-group myResourceGroup \
  --name legal-ai-backend \
  --image your-registry.azurecr.io/legal-ai-backend:latest \
  --dns-name-label legal-ai-backend \
  --ports 8000 \
  --environment-variables \
    GOOGLE_API_KEY=your_key \
    CHROMA_DB_PATH=chroma_db_gemini
```

---

### 🚀 Option 5: DigitalOcean App Platform

1. **Create DigitalOcean Account**
   - Go to [DigitalOcean](https://www.digitalocean.com)

2. **Create App**
   - Click "Create" → "App"
   - Connect GitHub repository
   - Configure:
     - **Run Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8080`
     - **HTTP Port:** 8080

3. **Add Environment Variables**
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   CHROMA_DB_PATH=chroma_db_gemini
   ```

---

## Environment Variables

All deployments require these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | - | Your Google Gemini API key |
| `CHROMA_DB_PATH` | ❌ No | `chroma_db_gemini` | Path to ChromaDB vector database |
| `CORS_ORIGINS` | ❌ No | `*` | Comma-separated list of allowed origins |
| `PORT` | ❌ No | `8000` | Port number (auto-set by most platforms) |

### Production CORS Configuration

For production, replace `*` with specific origins:
```bash
CORS_ORIGINS=https://yourmobileapp.com,https://app.yourdomain.com
```

---

## Post-Deployment

### 1. Test Your Deployment

#### Test Health Endpoint
```bash
curl https://your-deployed-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Legal AI Backend is running",
  "vector_store_loaded": true
}
```

#### Test Chat Endpoint
```bash
curl -X POST https://your-deployed-url.com/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Article 14?"}'
```

### 2. Mobile App Integration

#### Flutter Example
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class LegalAIService {
  static const String baseUrl = 'https://your-deployed-url.com';
  
  Future<Map<String, dynamic>> askQuestion(String query) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'query': query}),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get answer');
    }
  }
}
```

#### React Native Example
```javascript
const API_BASE_URL = 'https://your-deployed-url.com';

export const askQuestion = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

#### Swift (iOS) Example
```swift
import Foundation

class LegalAIService {
    static let baseURL = "https://your-deployed-url.com"
    
    func askQuestion(query: String, completion: @escaping (Result<[String: Any], Error>) -> Void) {
        guard let url = URL(string: "\(LegalAIService.baseURL)/chat") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: ["query": query])
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                return
            }
            
            completion(.success(json))
        }.resume()
    }
}
```

#### Kotlin (Android) Example
```kotlin
import retrofit2.http.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

data class ChatRequest(val query: String)
data class ChatResponse(val answer: String, val citations: List<Any>, val has_context: Boolean)

interface LegalAIApi {
    @POST("chat")
    suspend fun askQuestion(@Body request: ChatRequest): ChatResponse
}

object LegalAIService {
    private const val BASE_URL = "https://your-deployed-url.com/"
    
    val api: LegalAIApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(LegalAIApi::class.java)
    }
}
```

---

## Security Considerations

### 1. API Key Security
- ✅ **DO:** Store `GOOGLE_API_KEY` as environment variable
- ❌ **DON'T:** Commit API keys to Git
- ✅ **DO:** Use secrets management (Railway Secrets, Render Environment Groups)

### 2. CORS Configuration
```python
# Development - Allow all
CORS_ORIGINS=*

# Production - Restrict to your domains
CORS_ORIGINS=https://yourapp.com,https://app.yourdomain.com
```

### 3. Rate Limiting (Optional Enhancement)
Add rate limiting middleware to prevent abuse:
```bash
pip install slowapi
```

### 4. HTTPS Only
- All recommended platforms provide free SSL certificates
- Ensure your mobile app only communicates over HTTPS

### 5. API Authentication (Optional Enhancement)
For production, consider adding API key authentication:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

---

## Monitoring & Logs

### Railway
- View logs: Dashboard → Deployments → View Logs
- Monitor usage: Dashboard → Metrics

### Render
- View logs: Dashboard → Logs tab
- Monitor: Dashboard → Metrics tab

### Heroku
```bash
heroku logs --tail
heroku ps
```

### Docker-based (CloudWatch, Stackdriver, etc.)
Configure logging drivers and monitoring as per platform documentation.

---

## Troubleshooting

### Issue: Health check fails
**Solution:** Check if `GOOGLE_API_KEY` is set correctly
```bash
# Railway/Render
Check Variables section

# Heroku
heroku config:get GOOGLE_API_KEY
```

### Issue: CORS errors in mobile app
**Solution:** Update CORS_ORIGINS
```bash
CORS_ORIGINS=*  # Allow all (development)
CORS_ORIGINS=https://yourapp.com  # Production
```

### Issue: ChromaDB not loading
**Solution:** Ensure `chroma_db_gemini/` folder is included in deployment
- For Railway/Render: Commit the folder to Git
- For Docker: Verify `COPY chroma_db_gemini/` in Dockerfile

### Issue: Slow responses
**Solutions:**
1. Upgrade to paid tier for better resources
2. Cache frequently asked questions
3. Use faster Gemini model (gemini-2.0-flash-lite)

---

## Cost Estimates (USD/month)

| Platform | Free Tier | Paid Plan | Best For |
|----------|-----------|-----------|----------|
| **Railway** | $5 credit/month | $5+/month | Quick deploys, auto-scaling |
| **Render** | 750 hours/month | $7+/month | Reliable free tier |
| **Heroku** | None | $7+/month | Enterprise features |
| **DigitalOcean** | $200 credit (60 days) | $5+/month | Full control |
| **AWS/GCP/Azure** | Free tier (limits) | Pay-as-you-go | Large scale |

---

## Recommended Deployment Path

**For Getting Started (Free):**
1. Start with **Railway** or **Render** (free tier)
2. Test with mobile app
3. Monitor usage

**For Production:**
1. Upgrade to paid tier on Railway/Render, or
2. Move to Docker on AWS ECS/GCP Cloud Run for better control
3. Add monitoring, API authentication, rate limiting
4. Set up CI/CD pipelines

---

## Next Steps

1. ✅ Choose a deployment platform
2. ✅ Set up environment variables
3. ✅ Deploy and test
4. ✅ Integrate with mobile app
5. ✅ Monitor and optimize

For issues or questions, refer to platform-specific documentation or create an issue in your repository.

---

**Your API URL will be:**
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`
- Heroku: `https://your-app.herokuapp.com`

**Mobile App Configuration:**
```javascript
const API_BASE_URL = 'https://your-deployed-url.com';
```

Happy Deploying! 🚀
