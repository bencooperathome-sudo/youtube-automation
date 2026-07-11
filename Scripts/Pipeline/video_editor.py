"""Edit video clips and add audio/subtitles."""
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import os
import subprocess
from paths import ASSETS_DIR, VOICE, SUBTITLES, FINAL_VIDEO, VIDEO_WITH_SUBTITLES

print("Loading clips...")

clips = []

for file in sorted(os.listdir(ASSETS_DIR)):
    if file.endswith(".mp4"):
        clip_path = os.path.join(ASSETS_DIR, file)
        clips.append(VideoFileClip(str(clip_path)))

if not clips:
    raise Exception("No video clips found in Assets folder!")

audio = AudioFileClip(str(VOICE))
duration = audio.duration

print(f"✅ Voice length: {duration:.1f} seconds")
print(f"✅ Number of clips: {len(clips)}")

# Calculate duration per clip
clip_duration = duration / len(clips)

edited = []

for i, clip in enumerate(clips):
    print(f"Processing clip {i+1}/{len(clips)}")
    
    new_clip = (
        clip
        .subclipped(0, min(clip.duration, clip_duration))
        .resized(height=1920)
        .cropped(
            width=1080,
            height=1920,
            x_center=clip.w / 2,
            y_center=clip.h / 2
        )
    )
    
    edited.append(new_clip)
    
    print(
        f"  Clip {i+1}: {new_clip.duration:.2f}s @ "
        f"{new_clip.w}x{new_clip.h}"
    )

print("Concatenating clips...")

final = concatenate_videoclips(edited, method="compose")
final = final.with_audio(audio)

print("Writing video file...")

final.write_videofile(
    str(FINAL_VIDEO),
    fps=30,
    codec="libx264",
    audio_codec="aac",
    verbose=False,
    logger=None
)

print("✅ Video created!")
print(f"Location: {FINAL_VIDEO}")

print("Adding subtitles with FFmpeg...")

subprocess.run([
    "ffmpeg",
    "-y",
    "-i", str(FINAL_VIDEO),
    "-vf", f"subtitles={str(SUBTITLES)}",
    "-c:a", "copy",
    str(VIDEO_WITH_SUBTITLES)
], check=True)

print(f"✅ Final video with subtitles saved!")
print(f"Location: {VIDEO_WITH_SUBTITLES}")

# Close all clips
for clip in edited:
    clip.close()
audio.close()