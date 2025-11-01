# Free Deployment on Render - Step by Step Guide

## Quick Deploy (5 minutes!)

### Step 1: Commit Your Changes
```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### Step 2: Sign Up on Render
1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account** (easiest way)

### Step 3: Create Web Service
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select your repository: **`Utkarsht2310/Hind-Cap`**
4. Click **"Connect"**

### Step 4: Configure Service
Fill in the following:

- **Name**: `hind-cap` (or any name you like)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Environment**: `Python 3`
- **Build Command**: 
  ```bash
  apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  gunicorn app:app
  ```
- **Plan**: Select **"Free"**

### Step 5: Add Environment Variables
Scroll down to **"Environment Variables"** section and add:

1. Click **"Add Environment Variable"**
2. Add:
   - **Key**: `SECRET_KEY`
   - **Value**: Generate one using Python:
     ```python
     import secrets
     print(secrets.token_hex(32))
     ```
     Or use this online: https://randomkeygen.com/

3. **PORT** - Render automatically sets this, no need to add

4. **FLASK_ENV**:
   - **Key**: `FLASK_ENV`
   - **Value**: `production`

### Step 6: Deploy!
1. Scroll to bottom
2. Click **"Create Web Service"**
3. Wait 5-10 minutes for first deployment (it installs FFmpeg and dependencies)

### Step 7: Access Your App
Once deployed, you'll get a URL like:
```
https://hind-cap.onrender.com
```

🎉 **Your app is live!**

---

## Important Notes about Free Tier

### ⚠️ Free Tier Limitations:
1. **Spins down after 15 minutes of inactivity**
   - First request after inactivity takes 30-60 seconds
   - Subsequent requests are fast

2. **Resource Limits**:
   - 512 MB RAM
   - 0.1 CPU share
   - May be slow for large video processing

### 💡 Tips:
- For faster processing, consider upgrading to Starter ($7/month)
- Monitor your usage in Render dashboard
- Check logs if something goes wrong

---

## Troubleshooting

### Build Fails?
- Check build logs in Render dashboard
- Ensure all dependencies in `requirements.txt` are correct
- Verify FFmpeg is installed in build command

### App Crashes?
- Check runtime logs in Render
- Verify `SECRET_KEY` is set
- Ensure PORT is not manually set (Render handles it)

### Video Processing Too Slow?
- Free tier has limited resources
- Consider processing smaller videos
- Upgrade plan for better performance

---

## Alternative: Railway (Also Free Tier with Credits)

Railway gives $5 free credit monthly:
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select your repo
5. Add environment variables:
   - `SECRET_KEY`: (generate one)
6. Deploy automatically!

Railway is faster but uses credits (still generous free tier).

---

## Need Help?

- Render Docs: https://render.com/docs
- Check your Render dashboard logs
- Verify all files are pushed to GitHub

