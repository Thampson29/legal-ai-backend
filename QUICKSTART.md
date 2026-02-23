# 🚀 Quick Start - Deploy to Cloud in 5 Minutes

## Option 1: Deploy to Railway (Easiest - Free Tier)

### Step 1: Initialize Git & Push to GitHub

```powershell
# Initialize git repository
git init
git add .
git commit -m "Initial commit - Ready for deployment"

# Create GitHub repository at: https://github.com/new
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to **https://railway.app**
2. Click **"Sign up with GitHub"**
3. Click **"New Project"**
4. Click **"Deploy from GitHub repo"**
5. Select your repository
6. Click **"Deploy Now"**

### Step 3: Add Environment Variables

In Railway dashboard:
1. Click on your project
2. Go to **"Variables"** tab
3. Add:
   ```
   GOOGLE_API_KEY=AIzaSyCxlmBXGkc05FhXt9IBCOt8z52Ea_LukHY
   CHROMA_DB_PATH=chroma_db_gemini
   CORS_ORIGINS=*
   ```
4. Click **"Save"**

### Step 4: Get Your API URL

1. Go to **"Settings"** → **"Domains"**
2. Click **"Generate Domain"**
3. Your API will be available at: `https://your-app.railway.app`

### Step 5: Test Your Deployment

```powershell
# Test health endpoint
curl https://your-app.railway.app/health

# Test chat endpoint
curl -X POST https://your-app.railway.app/chat `
  -H "Content-Type: application/json" `
  -d '{"query": "What is Article 14?"}'
```

---

## Option 2: Deploy to Render (Free Tier with Automatic SSL)

### Step 1-2: Same as above (Git + GitHub)

### Step 3: Deploy to Render

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name:** legal-ai-backend
   - **Region:** Choose closest to you
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

### Step 4: Add Environment Variables

In Render dashboard:
1. Scroll to **"Environment Variables"**
2. Add:
   ```
   GOOGLE_API_KEY=AIzaSyCxlmBXGkc05FhXt9IBCOt8z52Ea_LukHY
   CHROMA_DB_PATH=chroma_db_gemini
   CORS_ORIGINS=*
   ```
3. Click **"Create Web Service"**

### Step 5: Wait for Deployment

- First deployment takes 5-10 minutes
- Your API will be at: `https://legal-ai-backend.onrender.com`

---

## Option 3: Test Locally with Docker First

### Build and Run

```powershell
# Build Docker image
docker build -t legal-ai-backend .

# Run container
docker run -d `
  -p 8000:8000 `
  -e GOOGLE_API_KEY=AIzaSyCxlmBXGkc05FhXt9IBCOt8z52Ea_LukHY `
  -e CHROMA_DB_PATH=chroma_db_gemini `
  --name legal-ai-backend `
  legal-ai-backend

# Test
curl http://localhost:8000/health
```

### Using Docker Compose

```powershell
# Create .env file with your API key
echo "GOOGLE_API_KEY=AIzaSyCxlmBXGkc05FhXt9IBCOt8z52Ea_LukHY" > .env

# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Mobile App Integration

Once deployed, use your API URL in your mobile app:

### Flutter
```dart
static const String baseUrl = 'https://your-app.railway.app';
```

### React Native
```javascript
const API_BASE_URL = 'https://your-app.railway.app';
```

### iOS (Swift)
```swift
static let baseURL = "https://your-app.railway.app"
```

### Android (Kotlin)
```kotlin
private const val BASE_URL = "https://your-app.railway.app/"
```

---

## API Endpoints

### Health Check
```
GET https://your-api-url.com/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Legal AI Backend is running",
  "vector_store_loaded": true
}
```

### Chat
```
POST https://your-api-url.com/chat
Content-Type: application/json

{
  "query": "What is Article 14 of Indian Constitution?"
}
```

Response:
```json
{
  "answer": "Article 14 guarantees equality before law...",
  "citations": [],
  "has_context": true
}
```

---

## Troubleshooting

### Issue: Build fails
- Check that `chroma_db_gemini/` folder is committed to Git
- Verify `requirements.txt` is present

### Issue: 500 Internal Server Error
- Check environment variables are set correctly
- Check logs in Railway/Render dashboard

### Issue: CORS errors from mobile app
- Verify `CORS_ORIGINS=*` is set (or specific domains for production)

---

## Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Railway** | $5 credit/month | Quick start, auto-deploy |
| **Render** | 750 hrs/month | Reliable free hosting |
| **Docker Local** | Free | Development & testing |

---

## Next Steps

1. ✅ Deploy to Railway or Render
2. ✅ Test with curl or Postman
3. ✅ Integrate with mobile app
4. ✅ Monitor usage in dashboard

For detailed deployment options, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

**Questions?** Check these resources:
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
