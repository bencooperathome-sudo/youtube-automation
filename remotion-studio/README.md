# Remotion evaluation

This isolated branch adds a reproducible, three-second render smoke test for the YouTube automation project. It does not change the existing Python/FFmpeg workflow, use API credentials, or upload a video.

From this directory, run `npm ci` then `npm run render:smoke`. The MP4 is written to `out/`, which is ignored by Git. `npm run studio` opens a local preview. Add approved screenshots, footage, audio and rights review before adapting it to a published video.
