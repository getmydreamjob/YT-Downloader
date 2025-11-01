import streamlit as st
import os
import subprocess
import tempfile
import shutil
from yt_dlp import YoutubeDL

# Set Streamlit config
st.set_page_config(page_title="YouTube Downloader", layout="centered")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url, use_cookies=False):
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'retries': 10,
        'socket_timeout': 60,
    }

    if use_cookies:
        ydl_opts['cookiefile'] = 'cookies.txt'

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info_dict)

def apply_transformations(input_file):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_transformed.mp4"

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-vf", "hflip,crop=in_w-8:in_h-8:4:4,scale=iw*0.98:ih*0.98,hue=s=0.97,eq=brightness=0.02:contrast=1.05,noise=alls=10",
        "-af", "asetrate=44100*1.02,atempo=0.98,acompressor",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_file
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    with st.spinner("🚧 Applying transformations (this may take several minutes for large files)..."):
        for line in process.stdout:
            if "frame=" in line or "time=" in line or "speed=" in line:
                st.text(line.strip())
        process.wait()

    if process.returncode != 0:
        raise Exception("❌ FFmpeg transformation failed.")
    return output_file

# Streamlit App UI
st.title("🎥 YouTube Downloader + Copyright Filter")

url = st.text_input("🔗 Paste the YouTube URL:")
use_cookies = st.checkbox("Use cookies.txt for age-restricted/private videos")

if st.button("📥 Download & Transform"):
    if not url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        try:
            with st.spinner("🔽 Downloading video... (large videos may take time)"):
                downloaded_file = download_video(url, use_cookies)
                st.success("✅ Download complete!")

            transformed_file = apply_transformations(downloaded_file)
            st.success("🎉 Transformation complete!")

            with open(transformed_file, 'rb') as f:
                st.download_button(
                    label="⬇️ Download Transformed Video",
                    data=f,
                    file_name=os.path.basename(transformed_file),
                    mime="video/mp4"
                )
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
