# 🌐 Hosting Guide for PesacodeDB

## 🚨 URGENT: Fix Deployment Error First

**Are you getting this error on Render?**
```
error Your lockfile needs to be updated, but yarn was run with `--frozen-lockfile`
warning package-lock.json found... advised not to mix package managers
```

**Quick Fix (Choose One):**

### Option A: Run the Fix Script (Easiest)

**On Windows:**
```bash
DELETE_YARN_LOCK.bat
```

**On Linux/Mac:**
```bash
chmod +x delete-yarn-lock.sh
./delete-yarn-lock.sh
```

Then commit and push:
```bash
git commit -m "Fix deployment: remove yarn.lock, use npm only"
git push
```

### Option B: Manual Fix

Run these commands:

```bash
# Navigate to frontend
cd frontend

# Delete yarn.lock (THIS IS CRITICAL!)
rm yarn.lock
# On Windows: del yarn.lock

# Delete old package-lock.json
rm package-lock.json
# On Windows: del package-lock.json

# Install with npm
npm install --legacy-peer-deps

# Go back to root
cd ..

# Commit ALL changes
git add frontend/
git commit -m "Fix deployment: remove yarn.lock, use npm only"

# Push to trigger redeployment
git push
```

**✅ After pushing, Render will automatically redeploy using npm!**

---

## 📊 Architecture Overview

Your PesacodeDB application consists of three interconnected components:

```
┌─────────────────────────────────────────────────┐
│  Frontend (React)                               │
│  - React SPA with TailwindCSS                   │
│  - Communicates via REST API                    │
│  - Requires: REACT_APP_BACKEND_URL              │
└─────────────────┬───────────────────────────────┘
                  │
                  │ HTTP/HTTPS (API Calls)
                  │ Includes: X-API-Key header
                  │
┌─────────────────▼───────────────────────────────┐
│  Backend (Python FastAPI)                       │
│  - FastAPI REST API server                      │
│  - Handles SQL queries and DB operations        │
│  - Port: 8000 (default)                         │
└─────────────────┬───────────────────────────────┘
                  │
                  │ File I/O (read/write JSON)
                  │
┌─────────────────▼───────────────────────────────┐
│  Database (PesaDB - File-Based)                 │
│  - Custom RDBMS implementation                  │
│  - Stores data as JSON in data/ folder          │
│  - NOT a separate database server               │
│  - Lives on same machine as backend             │
└─────────────────────────────────────────────────┘
```

## ❓ Critical Questions Answered

### Q: Can my hosted app connect to a local database?

**A: NO** ❌

Your database (PesaDB) is **file-based** and runs **inside** the backend application. It is NOT a separate database server like PostgreSQL or MongoDB.

**Why this matters:**
- The database files live on the same machine as the backend
- Your frontend cannot connect to a backend running on your local PC
- You MUST deploy both frontend AND backend to make this work

### Q: Do I need to host the backend?

**A: YES** ✅

Your current situation:
```
❌ Hosted Frontend → Local Backend → Local Database Files
```

What you need:
```
✅ Hosted Frontend → Hosted Backend → Hosted Database Files
```

### Q: Will my data persist after deployment?

**A: It depends** ⚠️

PesaDB stores data as JSON files in the `data/` folder. On Render's free tier:
- ❌ Files are **NOT persistent** between deployments
- ❌ Data is **LOST** when service restarts or redeploys
- ❌ Filesystem resets when service goes to sleep

**Solutions:**
1. **Add Persistent Disk** (Render - $1/month per GB)
2. **Migrate to real database** (PostgreSQL, MongoDB - recommended for production)
3. **Accept ephemeral storage** (for testing/development only)

---

## 🚀 Deployment Guide (Render.com)

### Why Render?
- ✅ Free tier available
- ✅ Easy setup with GitHub integration
- ✅ Automatic deployments on git push
- ✅ Built-in SSL/HTTPS
- ✅ Good for both frontend and backend

---

## 📦 Step 1: Deploy Backend to Render

### 1.1 Create Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### 1.2 Configure Service

```
Name:               pesacodedb-backend
Root Directory:     backend
Environment:        Python 3
Build Command:      pip install -r requirements.txt
Start Command:      python server.py
Instance Type:      Free
```

### 1.3 Generate Secure API Key

