import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import subprocess
import os
import traceback

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="YouTube Downloader with Mirroring",
    page_icon="🎬",
    layout="centered"
)

st.sidebar.header("Optional: Cookies")
cookies_file = st.sidebar.file_uploader("Upload your YouTube cookies.txt", type=["txt"])
cookie_path = None
if cookies_file:
    cookie_path = os.path.join(DOWNLOAD_FOLDER, "cookies.txt")
    with open(cookie_path, "wb") as f:
        f.write(cookies_file.getbuffer())

st.title("🎬 YouTube Video Downloader with Mirroring")
video_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Download Video"):
    if not video_url.strip():
        st.warning("Enter a valid YouTube URL.")
    else:
        with st.spinner("Downloading..."):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'quiet': True,
                    'noplaylist': True,
                    'retries': 3,
                    'concurrent_fragment_downloads': 1,
                    'geo_bypass': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'http_headers': {
                        'Referer': 'https://www.youtube.com',
                        'Accept-Language': 'en-US,en;q=0.9'
                    }
                }

                if cookie_path:
                    ydl_opts['cookiefile'] = cookie_path

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    if info.get('is_live'):
                        st.warning("Live streams are not supported.")
                        st.stop()

                    info = ydl.extract_info(video_url, download=True)
                    file_name = ydl.prepare_filename(info)
                    if not file_name.endswith(".mp4"):
                        file_name += ".mp4"

                if not os.path.exists(file_name) or os.path.getsize(file_name) < 1_000_000:
                    raise Exception("Download completed but file is empty. Possibly blocked or failed silently.")

                st.success("✅ Download completed!")
                st.write(f"**Title:** {info.get('title','Unknown')}")

                size_mb = os.path.getsize(file_name) / (1024 * 1024)
                st.write(f"**Original File Size:** {size_mb:.1f} MB")

                # Download button for original
                with open(file_name, "rb") as f:
                    st.download_button("Download Original", data=f, file_name=os.path.basename(file_name))

                try:
                    st.video(file_name)
                except:
                    st.warning("Preview not available.")

                # -----------------------------
                # Create mirrored version (ffmpeg)
                # -----------------------------
                mirrored_file_name = file_name.replace(".mp4", "_mirrored.mp4")

                if not os.path.exists(mirrored_file_name):
                    st.info("Creating mirrored version using ffmpeg...")
                    try:
                        subprocess.run([
                            "ffmpeg", "-y",
                            "-i", file_name,
                            "-vf", "hflip",
                            "-c:a", "copy",
                            mirrored_file_name
                        ], check=True)
                        st.success("Mirrored video created successfully!")
                    except subprocess.CalledProcessError as e:
                        st.error("Failed to mirror video with ffmpeg.")
                        st.text(e)

                if os.path.exists(mirrored_file_name):
                    mirrored_size_mb = os.path.getsize(mirrored_file_name) / (1024 * 1024)
                    st.write(f"**Mirrored File Size:** {mirrored_size_mb:.1f} MB")
                    with open(mirrored_file_name, "rb") as f:
                        st.download_button("Download Mirrored Video", data=f, file_name=os.path.basename(mirrored_file_name))
                    try:
                        st.video(mirrored_file_name)
                    except:
                        st.warning("Preview not available for mirrored file.")

            except DownloadError as de:
                st.error(f"Download failed: {de}")
                st.info(
                    "403 means YouTube blocked access. Ensure your cookies.txt is from a logged-in account "
                    "and try again, or the video may be private/age-restricted."
                )
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.text(traceback.format_exc())
