"""
Combine audio narration and a chart image into a short MP4 video.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from moviepy.editor import AudioFileClip, ImageClip

from ..config import RuntimeConfig

logger = logging.getLogger(__name__)


def assemble_video(
    image_path: Path,
    audio_path: Path,
    *,
    output_path: Optional[Path] = None,
    fps: int = 30,
    runtime_config: Optional[RuntimeConfig] = None,
) -> Path:
    """
    Merge an audio track with a static image to create a short clip.
    """
    runtime = runtime_config or RuntimeConfig.from_env()
    output = output_path or image_path.with_name(f"{runtime.run_id}_{image_path.stem}.mp4")
    image_clip = ImageClip(str(image_path))
    audio_clip = AudioFileClip(str(audio_path))
    video = image_clip.set_duration(audio_clip.duration).set_audio(audio_clip)

    output.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Rendering video to %s (run_id=%s)", output, runtime.run_id)
    video.write_videofile(
        str(output),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )
    video.close()
    audio_clip.close()
    image_clip.close()
    return output