Run this command locally to generate a strong API key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
xK9mP2nQ8rT5vW7yZ3aB6cE1fH4jL0oR9sU2wX5zA8
```

Copy this key - you'll need it for both backend and frontend.

### 1.4 Add Environment Variables

Click **"Environment"** tab and add these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `PESADB_URL` | `pesadb://localhost/default` | Database connection URL |
| `API_KEY` | `<your-generated-key>` | Your secure API key from step 1.3 |
| `REQUIRE_API_KEY` | `true` | Enable API authentication |
| `DEBUG` | `false` | Disable debug mode in production |
| `CORS_ORIGINS` | `*` | Allow all origins (update after frontend deployment) |

**Example:**
```env
PESADB_URL=pesadb://localhost/default
API_KEY=xK9mP2nQ8rT5vW7yZ3aB6cE1fH4jL0oR9sU2wX5zA8
REQUIRE_API_KEY=true
DEBUG=false
CORS_ORIGINS=*
```

### 1.5 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete (watch the logs)
3. Once deployed, **copy your backend URL**

**Example backend URL:**
```
https://pesacodedb-backend.onrender.com
```

### 1.6 Test Backend

Test the backend is working:

```bash
# Health check
curl https://your-backend-url.onrender.com/api/health

# Test with API key
curl -X POST https://your-backend-url.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"sql": "SHOW DATABASES", "db": "default"}'
```

Expected response:
```json
{
  "success": true,
  "data": ["default"],
  "execution_time": 0.001
}
```

---

## 🎨 Step 2: Deploy Frontend to Render

### 2.1 Create Static Site

1. In Render dashboard, click **"New +"** → **"Static Site"**
2. Select your repository

### 2.2 Configure Service

```
Name:                pesacodedb-frontend
Root Directory:      frontend
Build Command:       npm install --legacy-peer-deps && npm run build
Publish Directory:   build
```

**Note:** We use `--legacy-peer-deps` to handle the react-day-picker/date-fns dependency resolution.

### 2.3 Add Environment Variables

Click **"Environment"** tab and add:

| Variable | Value | Description |
|----------|-------|-------------|
| `REACT_APP_BACKEND_URL` | `https://your-backend-url.onrender.com` | Your backend URL from Step 1.5 |
| `REACT_APP_API_KEY` | `<same-key-as-backend>` | Same API key used in backend |
| `REACT_APP_REQUIRE_API_KEY` | `true` | Enable API key in requests |

**Example:**
```env
REACT_APP_BACKEND_URL=https://pesacodedb-backend.onrender.com
REACT_APP_API_KEY=xK9mP2nQ8rT5vW7yZ3aB6cE1fH4jL0oR9sU2wX5zA8
REACT_APP_REQUIRE_API_KEY=true
```

### 2.4 Deploy

1. Click **"Create Static Site"**
2. Wait for build to complete
3. Once deployed, **copy your frontend URL**

**Example frontend URL:**
```
https://pesacodedb-frontend.onrender.com
```

---

## 🔒 Step 3: Configure CORS Security

Now that you have your frontend URL, update backend CORS settings:

1. Go to your **backend service** on Render
2. Click **"Environment"** tab
3. Update `CORS_ORIGINS` variable:

```
CORS_ORIGINS=https://pesacodedb-frontend.onrender.com
```

4. Click **"Save Changes"**
5. Backend will automatically redeploy

**For multiple domains:**
```
CORS_ORIGINS=https://pesacodedb-frontend.onrender.com,https://www.yourdomain.com
```

---

## 🧪 Step 4: Test Your Deployment

### 4.1 Test Frontend

1. Open your frontend URL in browser: `https://your-frontend.onrender.com`
2. Open browser DevTools (F12) → Console tab
3. Try executing a SQL query in the app
4. Check console for API calls

**Expected console output:**
```
🔵 API Request: POST /query
✅ API Response: POST /query {status: 200, data: {...}}
```

### 4.2 Verify API Connection

In the browser console, run:

```javascript
// Check API configuration
console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);
console.log('Has API Key:', !!process.env.REACT_APP_API_KEY);
```

### 4.3 Test Database Operations

Try these in your app:

1. **View databases:**
   ```sql
   SHOW DATABASES;
   ```

2. **Create a table:**
   ```sql
   CREATE TABLE test_users (
       id INT PRIMARY KEY,
       name STRING
   );
   ```

3. **Insert data:**
   ```sql
   INSERT INTO test_users VALUES (1, 'Alice');
   ```

4. **Query data:**
   ```sql
   SELECT * FROM test_users;
   ```

---

