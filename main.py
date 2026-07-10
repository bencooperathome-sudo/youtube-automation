"""Main orchestrator for the YouTube Shorts automation pipeline."""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"Logs/automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_pipeline(upload_to_youtube=False):
    """Run the complete YouTube Shorts generation pipeline."""
    
    logger.info("=" * 60)
    logger.info("🎬 YouTube Shorts Automation Pipeline Started")
    logger.info("=" * 60)
    
    try:
        # Step 1: Generate WoW Topic
        logger.info("\n[1/7] Generating WoW topic...")
        from Scripts.topic_generator import topic_generator
        # Import and run would look like:
        import subprocess
        result = subprocess.run([sys.executable, "Scripts/topic_generator.py"], check=True)
        logger.info("✅ Topic generated")
        
        # Step 2: Download background videos
        logger.info("\n[2/7] Downloading background videos from Pexels...")
        result = subprocess.run([sys.executable, "Scripts/video_downloader.py"], check=True)
        logger.info("✅ Videos downloaded")
        
        # Step 3: Generate script
        logger.info("\n[3/7] Generating narration script...")
        result = subprocess.run([sys.executable, "Scripts/script_generator.py"], check=True)
        logger.info("✅ Script generated")
        
        # Step 4: Generate voice narration
        logger.info("\n[4/7] Generating voice narration...")
        result = subprocess.run([sys.executable, "Scripts/voice_generator.py"], check=True)
        logger.info("✅ Voice generated")
        
        # Step 5: Generate subtitles
        logger.info("\n[5/7] Generating subtitles...")
        result = subprocess.run([sys.executable, "Scripts/subtitle_generator.py"], check=True)
        logger.info("✅ Subtitles generated")
        
        # Step 6: Generate metadata
        logger.info("\n[6/7] Generating metadata (title, description, hashtags)...")
        result = subprocess.run([sys.executable, "Scripts/metadata_generator.py"], check=True)
        logger.info("✅ Metadata generated")
        
        # Step 7: Edit video
        logger.info("\n[7/7] Editing video and adding audio/subtitles...")
        result = subprocess.run([sys.executable, "Scripts/video_editor.py"], check=True)
        logger.info("✅ Video created")
        
        # Optional: Upload to YouTube
        if upload_to_youtube:
            logger.info("\n[BONUS] Uploading to YouTube...")
            result = subprocess.run([sys.executable, "Scripts/youtube_upload.py"], check=True)
            logger.info("✅ Video uploaded to YouTube")
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Pipeline completed successfully!")
        logger.info("=" * 60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Pipeline failed at step: {e}")
        logger.error(f"Error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload video to YouTube after creation"
    )
    
    args = parser.parse_args()
    
    success = run_pipeline(upload_to_youtube=args.upload)
    sys.exit(0 if success else 1)
