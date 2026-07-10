# 🎬 YouTube Shorts Automation - World of Warcraft Edition

Automatically generate viral YouTube Shorts videos about World of Warcraft facts with AI-generated scripts, voices, and metadata.

## 🌟 Features

- ✅ **AI-Powered Content Generation** - GPT-4o for scripts, metadata, and subtitles
- ✅ **WoW-Specific Facts** - Daily WoW lore, mechanics, and Easter eggs
- ✅ **Automatic Video Editing** - Combines background clips with narration and subtitles
- ✅ **Voice Generation** - High-quality AI voice narration
- ✅ **YouTube Integration** - Automatic upload to YouTube (optional)
- ✅ **Daily Scheduler** - Run automatically every day at a set time
- ✅ **Professional Quality** - 1080x1920 vertical videos optimized for Shorts

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Pexels API key
- YouTube API credentials (optional, for uploads)
- FFmpeg installed on system
- ~2GB free disk space per video

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-proj-your-key-here
PEXELS_API_KEY=your-pexels-key-here
```

### 3. Get API Keys

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste into `.env`

**Pexels API Key:**
1. Go to https://www.pexels.com/api/
2. Sign up for free
3. Create an app to get your API key
4. Copy and paste into `.env`

**YouTube Credentials (Optional for uploads):**
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application)
5. Download as `client_secret.json` and place in project root

### 4. Install FFmpeg

**Windows:**
```bash
# Using chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## 📖 Usage

### Generate Single Video

```bash
python main.py
```

This will:
1. Generate a random WoW fact
2. Download background video clips
3. Create narration script
4. Generate voice and subtitles
5. Edit and combine video
6. Generate title, description, and hashtags

Output will be in `Output/[timestamp]/` directory

### Generate and Upload to YouTube

```bash
python main.py --upload
```

### Schedule Daily Generation

Run videos automatically every day at 9 AM:

```bash
python scheduler.py --time 09:00
```

Or at a custom time:

```bash
python scheduler.py --time 14:30
```

With YouTube upload enabled:

```bash
python scheduler.py --time 09:00 --upload
```

## 📁 Project Structure

```
Youtube Ai/
├── Scripts/                    # Individual pipeline scripts
│   ├── topic_generator.py     # Generate WoW facts
│   ├── video_downloader.py    # Download clips from Pexels
│   ├── script_generator.py    # Create narration script
│   ├── voice_generator.py     # Generate voice (TTS)
│   ├── subtitle_generator.py  # Create SRT subtitles
│   ├── metadata_generator.py  # Generate title/description
│   ├── video_editor.py        # Edit and combine video
│   └── youtube_upload.py      # Upload to YouTube
├── Prompts/                    # AI prompts for content
│   └── wow_script_prompt.txt  # WoW-specific prompt
├── Assets/                     # Downloaded video clips (temp)
├── Output/                     # Generated videos and metadata
├── Logs/                       # Execution logs
├── config.py                   # API configuration
├── settings.py                 # Global settings
├── paths.py                    # File path management
├── main.py                     # Main orchestrator
├── scheduler.py                # Daily scheduler
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (create this)
```

## ⚙️ Configuration

### Customize WoW Topics

Edit `settings.py` to add your own topics:

```python
WOW_TOPICS = [
    "World of Warcraft lore",
    "WoW raids and dungeons",
    "WoW character builds",
    "WoW economy and gold making",
    "WoW PvP strategies",
    "WoW expansions history",
    "WoW Easter eggs",
    # Add more topics here
]
```

### Change Voice

In `settings.py`, change the `VOICE` setting:

```python
VOICE = "alloy"  # Options: alloy, echo, fused, onyx, nova, shimmer
```

### Change Video Resolution

In `settings.py`, adjust:

```python
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
```

## 🎯 Pipeline Flow

```
Topic Generation
    ↓
Video Download (Pexels)
    ↓
Script Generation (GPT-4o-mini)
    ↓
Voice Generation (TTS)
    ↓
Subtitle Generation
    ↓
Metadata Generation (Title, Description, Hashtags)
    ↓
Video Editing (MoviePy + FFmpeg)
    ↓
YouTube Upload (Optional)
```

## 📝 Logs

All execution logs are saved to `Logs/` directory with timestamps. Check logs if something goes wrong:

```bash
# View latest log
cat Logs/automation_latest.log

# Or view scheduler log
cat Logs/scheduler_[date].log
```

## 🐛 Troubleshooting

### "No videos found for topic"
- The video downloader falls back to "gaming" videos
- Try changing your WoW_TOPICS in settings.py

### "FFmpeg not found"
- Make sure FFmpeg is installed and in your PATH
- Verify: `ffmpeg -version`

### "API rate limit exceeded"
- OpenAI: Check your usage at https://platform.openai.com/account/usage
- Pexels: Free tier has 200 requests/hour

### "YouTube upload fails"
- Ensure `client_secret.json` is in the project root
- First upload requires manual authentication (browser will open)
- Token is cached as `token.pickle` for future uploads

## 📊 Performance Tips

- Run during off-peak hours to avoid API rate limits
- Each video takes ~2-5 minutes to generate depending on system
- Use the scheduler for consistent quality and timing
- Monitor logs for bottlenecks

## 🎓 Learn More

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Pexels API Docs](https://www.pexels.com/api/documentation/)
- [YouTube API Docs](https://developers.google.com/youtube/v3)
- [MoviePy Docs](https://zulko.github.io/moviepy/)

## 📄 License

This project is for educational purposes. Ensure you have rights to content and comply with YouTube's Terms of Service.

## 💡 Ideas for Improvement

- [ ] Add support for multiple languages
- [ ] Implement thumbnail generation
- [ ] Add background music library
- [ ] Create video templates for different formats
- [ ] Add analytics dashboard
- [ ] Implement quality checks
- [ ] Add watermark support
- [ ] Create mobile app companion

## 🤝 Contributing

Contributions welcome! Please ensure code follows the existing structure.

## ⚖️ Legal

- Respect copyright and intellectual property
- Ensure facts are accurate about World of Warcraft
- Follow YouTube's Community Guidelines
- Don't misrepresent AI-generated content

---

**Made with ❤️ for WoW enthusiasts**
