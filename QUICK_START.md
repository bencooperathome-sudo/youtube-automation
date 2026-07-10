# 🚀 Quick Start Guide - YouTube Shorts WoW Automation

## ✅ Setup Status

Your project is **READY TO USE**! All dependencies are installed and configured.

### Verified:
- ✓ Python 3.14.6 (compatible)
- ✓ FFmpeg installed
- ✓ .env file with API keys configured
- ✓ All Python packages installed
- ✓ Project directories created

## 📖 How to Generate Your First Video

### Option 1: Generate ONE Video

```bash
python main.py
```

This will:
1. Pick a random WoW fact topic
2. Download background clips from Pexels
3. Generate a script using GPT-4o-mini
4. Create voice narration
5. Generate subtitles
6. Create metadata (title, description, hashtags)
7. Edit the video with subtitles
8. Save to: `Output/[timestamp]/`

**Time:** ~2-5 minutes depending on internet and system

### Option 2: Generate AND Upload to YouTube

```bash
python main.py --upload
```

First time only: A browser will open asking you to authenticate with YouTube

### Option 3: Schedule Daily Generation

Generate a new video every day at 9:00 AM:

```bash
python scheduler.py --time 09:00
```

Or at a custom time (24-hour format):

```bash
python scheduler.py --time 14:30
```

**To run daily with uploads:**

```bash
python scheduler.py --time 09:00 --upload
```

## 📁 Output Structure

After generation, your video will be in:

```
Output/
└── 20260709_093000/              (Timestamp folder)
    ├── topics.txt                 (Generated topic)
    ├── script.txt                 (Narration script)
    ├── voice.mp3                  (Voice file)
    ├── subtitles.srt             (Subtitle file)
    ├── title.txt                  (YouTube title)
    ├── description.txt            (YouTube description)
    ├── hashtags.txt               (YouTube hashtags)
    ├── final_video.mp4            (Video without subtitles)
    └── video_with_subtitles.mp4   (Final video with subtitles) ← UPLOAD THIS
```

## ⚙️ Customization

### Change Daily Topic Category

Edit `settings.py`:

```python
WOW_TOPICS = [
    "World of Warcraft lore",
    "WoW raids and dungeons",
    "WoW character builds",
    # Add your topics...
]
```

### Change Voice

In `settings.py`, options are: `alloy`, `echo`, `fused`, `onyx`, `nova`, `shimmer`

```python
VOICE = "nova"  # More powerful voice
```

## 🐛 Troubleshooting

### "No videos found for topic"
→ This is normal. System will use generic "gaming" videos as fallback.

### "OpenAI API rate limit"
→ Slow down generation frequency or upgrade your OpenAI plan.

### "FFmpeg not found"
→ Make sure FFmpeg is installed: `ffmpeg -version`

### "YouTube upload fails"
→ Delete `token.pickle` and try again. First upload requires authentication.

## 📊 Logs

Check logs if something goes wrong:

```
Logs/
├── automation_20260709_093000.log  (Generation logs)
└── scheduler_20260709.log         (Scheduler logs)
```

## 🎯 Next Steps

1. **Test:** `python main.py` and check `Output/` for videos
2. **Customize:** Edit `settings.py` to add your own WoW topics
3. **Schedule:** Set up daily generation with `scheduler.py`
4. **YouTube:** Set up upload credentials for automatic posting

## 📞 Support

- Check README.md for detailed documentation
- Review logs in `Logs/` folder for errors
- Verify API keys are valid at:
  - OpenAI: https://platform.openai.com/account/usage
  - Pexels: https://www.pexels.com/api/

## 💡 Pro Tips

- Run during off-peak hours to avoid API limits
- Monitor first few videos to ensure quality
- Adjust topics based on what gets the most views
- Use different voice options for variety
- Schedule at consistent times for audience building

---

**Ready to go!** 🎬 Run `python main.py` now!
