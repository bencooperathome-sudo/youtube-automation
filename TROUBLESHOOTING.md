# 🐛 Troubleshooting Guide

## Common Issues & Solutions

### 1. "ModuleNotFoundError: No module named 'openai'"

**Problem:** Python can't find the openai package

**Solution:**
```bash
pip install openai
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

---

### 2. "OPENAI_API_KEY not found in .env file"

**Problem:** The .env file doesn't exist or doesn't have the right variable

**Solution:**
1. Create `.env` file in project root (same folder as main.py)
2. Add these lines:
```
OPENAI_API_KEY=sk-your-actual-key-here
PEXELS_API_KEY=your-actual-pexels-key-here
```
3. Save and restart Python

---

### 3. "ffmpeg: not found" or "ffmpeg is not recognized"

**Problem:** FFmpeg is not installed or not in PATH

**Solution:**

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
# Add to PATH manually
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

---

### 4. "No videos found for topic"

**Problem:** Pexels search returns no results

**Why:** Some WoW topics may not have good video results on Pexels

**Solution:**
- The system automatically falls back to "gaming" videos
- Videos will still generate (they just won't be WoW-specific)
- Try different topics in settings.py
- If it keeps happening, check your Pexels API key is valid

---

### 5. "Rate limit exceeded" (OpenAI)

**Problem:** Too many API requests in short time

**Solution:**
1. Wait a few minutes before retrying
2. Check usage at: https://platform.openai.com/account/usage
3. Upgrade your OpenAI plan if hitting limits
4. Space out generations (don't run too many at once)

**Example:** Don't run main.py 10 times in 1 second

---

### 6. "Rate limit exceeded" (Pexels)

**Problem:** Pexels free tier has 200 requests/hour limit

**Solution:**
1. Wait 1 hour before running again
2. Upgrade to Pexels paid plan
3. Cache videos locally to reuse them

---

### 7. "MoviePy: Could not write to file"

**Problem:** Permission denied writing video file

**Solution:**
1. Check that `Output/` directory exists and is writable
2. Make sure no other program is using the file
3. Run with admin rights (Windows)
4. Check disk space (need ~500MB free)

---

### 8. "FFmpeg error: File not found"

**Problem:** Subtitle file or audio file wasn't created

**Solution:**
1. Check Output/[timestamp]/ directory
2. Make sure script.txt exists (generation didn't fail)
3. Make sure subtitles.srt exists
4. Check logs for what failed

---

### 9. "YouTube upload fails - 'invalid_client'"

**Problem:** Authentication credentials are incorrect

**Solution:**
1. Delete `token.pickle` file
2. Make sure `client_secret.json` exists in root
3. Run with `--upload` flag again
4. Authenticate in the browser window that opens

---

### 10. "YouTube upload fails - 'forbidden'"

**Problem:** YouTube account doesn't allow uploads

**Solution:**
1. Verify your YouTube account is in good standing
2. Ensure account is verified by YouTube
3. Check if you're using a brand account correctly
4. Try with `--upload` flag after deleting token.pickle

---

## Debugging Steps

### 1. Enable Verbose Logging

The scripts already log to `Logs/` directory. Check the latest log:

```bash
# Windows
type Logs\automation_latest.log

# Mac/Linux
cat Logs/automation_latest.log
```

### 2. Run One Script at a Time

Test each script individually:

```bash
# Step by step
python Scripts/topic_generator.py
python Scripts/video_downloader.py
python Scripts/script_generator.py
python Scripts/voice_generator.py
python Scripts/subtitle_generator.py
python Scripts/metadata_generator.py
python Scripts/video_editor.py
```

### 3. Check Files Exist

```bash
# Windows
dir Output
dir Output\[timestamp]

# Mac/Linux
ls Output/
ls Output/[timestamp]/
```

### 4. Verify API Keys

```bash
# Check .env file
cat .env

# Verify OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"

# Verify Pexels
curl "https://api.pexels.com/v1/search?query=nature" \
  -H "Authorization: YOUR_PEXELS_KEY"
```

---

## Performance Issues

### Video Generation is Slow

**Typical times:**
- topic generation: 5-10 seconds
- video download: 10-20 seconds
- script generation: 3-5 seconds
- voice generation: 2-3 seconds
- subtitle generation: 3-5 seconds
- metadata generation: 3-5 seconds
- video editing: 1-2 minutes
- **Total: 2-5 minutes**

**To speed up:**
- Use a faster internet connection
- Close other programs
- Reduce video quality in settings.py
- Run during off-peak API hours

### Video File is Very Large

**Normal size:** 50-100MB for 30-second 1080x1920 video

**To reduce:**
- Lower video quality in settings.py
- Use different codec (requires ffmpeg knowledge)
- Compress after generation

---

## API Issues

### OpenAI API Issues

**Check:**
1. API key is valid: https://platform.openai.com/account/api-keys
2. Account has usage: https://platform.openai.com/account/usage
3. Not in restricted region
4. Subscription is active

### Pexels API Issues

**Check:**
1. API key is valid: https://www.pexels.com/api/
2. App is still active
3. Free tier rate limit (200/hour)
4. Internet connection is stable

### YouTube API Issues

**Check:**
1. YouTube API enabled in Google Cloud Console
2. OAuth credentials created correctly
3. YouTube account exists and is verified
4. Video not violating YouTube policies

---

## File Not Found Errors

### "Output directory not found"

**Solution:**
```bash
# Create Output directory
mkdir Output

# Or it's created automatically on first run
python main.py
```

### "Topics.txt not found"

**Solution:**
1. Run topic_generator.py first
2. Check Output/[timestamp]/ directory exists
3. Make sure first step completed successfully

---

## Permission Errors

### "Permission denied"

**Windows:**
```bash
# Run as Administrator
# Or check file permissions in Properties
```

**Mac/Linux:**
```bash
# Make files executable
chmod +x main.py
chmod +x Scripts/*.py

# Or run with sudo (not recommended)
sudo python main.py
```

---

## Strange Errors?

### Check These First

1. **Is Python 3.8+?**
   ```bash
   python --version
   ```

2. **Are all dependencies installed?**
   ```bash
   pip install -r requirements.txt
   ```

3. **Is .env file in right location?**
   ```bash
   # Should be in same folder as main.py
   ls .env  # Mac/Linux
   dir .env  # Windows
   ```

4. **Are API keys valid?**
   - Check keys at their respective dashboards
   - Ensure no extra spaces/quotes

5. **Check logs for details**
   ```bash
   # Latest log file
   Logs/automation_*.log
   ```

---

## Getting Help

1. **Read the logs** - They contain detailed error messages
2. **Check README.md** - Full documentation
3. **Review QUICK_START.md** - Common workflows
4. **Run setup.py** - Verify your setup
5. **Test one script at a time** - Isolate the problem

---

## Still Stuck?

**Share these details:**
1. Python version: `python --version`
2. Full error message from logs
3. Which step failed (topic, script, voice, etc.)
4. Your operating system
5. Output of `pip list | grep -E "openai|moviepy|google"`

---

*Last Updated: 2026-07-09*
