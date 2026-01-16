# Railway Deployment Troubleshooting

## Current Issue: "pip: command not found"

This error occurs when Railway auto-generates an incorrect Dockerfile instead of using your configuration.

---

## ✅ **SOLUTION 1: Force Use of Dockerfile (RECOMMENDED)**

### Step 1: Commit All Changes
```bash
git add .
git commit -m "Fix Railway build configuration"
git push
```

### Step 2: Clear Railway Cache

In Railway Dashboard:
1. Go to your service
2. Click **"Settings"**
3. Scroll down to **"Danger Zone"**
4. Click **"Clear Build Cache"**
5. Click **"Redeploy"**

### Step 3: Verify Build Settings

In Railway Settings → **Build**:
- **Builder**: Should show `Dockerfile`
- **Dockerfile Path**: `Dockerfile`
- **Root Directory**: Leave empty

---

## ✅ **SOLUTION 2: Use Railway Dashboard (Easiest)**

### Delete and Recreate Service:

1. **Delete Current Service**:
   - Go to your Railway project
   - Click on the service
   - Settings → Danger Zone → "Delete Service"

2. **Create New Service**:
   - Click "+ New"
   - Select "GitHub Repo"
   - Choose your repository
   - Railway will auto-detect the Dockerfile

3. **Set Environment Variables** (again):
   ```bash
   API_KEY=your_secure_key
   REQUIRE_API_KEY=true
   PESADB_URL=pesadb://localhost/default?data_dir=/app/data
   CORS_ORIGINS=*
   ```

4. **Add Volume**:
   - Settings → Volumes → Add Volume
   - Mount Path: `/app/data`

5. **Deploy**

---

## ✅ **SOLUTION 3: Use Nixpacks Without Docker**

### Step 1: Remove Dockerfile Temporarily
```bash
# Rename to prevent Railway from using it
mv Dockerfile Dockerfile.backup
```

### Step 2: Ensure nixpacks.toml is Correct

The `nixpacks.toml` file should look like this:
```toml
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = ["pip install -r backend/requirements.txt"]

[start]
cmd = "cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT"
```

### Step 3: Commit and Push
```bash
git add .
git commit -m "Use Nixpacks for deployment"
git push
```

---

## ✅ **SOLUTION 4: Railway CLI Manual Deploy**

### Install Railway CLI
```bash
npm i -g @railway/cli
```

### Login and Link
```bash
railway login
railway link
```

### Set Builder to Dockerfile
```bash
railway service
# Select your service
```

Then in the dashboard:
- Settings → Build → Builder: `Dockerfile`

### Clear Cache and Redeploy
```bash
railway up --detach
```

---

## 🔍 **Verify Your Files Are Correct**

### Check Dockerfile (Root of Project)
```bash
cat Dockerfile
```

Should start with:
```dockerfile
FROM python:3.11-slim
```

### Check railway.json
```bash
cat railway.json
```

Should have:
```json
{
  "build": {
    "builder": "dockerfile",
    "dockerfilePath": "Dockerfile"
  }
}
```

### Check File Structure
```
project/
├── Dockerfile          ← Must be here!
├── railway.json        ← Must be here!
├── nixpacks.toml       ← Must be here!
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── Procfile
├── rdbms/
│   └── ...
└── data/
    └── catalog.json
```

---

## 🐛 **Debug: Check What Railway Sees**

### View Build Logs
```bash
railway logs --deployment
```

Look for:
- `Building Dockerfile` ← Should see this
- `FROM python:3.11-slim` ← Should see this
- NOT `Auto-detected Python` ← Don't want this

### Check Railway Dashboard
1. Click your service
2. Go to **"Deployments"**
3. Click the latest deployment
4. Check **"Build Logs"**

You should see:
```
✓ Building Dockerfile
✓ FROM python:3.11-slim
✓ COPY backend/requirements.txt
✓ RUN pip install...
```

If you see something different, Railway isn't using your Dockerfile!

---

## 💡 **Why This Happens**

Railway tries to be smart and auto-detect your project:
1. It scans your repo
2. If it finds certain files, it auto-generates a build config
3. Sometimes it ignores your Dockerfile and creates its own
4. The auto-generated config doesn't always work

**The fix**: Explicitly tell Railway to use YOUR Dockerfile via `railway.json`

---

## 🚨 **Nuclear Option: Start Fresh**

If nothing works:

### 1. Delete Everything in Railway
- Delete the service completely
- Delete the project if needed

### 2. Create New Project via CLI
```bash
railway init
railway link
```

### 3. Set Builder Before First Deploy
In Railway Dashboard:
- Settings → Build
- Builder: `Dockerfile`
- Dockerfile Path: `Dockerfile`

### 4. Set Environment Variables
```bash
railway variables set API_KEY=your_key
railway variables set REQUIRE_API_KEY=true
railway variables set PESADB_URL=pesadb://localhost/default?data_dir=/app/data
railway variables set CORS_ORIGINS=*
```

### 5. Deploy
```bash
railway up
```

---

## ✅ **Success Indicators**

You'll know it worked when you see:

### In Build Logs:
```
Building with Dockerfile
FROM python:3.11-slim
Successfully installed fastapi uvicorn ...
```

### In Deployment Logs:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

### When Testing:
```bash
curl https://your-app.railway.app/api/health
# Should return:
{
  "status": "healthy",
  "timestamp": "...",
  "databases": 1
}
```

---

## 📞 **Still Not Working?**

### Share This Info:
1. Your build logs (copy from Railway)
2. Output of: `ls -la` (root of project)
3. Output of: `cat railway.json`
4. Output of: `cat Dockerfile`

### Check:
- [ ] Dockerfile exists in root directory
- [ ] railway.json specifies "dockerfile" builder
- [ ] You've cleared Railway build cache
- [ ] You've committed and pushed all changes
- [ ] Environment variables are set in Railway

---

## 🎯 **Quick Checklist**

Before deploying:
- [ ] `Dockerfile` exists in root
- [ ] `railway.json` has `"builder": "dockerfile"`
- [ ] Committed all changes: `git push`
- [ ] Cleared Railway cache in dashboard
- [ ] Environment variables set in Railway
- [ ] Volume mounted at `/app/data`
- [ ] Redeployed from Railway dashboard

---

Good luck! 🚀
