import streamlit as st
import subprocess
import tempfile
import os
from yt_dlp import YoutubeDL
from io import BytesIO

st.set_page_config(page_title="YT Video Transformer", layout="centered")
st.title("📥 YouTube Video Downloader + Transformer")

url = st.text_input("🎬 Enter YouTube video URL")

cookie_file = st.file_uploader("🍪 Upload cookies.txt", type=["txt"])
downloaded_path, transformed_path = None, None

def download_video(url, cookie_path):
    temp_dir = tempfile.mkdtemp()
    outtmpl = os.path.join(temp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": False,
        "merge_output_format": "mp4",
        "cookies": cookie_path,
        "extractor_args": {"youtube": {"player_client": "default"}}
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded = ydl.prepare_filename(info)
        if not downloaded.endswith(".mp4"):
            downloaded += ".mp4"
        return downloaded

def apply_transformations(input_path):
    base, _ = os.path.splitext(input_path)
    output_path = base + "_transformed.mp4"

    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "hflip,crop=in_w-8:in_h-8:4:4,scale=iw*0.98:ih*0.98,hue=s=0.97,eq=brightness=0.02:contrast=1.05,noise=alls=10",
        "-af", "asetrate=44100*1.02,atempo=0.98,acompressor",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-y", output_path
    ]

    progress = st.progress(0, text="⏳ Processing video...")

    try:
        process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, universal_newlines=True)
        duration = None

        for line in process.stderr:
            if "Duration" in line:
                t = line.split("Duration: ")[1].split(",")[0]
                h, m, s = map(float, t.split(":"))
                duration = h * 3600 + m * 60 + s

            if "time=" in line and duration:
                ts = line.split("time=")[1].split(" ")[0]
                h, m, s = map(float, ts.split(":"))
                current = h * 3600 + m * 60 + s
                pct = int((current / duration) * 100)
                progress.progress(min(pct, 100) / 100, text=f"🎬 Transforming... {pct}%")

        process.wait()
        progress.progress(1.0, text="✅ Transformation complete!")
        return output_path

    except Exception as e:
        st.error(f"⚠️ FFmpeg failed: {str(e)}")
        return None

if st.button("🔄 Start Download + Transform"):
    if not url or not cookie_file:
        st.error("Please provide both URL and cookies.txt")
        st.stop()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_cookie:
        temp_cookie.write(cookie_file.read())
        cookie_path = temp_cookie.name

    try:
        with st.spinner("📥 Downloading video..."):
            downloaded_path = download_video(url, cookie_path)
        st.success("✅ Video downloaded!")

        with st.spinner("⚙️ Transforming video..."):
            transformed_path = apply_transformations(downloaded_path)

        if transformed_path and os.path.exists(transformed_path):
            with open(transformed_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Transformed Video",
                    data=f,
                    file_name=os.path.basename(transformed_path),
                    mime="video/mp4"
                )
        else:
            st.error("❌ Something went wrong during transformation")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
