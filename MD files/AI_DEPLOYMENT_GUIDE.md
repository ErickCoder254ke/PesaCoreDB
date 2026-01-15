# AI Feature Deployment Guide

## Overview

The AI features in PesacodeDB use Google's Gemini API to provide SQL assistance, query generation, and optimization. For security, all AI requests are now **proxied through the backend** instead of being called directly from the frontend.

## Why This Change?

**Before:** The frontend made direct API calls to Google Gemini, exposing your API key in the browser.

**After:** The frontend sends requests to your backend, which then calls Gemini. Your API key stays secure on the server.

## Backend Configuration (Render)

### 1. Set Environment Variables

In your Render backend service dashboard, add these environment variables:

```bash
# Required for AI features
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional - defaults to gemini-flash-latest
GEMINI_MODEL=gemini-flash-latest

# Existing variables (keep these)
API_KEY=your_api_key
REQUIRE_API_KEY=true
PESADB_URL=pesadb://localhost/default
CORS_ORIGINS=*
```

### 2. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your Render environment variables

### 3. Deploy Backend

After adding the environment variable:
1. Render will automatically redeploy your backend
2. Or manually trigger a deployment from the Render dashboard

### 4. Verify Backend Configuration

Check your backend logs on Render. You should see:

```
🤖 AI Configuration:
   AI Features: ✅ ENABLED
   Gemini API Key: ✅ Configured
   Model: gemini-flash-latest
```

If you see "⚠️ DISABLED", the API key is not set correctly.

## Frontend Configuration (Render)

### No Environment Variables Needed!

The frontend now connects to the backend AI proxy, so you **do NOT need** to set `REACT_APP_GEMINI_API_KEY` on the frontend.

### Backend URL Configuration

Make sure your frontend knows where your backend is:

```bash
# In your frontend Render service
REACT_APP_BACKEND_URL=https://your-backend.onrender.com

# For API authentication
REACT_APP_API_KEY=your_api_key
```

## Testing AI Features

### 1. Check Backend Health Endpoint

Visit: `https://your-backend.onrender.com/api/health`

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-14T...",
  "databases": 1,
  "uptime": "0:05:23",
  "ai_enabled": true
}
```

### 2. Check AI Configuration Endpoint

Visit: `https://your-backend.onrender.com/api/ai/config`

You should see:
```json
{
  "enabled": true,
  "model": "gemini-flash-latest",
  "message": "AI features available"
}
```

If `enabled` is `false`, check your backend environment variables.

### 3. Test in Frontend

1. Open your deployed frontend
2. Go to the SQL Assistant panel
3. Type a question like "Show me all users"
4. You should get an AI-generated SQL query

## New Backend API Endpoints

### GET `/api/ai/config`

Check if AI is configured

**Response:**
```json
{
  "enabled": true,
  "model": "gemini-flash-latest",
  "message": "AI features available"
}
```

### POST `/api/ai/generate`

Generate AI response (proxied to Gemini)

**Request:**
```json
{
  "prompt": "How do I select all users?",
  "context": "Database schema: users table with columns id, name, email",
  "system_prompt": "You are a SQL expert...",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "success": true,
  "message": "To select all users, use:\n\nSELECT * FROM users;"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "AI is not configured. Set GEMINI_API_KEY environment variable.",
  "error_type": "api_key"
}
```

## Troubleshooting

### "AI is not configured" Error

**Symptoms:** Frontend shows "AI is not configured. Please add your Gemini API key"

**Solution:**
1. Check backend environment variable: `GEMINI_API_KEY` is set
2. Check backend logs for "AI Features: ✅ ENABLED"
3. Visit `/api/ai/config` to verify
4. Redeploy backend after adding the variable

### "Network error" Message

**Symptoms:** "Network error. Please check your connection to the backend."

**Solutions:**
1. Check `REACT_APP_BACKEND_URL` is set correctly in frontend
2. Check CORS configuration in backend (should allow your frontend domain)
3. Check backend is running and accessible
4. Check browser console for network errors

### "Authentication failed" Error

**Symptoms:** 403 errors when calling AI endpoints

**Solutions:**
1. Check `REACT_APP_API_KEY` matches backend `API_KEY`
2. Check `REQUIRE_API_KEY=true` in backend
3. Check frontend is sending X-API-Key header (automatic via api-client)

### API Rate Limits

Google's Gemini API has rate limits. If you hit them:
- **Free tier:** 60 requests per minute
- **Solution:** Implement client-side rate limiting (already done in frontend)
- **Upgrade:** Consider upgrading to a paid plan for higher limits

## Cost Considerations

### Gemini API Pricing (as of 2025)

- **Free tier:** 
  - 60 requests per minute
  - 1,500 requests per day
  - Good for development and small projects

- **Paid tier:**
  - Higher rate limits
  - More reliable uptime
  - Better for production

Check current pricing at: https://ai.google.dev/pricing

## Security Best Practices

✅ **DO:**
- Keep `GEMINI_API_KEY` on the backend only
- Use environment variables for all secrets
- Enable API key authentication (`REQUIRE_API_KEY=true`)
- Monitor API usage in Google Cloud Console
- Set appropriate CORS origins (not `*` in production)

❌ **DON'T:**
- Commit API keys to git
- Set `GEMINI_API_KEY` on the frontend
- Expose backend API without authentication
- Use the same API key for dev and production

## Migration from Old Setup

If you were using the old direct-to-Gemini approach:

1. **Remove from frontend:**
   - Delete `REACT_APP_GEMINI_API_KEY` environment variable
   - The code already uses the new backend proxy

2. **Add to backend:**
   - Set `GEMINI_API_KEY` environment variable
   - Deploy backend changes

3. **Redeploy:**
   - Backend first (with new endpoint and env var)
   - Frontend second (to use new proxy)

## Additional Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Render Environment Variables Guide](https://render.com/docs/environment-variables)

## Support

If you're still having issues:

1. Check backend logs on Render
2. Check frontend browser console
3. Test `/api/health` and `/api/ai/config` endpoints
4. Verify all environment variables are set correctly
5. Try redeploying both services

---

**Last Updated:** January 2025  
**Version:** 2.0.0
