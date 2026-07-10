"""Daily scheduler for automated YouTube Shorts generation."""
import schedule
import time
import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path("Logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def job():
    """Job to run the YouTube Shorts pipeline daily."""
    logger.info("=" * 60)
    logger.info("🎬 Daily WoW Facts Video Generation Started")
    logger.info("=" * 60)
    
    import subprocess
    
    try:
        # Run the main pipeline
        result = subprocess.run(
            [sys.executable, "main.py"],
            check=True,
            capture_output=False
        )
        
        logger.info("✅ Daily video generation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Daily video generation failed: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in scheduler: {e}")
        import traceback
        logger.error(traceback.format_exc())


def schedule_jobs(time_str="09:00", upload=False):
    """
    Schedule daily jobs.
    
    Args:
        time_str: Time in HH:MM format (24-hour) when to run the job
        upload: Whether to upload to YouTube
    """
    
    logger.info(f"📅 Scheduler configured to run daily at {time_str}")
    logger.info(f"📤 YouTube upload: {'Enabled' if upload else 'Disabled'}")
    
    # Schedule the job
    schedule.every().day.at(time_str).do(job)
    
    logger.info("✅ Scheduler started. Waiting for scheduled time...")
    
    # Keep scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n📴 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            time.sleep(60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Shorts Daily Scheduler")
    parser.add_argument(
        "--time",
        default="09:00",
        help="Time to run daily (HH:MM format, 24-hour). Default: 09:00"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload videos to YouTube"
    )
    
    args = parser.parse_args()
    
    # Validate time format
    try:
        datetime.strptime(args.time, "%H:%M")
    except ValueError:
        logger.error(f"Invalid time format: {args.time}. Use HH:MM format (24-hour)")
        sys.exit(1)
    
    try:
        schedule_jobs(time_str=args.time, upload=args.upload)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