## 💾 Step 5: Set Up Data Persistence (Optional but Recommended)

### Option A: Add Persistent Disk (Render)

⚠️ **Without this, your data will be lost on each deployment!**

1. Go to your **backend service** on Render
2. Click **"Disks"** in left sidebar
3. Click **"Add Disk"**
4. Configure:
   ```
   Name:        pesacodedb-data
   Mount Path:  /opt/render/project/src/data
   Size:        1 GB
   ```
5. Click **"Create"**
6. Service will redeploy with persistent storage

**Cost:** $1/month per GB

### Option B: Migrate to PostgreSQL (Recommended for Production)

For a production app, consider switching to a real database:

**Benefits:**
- ✅ Reliable data persistence
- ✅ Better performance
- ✅ ACID transactions
- ✅ Concurrent access
- ✅ Backup/restore tools
- ✅ Free tiers available

**Free PostgreSQL options:**
- [Supabase](https://supabase.com) - 500MB free
- [Render PostgreSQL](https://render.com) - Free tier available
- [Neon](https://neon.tech) - Serverless PostgreSQL
- [ElephantSQL](https://www.elephantsql.com) - 20MB free

### Option C: Accept Ephemeral Storage

For development/testing only:
- ✅ No additional cost
- ✅ Simple setup
- ❌ Data lost on restart
- ❌ Not suitable for production

---

## 🔧 Troubleshooting

### Issue 1: "Invalid API Key" Error

**Symptoms:**
- Frontend gets 403 Forbidden responses
- Console shows: "Authentication Error: Invalid or missing API key"

**Solutions:**

1. **Check API keys match:**
   ```bash
   # Backend environment
   API_KEY=xK9mP2nQ8rT5vW7yZ3aB6cE1fH4jL0oR9sU2wX5zA8
   
   # Frontend environment (must be identical)
   REACT_APP_API_KEY=xK9mP2nQ8rT5vW7yZ3aB6cE1fH4jL0oR9sU2wX5zA8
   ```

2. **Verify environment variables are set:**
   - Go to each service → Environment tab
   - Confirm variables are present
   - Redeploy if you made changes

3. **Check frontend is sending the key:**
   - Open browser DevTools → Network tab
   - Click on a request to `/api/query`
   - Check Request Headers for `X-API-Key`

### Issue 2: CORS Error

**Symptoms:**
- Browser console shows CORS error
- Network requests are blocked
- Error: "Access-Control-Allow-Origin"

**Solutions:**

1. **Update backend CORS_ORIGINS:**
   ```env
   # Must include your frontend URL
   CORS_ORIGINS=https://pesacodedb-frontend.onrender.com
   ```

2. **Check for typos:**
   - No trailing slashes: ✅ `https://app.com` ❌ `https://app.com/`
   - Use HTTPS in production, not HTTP
   - Match the exact domain

3. **For development (temporarily):**
   ```env
   CORS_ORIGINS=*
   ```
   ⚠️ Change this to specific domain before production!

### Issue 3: Build Failed on Frontend

**Symptoms:**
- Render build logs show npm errors
- Deployment fails
- Error: "Your lockfile needs to be updated, but yarn was run with `--frozen-lockfile`"
- Error: "package-lock.json found... advised not to mix package managers"

**Root Cause:**
- Project has both `yarn.lock` and `package-lock.json` (conflicting package managers)
- Render defaults to Yarn when it sees `yarn.lock`
- Lockfile is out of sync with dependencies

**Solution (Recommended - Use npm):**

Update your Render **Build Command** to:
```
npm install --legacy-peer-deps && npm run build
```

This forces npm usage and handles peer dependency conflicts.

**Alternative Solutions:**

1. **Option A: Delete package-lock.json and use Yarn:**
   ```bash
   cd frontend
   rm package-lock.json
   yarn install
   git add yarn.lock package.json
   git commit -m "Update yarn.lock and remove package-lock.json"
   git push
   ```

2. **Option B: Delete yarn.lock and use npm only:**
   ```bash
   cd frontend
   rm yarn.lock
   npm install --legacy-peer-deps
   git add package-lock.json package.json
   git commit -m "Switch to npm, remove yarn.lock"
   git push
   ```
   Then use Build Command: `npm install --legacy-peer-deps && npm run build`

3. **Check Node version:**
   - Add `.node-version` file in frontend folder:
   ```
   18.17.0
   ```

### Issue 4: Backend Not Starting

**Symptoms:**
- Backend deployment fails
- Logs show import errors or module not found

**Solutions:**

1. **Check requirements.txt exists:**
   ```
   backend/requirements.txt
   ```

2. **Verify Start Command:**
   ```
   python server.py
   ```

3. **Check Python version:**
   - Add `runtime.txt` in backend folder:
   ```
   python-3.11.0
   ```

4. **Check backend logs:**
   - Go to service → Logs
   - Look for error messages
   - Fix import errors or missing modules

### Issue 5: Data Lost After Deployment

**Symptoms:**
- Data disappears after redeployment
- Tables are gone after service restart

**This is expected behavior** without persistent disk!

**Solutions:**
- See [Step 5: Set Up Data Persistence](#step-5-set-up-data-persistence-optional-but-recommended)
- Add a persistent disk ($1/month)
- Or migrate to PostgreSQL

### Issue 6: "Cannot connect to backend"

**Symptoms:**
- Frontend shows connection errors
- Network tab shows failed requests

**Solutions:**

1. **Check backend is running:**
   - Visit: `https://your-backend-url.onrender.com/api/health`
   - Should return: `{"status": "healthy"}`

2. **Check REACT_APP_BACKEND_URL:**
   ```env
   # Must be full URL including https://
   REACT_APP_BACKEND_URL=https://pesacodedb-backend.onrender.com
   ```

3. **Check for typos:**
   - No trailing slashes
   - Correct domain name
   - HTTPS, not HTTP

---

## 📱 Connecting Mobile/External Apps

Once your backend is deployed, any application can connect using the REST API:

### React Native Example

```javascript
const API_URL = 'https://your-backend-url.onrender.com/api';
const API_KEY = 'your_api_key';

async function executeQuery(sql) {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({
      sql: sql,
      db: 'default'
    })
  });
  
  return await response.json();
}

// Usage
const result = await executeQuery('SELECT * FROM users');
console.log(result.data);
```

### Python App Example

```python
import requests

API_URL = 'https://your-backend-url.onrender.com/api'
API_KEY = 'your_api_key'

def execute_query(sql):
    response = requests.post(
        f'{API_URL}/query',
        json={'sql': sql, 'db': 'default'},
        headers={'X-API-Key': API_KEY}
    )
    return response.json()

# Usage
result = execute_query('SELECT * FROM users')
print(result['data'])
```

### Flutter Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

const API_URL = 'https://your-backend-url.onrender.com/api';
const API_KEY = 'your_api_key';

Future<Map<String, dynamic>> executeQuery(String sql) async {
  final response = await http.post(
    Uri.parse('$API_URL/query'),
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: jsonEncode({
      'sql': sql,
      'db': 'default',
    }),
  );
  
  return jsonDecode(response.body);
}

// Usage
final result = await executeQuery('SELECT * FROM users');
print(result['data']);
```

---

## 🔐 Security Best Practices

### 1. API Key Security

✅ **Do:**
- Generate strong, random API keys (32+ characters)
- Store keys in environment variables
- Rotate keys periodically (every 3-6 months)
- Use different keys for development/production

❌ **Don't:**
- Commit keys to git
- Share keys publicly
- Use simple/guessable keys
- Hardcode keys in source code

### 2. CORS Configuration

✅ **Production:**
```env
# Specific domains only
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

❌ **Avoid in production:**
```env
# Allows any domain (development only!)
CORS_ORIGINS=*
```

### 3. Debug Mode

✅ **Production:**
```env
DEBUG=false
```

❌ **Never in production:**
```env
DEBUG=true  # Exposes sensitive error details!
```

### 4. HTTPS Only

✅ **Always use HTTPS in production:**
```env
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

❌ **Never HTTP in production:**
```env
REACT_APP_BACKEND_URL=http://api.yourdomain.com
```

### 5. Environment Files

✅ **Do:**
- Use `.env.example` templates
- Add `.env` to `.gitignore`
- Document required variables

❌ **Don't:**
- Commit `.env` files to git
- Include real secrets in `.env.example`

---

## 📊 Monitoring Your Deployment

### Render Dashboard

**View Logs:**
1. Go to your service
2. Click "Logs" tab
3. Monitor real-time logs

**Check Metrics:**
1. Go to your service
2. Click "Metrics" tab
3. View CPU, memory, bandwidth usage

### Backend Health Endpoint

Check if backend is healthy:

```bash
curl https://your-backend-url.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-14T10:30:00Z",
  "database": "connected"
}
```

### Frontend Health Check

Visit your frontend URL and check:
- Page loads successfully
- No console errors
- Can execute queries
- Data displays correctly

---

## 🎯 Deployment Checklist

Before going live:

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Render
- [ ] Strong API key generated (32+ chars)
- [ ] Backend environment variables set (API_KEY, PESADB_URL, etc.)
- [ ] Frontend environment variables set (REACT_APP_BACKEND_URL, etc.)
- [ ] CORS configured with frontend URL
- [ ] DEBUG=false on backend
- [ ] HTTPS enabled (automatic on Render)
- [ ] Backend health check passes
- [ ] Frontend can connect to backend
- [ ] API authentication working
- [ ] Test queries successful
- [ ] Persistent disk added (if needed)
- [ ] Monitoring/logging enabled
- [ ] Backup strategy planned

---

## 💡 Cost Breakdown

### Render Free Tier (Current)

**Backend (Web Service):**
- ✅ Free tier available
- ⚠️ 750 hours/month limit
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Slow cold starts (~30 seconds)

**Frontend (Static Site):**
- ✅ 100GB bandwidth/month free
- ✅ No sleep/inactivity limits
- ✅ Fast loading

**Total Cost:** $0/month

### Optional Add-ons

**Persistent Disk:**
- 💰 $1/month per GB
- ✅ Data persists between deployments
- ✅ Required for production data

**Paid Instance:**
- 💰 $7/month (Starter)
- ✅ No sleep
- ✅ Faster performance
- ✅ More resources

---

## 🚀 Next Steps

### After Successful Deployment

1. **Set up monitoring:**
   - Add error tracking (Sentry)
   - Set up uptime monitoring (UptimeRobot)
   - Configure log aggregation

2. **Improve performance:**
   - Add caching
   - Optimize queries
   - Consider CDN for frontend

3. **Enhance security:**
   - Implement rate limiting
   - Add user authentication (JWT)
   - Enable request logging
   - Regular security audits

4. **Plan for scale:**
   - Consider migrating to PostgreSQL
   - Add database backups
   - Implement CI/CD pipeline
   - Add automated tests

### Recommended Improvements

1. **Database Migration** (High Priority)
   - Migrate from file-based PesaDB to PostgreSQL
   - Why: Better performance, reliability, ACID compliance
   - See: `MIGRATION_TO_PESADB.md` for migration patterns

2. **User Authentication** (Medium Priority)
   - Replace API key with JWT tokens
   - Add user roles and permissions
   - Secure admin operations

3. **Automated Backups** (High Priority)
   - Schedule regular database backups
   - Store backups off-site (S3, Google Cloud Storage)
   - Test restore procedures

4. **CI/CD Pipeline** (Medium Priority)
   - Automated testing on push
   - Automated deployment on merge
   - Use GitHub Actions or Render Auto-deploy

---

## 📚 Related Documentation

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Detailed deployment instructions with multiple hosting options
- **[CLIENT_APP_CONNECTION_GUIDE.md](./CLIENT_APP_CONNECTION_GUIDE.md)** - How to connect external apps to your API
- **[README.md](./README.md)** - Project overview and architecture
- **[PESADB_QUICKSTART.md](./PESADB_QUICKSTART.md)** - Database usage guide

---

## 🆘 Getting Help

**Common issues solved:**
- Check [Troubleshooting](#troubleshooting) section above
- Review Render deployment logs
- Check browser console for errors
- Verify environment variables

**Still stuck?**
1. Check the logs on Render dashboard
2. Test backend health endpoint
3. Verify CORS configuration
4. Confirm API keys match

**For Render-specific issues:**
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)

---

## ✅ Success Indicators

Your deployment is successful when:

- ✅ Backend health check returns `{"status": "healthy"}`
- ✅ Frontend loads without console errors
- ✅ Can execute SQL queries through UI
- ✅ Data persists (if persistent disk configured)
- ✅ API authentication working
- ✅ CORS configured correctly
- ✅ HTTPS enabled on both services

---

**🎉 Congratulations!** Your PesacodeDB application is now live and accessible from anywhere!

For production use, strongly consider:
1. Adding persistent disk or migrating to PostgreSQL
2. Setting up automated backups
3. Implementing proper authentication
4. Adding monitoring and alerting

---

**Last Updated:** January 14, 2026  
**Version:** 1.0  
**Maintained by:** PesacodeDB Team
