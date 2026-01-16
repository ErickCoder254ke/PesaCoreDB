# Railway.app Deployment Guide for PesacodeDB

This guide walks you through deploying the PesacodeDB backend to Railway.app.

## Prerequisites

1. A [Railway.app](https://railway.app/) account (free tier available)
2. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Railway CLI installed (optional, but recommended): `npm i -g @railway/cli`

## Step-by-Step Deployment

### Option 1: Deploy via Railway Dashboard (Easiest)

#### 1. Create a New Project

1. Go to [Railway.app](https://railway.app/) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your repositories
5. Select your PesacodeDB repository

#### 2. Configure Build Settings

Railway should auto-detect your Python project. If not:

1. Go to your service settings
2. Under **"Build"** section, ensure:
   - **Root Directory**: Leave empty (or set to `/` if needed)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`

#### 3. Set Environment Variables

In your Railway project dashboard:

1. Click on your service
2. Go to **"Variables"** tab
3. Add the following environment variables:

```bash
# Required
API_KEY=<generate-a-strong-random-key>
REQUIRE_API_KEY=true
PESADB_URL=pesadb://localhost/default

# Optional - AI Features
GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-1.5-flash-latest

# Optional - CORS
CORS_ORIGINS=*

# Optional - Debug
DEBUG=false
```

**Important**: Generate a secure API key:
```bash
# On Mac/Linux
openssl rand -hex 32

# Or use an online generator
# https://www.random.org/strings/
```

#### 4. Add Persistent Volume (Important!)

PesacodeDB stores data in JSON files. To persist data across deployments:

1. In your service dashboard, go to **"Settings"**
2. Scroll to **"Volumes"**
3. Click **"Add Volume"**
4. Mount Path: `/app/data`
5. Click **"Add"**

Then update your `PESADB_URL` environment variable:
```bash
PESADB_URL=pesadb://localhost/default?data_dir=/app/data
```

#### 5. Deploy

Railway will automatically deploy your application. You can monitor the deployment in the **"Deployments"** tab.

#### 6. Get Your Public URL

Once deployed:
1. Go to **"Settings"** tab
2. Under **"Networking"**, click **"Generate Domain"**
3. Railway will provide a public URL like: `https://your-app.railway.app`

#### 7. Test Your Deployment

Test the health endpoint:
```bash
curl https://your-app.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T...",
  "databases": 1,
  "uptime": "0:00:05",
  "ai_enabled": false
}
```

Test with API key:
```bash
curl -X GET https://your-app.railway.app/api/databases \
  -H "X-API-Key: your_api_key_here"
```

---

### Option 2: Deploy via Railway CLI

#### 1. Install Railway CLI

```bash
npm i -g @railway/cli
```

#### 2. Login to Railway

```bash
railway login
```

#### 3. Initialize Project

In your project directory:
```bash
railway init
```

#### 4. Link to Railway Project

```bash
railway link
```

#### 5. Set Environment Variables

```bash
railway variables set API_KEY=<your-secure-key>
railway variables set REQUIRE_API_KEY=true
railway variables set PESADB_URL=pesadb://localhost/default
```

#### 6. Add Volume

```bash
railway volume add --mount-path /app/data
```

Then update PESADB_URL:
```bash
railway variables set PESADB_URL=pesadb://localhost/default?data_dir=/app/data
```

#### 7. Deploy

```bash
railway up
```

#### 8. Open Your App

```bash
railway open
```

---

## Post-Deployment Configuration

### 1. Configure Your Frontend

Update your frontend's API client configuration to point to your Railway URL:

**File**: `frontend/src/lib/config.js`

```javascript
export const API_BASE_URL = 'https://your-app.railway.app/api';
export const API_KEY = 'your_api_key_here';
```

### 2. Update CORS Origins (Production)

For security, restrict CORS to your frontend domain:

```bash
railway variables set CORS_ORIGINS=https://your-frontend-domain.com
```

### 3. Enable AI Features (Optional)

1. Get a Gemini API key from: https://makersuite.google.com/app/apikey
2. Set the environment variable:
```bash
railway variables set GEMINI_API_KEY=<your-key>
```

---

## Monitoring and Logs

### View Logs
```bash
railway logs
```

Or in the dashboard: Click your service → **"Logs"** tab

### Monitor Health
Access these endpoints:
- Health Check: `https://your-app.railway.app/api/health`
- Stats: `https://your-app.railway.app/api/stats`
- API Docs: `https://your-app.railway.app/docs`

---

## Troubleshooting

### Issue: "Server configuration error: API key not set"

**Solution**: Make sure `API_KEY` environment variable is set:
```bash
railway variables set API_KEY=your_secure_key
```

### Issue: Data not persisting between deployments

**Solution**: Ensure you have:
1. Created a volume mounted at `/app/data`
2. Updated `PESADB_URL` to use the volume path:
   ```bash
   railway variables set PESADB_URL=pesadb://localhost/default?data_dir=/app/data
   ```

### Issue: Build fails with "Module not found"

**Solution**: Verify your start command includes `cd backend`:
```bash
cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Issue: CORS errors from frontend

**Solution**: Update CORS_ORIGINS to include your frontend domain:
```bash
railway variables set CORS_ORIGINS=https://your-frontend.com,https://localhost:3000
```

### Issue: Port binding errors

**Solution**: Ensure your start command uses `--port $PORT` (not hardcoded 8000)

---

## Cost Optimization

Railway offers a free tier with:
- $5 free credit per month
- 500 hours of usage
- 512 MB RAM
- Shared CPU

**Tips to stay within free tier:**
1. Set up auto-sleep for inactive services
2. Use volumes efficiently (limited storage)
3. Monitor usage in the Railway dashboard

---

## Security Best Practices

1. **Never commit `.env` files** to your repository
2. **Use strong API keys** (32+ characters)
3. **Restrict CORS** in production
4. **Enable HTTPS** (Railway provides this automatically)
5. **Rotate API keys** regularly
6. **Monitor logs** for suspicious activity

---

## Updating Your Deployment

Railway automatically redeploys when you push to your connected Git branch.

To manually trigger a deployment:
```bash
railway up
```

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord Community](https://discord.gg/railway)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

---

## Getting Help

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Check the [Railway Status Page](https://status.railway.app/)
3. Visit the [Railway Community Forum](https://help.railway.app/)
4. Join the [Railway Discord](https://discord.gg/railway)

---

## Next Steps

After deployment:
1. ✅ Test all API endpoints
2. ✅ Initialize demo data: `POST /api/initialize-demo`
3. ✅ Configure your frontend to use the Railway URL
4. ✅ Set up monitoring and alerts
5. ✅ Document your API key for your team
6. ✅ (Optional) Deploy your frontend to Vercel/Netlify

Happy deploying! 🚀
