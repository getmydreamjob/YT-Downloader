import streamlit as st
import subprocess
import os
import shutil
import tempfile
from yt_dlp import YoutubeDL
from io import BytesIO

st.set_page_config(page_title="YouTube Downloader", layout="centered")

st.title("🎬 YouTube Downloader + Transformer")

url = st.text_input("Enter YouTube URL")

uploaded_cookies = st.file_uploader("Upload cookies.txt file (from browser)", type=["txt"])

download_button_placeholder = st.empty()
transformed_file_path = None

def download_video(url, cookies_path):
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "cookies": cookies_path,
        "quiet": True,
        "merge_output_format": "mp4"
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        downloaded_file = ydl.prepare_filename(info_dict)
        if not downloaded_file.endswith(".mp4"):
            downloaded_file += ".mp4"
        return downloaded_file, info_dict.get("title", "video")

def mirror_video(input_path):
    base, ext = os.path.splitext(input_path)
    output_path = base + "_mirrored.mp4"

    # Create progress bar
    progress_bar = st.progress(0, text="Applying mirror transformation...")

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "hflip",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "copy",
        "-y", output_path
    ]

    # Run ffmpeg with subprocess and read stderr for updates
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    total_duration = None
    for line in process.stderr:
        if "Duration" in line:
            time_str = line.strip().split("Duration: ")[1].split(",")[0]
            h, m, s = map(float, time_str.split(":"))
            total_duration = h * 3600 + m * 60 + s

        if "time=" in line and total_duration:
            try:
                time_str = line.strip().split("time=")[1].split(" ")[0]
                h, m, s = map(float, time_str.split(":"))
                current = h * 3600 + m * 60 + s
                percent = min(int((current / total_duration) * 100), 100)
                progress_bar.progress(percent / 100, text=f"Transforming... {percent}%")
            except:
                pass

    process.wait()
    progress_bar.progress(1.0, text="Transformation complete ✅")
    return output_path

if st.button("Download and Transform") and url and uploaded_cookies:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as cookie_file:
        cookie_file.write(uploaded_cookies.read())
        cookie_file_path = cookie_file.name

    with st.spinner("📥 Downloading video..."):
        try:
            downloaded_path, title = download_video(url, cookie_file_path)
            st.success("✅ Video downloaded successfully!")
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
            st.stop()

    with st.spinner("🛠️ Transforming video..."):
        try:
            transformed_file_path = mirror_video(downloaded_path)
            st.success("✅ Transformation complete!")
        except Exception as e:
            st.error(f"Transformation failed: {str(e)}")
            st.stop()

    if transformed_file_path:
        with open(transformed_file_path, "rb") as f:
            video_bytes = f.read()
        st.download_button(
            label="⬇️ Download Transformed Video",
            data=BytesIO(video_bytes),
            file_name=os.path.basename(transformed_file_path),
            mime="video/mp4"
        )

        # Clean up temp files
        os.remove(downloaded_path)
        os.remove(transformed_file_path)
        os.remove(cookie_file_path)
