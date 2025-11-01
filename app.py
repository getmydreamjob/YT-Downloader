import streamlit as st
import os
import tempfile
import subprocess
from yt_dlp import YoutubeDL
from pathlib import Path

st.title("📥 YouTube Video Downloader")

url = st.text_input("Enter the YouTube Video URL")

audio_only = st.checkbox("Download Audio Only (MP3)", value=False)
if st.button("Download") and url:
    with st.spinner("Downloading..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title).200s.%(ext)s")
            ydl_opts = {
                "outtmpl": output_template,
                "format": "bestaudio/best" if audio_only else "bestvideo+bestaudio/best",
                "merge_output_format": "mp4" if not audio_only else "mp3",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio" if audio_only else "FFmpegVideoConvertor",
                    "preferredcodec": "mp3" if audio_only else "mp4",
                }],
            }

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    final_file = Path(filename).with_suffix(".mp3" if audio_only else ".mp4")

                with open(final_file, "rb") as f:
                    st.success("✅ Download complete!")
                    st.download_button(
                        label="📥 Click to download file",
                        data=f,
                        file_name=final_file.name,
                        mime="audio/mpeg" if audio_only else "video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
