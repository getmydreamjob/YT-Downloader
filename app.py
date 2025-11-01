import streamlit as st
import subprocess
import os
import tempfile
from yt_dlp import YoutubeDL
import uuid

def run_ffmpeg(input_path, output_path, audio_only=False):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "hue=s=0",  # grayscale transformation
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "copy",
        "-f", "mp4",
        output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)

st.set_page_config(page_title="YT Downloader", page_icon="📥")
st.title("📥 YouTube Downloader + MP3 + FX")

url = st.text_input("🎯 Enter YouTube video URL:")
apply_transform = st.checkbox("🎨 Apply Grayscale Effect", value=True)
audio_only = st.checkbox("🔊 Download Audio Only (MP3)", value=False)

if st.button("🚀 Download"):
    if not url:
        st.warning("Please enter a URL first.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            video_id = str(uuid.uuid4())
            download_path = os.path.join(tmpdir, f"{video_id}.%(ext)s")
            output_path = os.path.join(tmpdir, f"{video_id}_out.mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio',
                'outtmpl': download_path,
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio' if audio_only else 'FFmpegVideoConvertor',
                    'preferredcodec': 'mp3' if audio_only else 'mp4',
                }],
                'quiet': True,
            }

            with st.spinner("⬇️ Downloading..."):
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    downloaded = ydl.prepare_filename(info)
                    if audio_only:
                        downloaded = downloaded.rsplit(".", 1)[0] + ".mp3"
                        with open(downloaded, "rb") as f:
                            st.download_button("🎧 Download MP3", f, file_name="audio.mp3", mime="audio/mpeg")
                    else:
                        if apply_transform:
                            st.spinner("🎞️ Applying transformation...")
                            run_ffmpeg(downloaded, output_path)
                            with open(output_path, "rb") as f:
                                st.download_button("🎬 Download Transformed MP4", f, file_name="video_fx.mp4", mime="video/mp4")
                        else:
                            with open(downloaded, "rb") as f:
                                st.download_button("📽️ Download Original MP4", f, file_name="video.mp4", mime="video/mp4")
