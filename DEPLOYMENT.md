# Deployment Guide

This guide covers deploying the Video Caption Generator to various cloud platforms.

## Prerequisites

- GitHub repository: https://github.com/Utkarsht2310/Hind-Cap.git
- FFmpeg is required for video processing (automatically installed in most platforms)

---

## Option 1: Render (Recommended - Easy & Free Tier Available)

**Best for**: Quick deployment, free tier available, supports FFmpeg

### Steps:

1. **Sign up/Login**: Go to [render.com](https://render.com) and sign up with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select `Hind-Cap` repository

3. **Configuration**:
   - **Name**: `hind-cap` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or choose paid for better performance)

4. **Environment Variables** (Settings → Environment):
   ```
   SECRET_KEY=your-secret-key-here-generate-a-random-string
   PORT=10000
   FLASK_ENV=production
   ```

5. **Advanced Settings**:
   - Add Build Command: `chmod +x build.sh && ./build.sh`
   - Or manually add: `apt-get update && apt-get install -y ffmpeg` in build settings

6. **Deploy**: Click "Create Web Service"

**Note**: Render's free tier spins down after inactivity. First request may take 30-60 seconds.

---

## Option 2: Railway (Great for Video Processing)

**Best for**: Fast deployments, good for resource-intensive apps, $5/month with credits

### Steps:

1. **Sign up**: Go to [railway.app](https://railway.app) and sign up with GitHub

2. **New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `Hind-Cap` repository

3. **Configure**:
   - Railway auto-detects Python apps
   - Add environment variables in Variables tab:
     ```
     SECRET_KEY=your-secret-key-here
     PORT=8080
     ```

4. **Nixpacks Configuration** (optional - create `nixpacks.toml`):
   ```toml
   [phases.setup]
   nixPkgs = ["python311", "ffmpeg"]
   
   [phases.install]
   cmds = ["pip install -r requirements.txt"]
   
   [start]
   cmd = "gunicorn app:app --bind 0.0.0.0:$PORT"
   ```

5. **Deploy**: Railway will automatically deploy

**Note**: Railway provides $5 free credit monthly, then pay-as-you-go.

---

## Option 3: Fly.io (Docker-based)

**Best for**: Full control, Docker support, global deployment

### Steps:

1. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create App**:
   ```bash
   fly launch
   ```
   - Follow prompts
   - Name your app (e.g., `hind-cap`)
   - Select region
   - Don't deploy yet (we'll set env vars first)

4. **Set Secrets**:
   ```bash
   fly secrets set SECRET_KEY="your-secret-key-here"
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

**Note**: Fly.io has a free tier with 3 shared VMs.

---

## Option 4: PythonAnywhere

**Best for**: Free tier available, simple Python hosting

### Steps:

1. **Sign up**: [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Bash Console**:
   - Clone your repo: `git clone https://github.com/Utkarsht2310/Hind-Cap.git`
   - Install FFmpeg: `apt-get install ffmpeg` (or via package manager)
   - Install dependencies: `pip3.10 install -r requirements.txt --user`

3. **Create Web App**:
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose Flask and Python 3.10
   - Set source code directory to your project

4. **Configure WSGI**:
   - Edit the WSGI file to point to `app.py`

5. **Set Environment Variables**: In the Web app config

**Note**: Free tier has limitations; upgrade needed for better performance.

---

## Option 5: Heroku

**Best for**: Traditional deployment (requires paid tier for video processing)

### Steps:

1. **Install Heroku CLI**: [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create App**:
   ```bash
   heroku create hind-cap
   ```

4. **Add Buildpack for FFmpeg**:
   ```bash
   heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest
   heroku buildpacks:add heroku/python
   ```

5. **Set Config Vars**:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key-here"
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

**Note**: Heroku free tier is discontinued. Requires paid plan.

---

## Environment Variables

All platforms need these environment variables:

```
SECRET_KEY=<generate-a-random-secret-key>
PORT=<automatically-set-by-platform>
FLASK_ENV=production
```

### Generate Secret Key:
```python
import secrets
print(secrets.token_hex(32))
```

---

## Post-Deployment

1. **Test the deployment**: Visit your app URL
2. **Check logs**: Monitor for any errors
3. **Update GitHub**: If you made deployment config changes, commit and push
4. **Set up custom domain** (optional): Most platforms support custom domains

---

## Troubleshooting

### FFmpeg not found
- Ensure FFmpeg is installed in the build process
- Check platform logs for installation errors

### Timeout errors
- Increase timeout settings (video processing takes time)
- Consider using background tasks for long operations

### Memory issues
- Upgrade to a higher tier plan
- Optimize video processing (reduce file sizes)

### File storage
- Consider using cloud storage (S3, Cloudinary) for uploaded videos
- Current setup uses local storage (cleared on restart in some platforms)

---

## Recommended Setup

For production, I recommend:
- **Platform**: Render or Railway (both have good free tiers)
- **Storage**: Integrate with cloud storage (S3/GCS) for uploaded videos
- **Database**: Add database for user management (optional)
- **Background Jobs**: Use Celery/Redis for async video processing

---

## Need Help?

- Check platform-specific documentation
- Review application logs
- Test locally first: `python app.py`

