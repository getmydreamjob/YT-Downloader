import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import os
import traceback

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Optional cookies upload for age-restricted/private videos
st.sidebar.header("Optional: Cookies")
cookies_file = st.sidebar.file_uploader("Upload your YouTube cookies.txt", type=["txt"])
cookie_path = None
if cookies_file:
    cookie_path = os.path.join(DOWNLOAD_FOLDER, "cookies.txt")
    with open(cookie_path, "wb") as f:
        f.write(cookies_file.getbuffer())

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 YouTube Video Downloader")
st.write("Paste your YouTube video link below to download.")

video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Download Video"):
    if not video_url.strip():
        st.warning("Please enter a valid YouTube video URL.")
    else:
        with st.spinner("Downloading... Please wait..."):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                    'merge_output_format': 'mp4',
                    'http_headers': {
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/115.0.0.0 Safari/537.36'
                        ),
                        'Referer': 'https://www.youtube.com',
                        'Accept-Language': 'en-US,en;q=0.9',
                    },
                    'retries': 3,
                }
                # If user uploaded cookies, include them
                if cookie_path:
                    ydl_opts['cookiefile'] = cookie_path

                with YoutubeDL(ydl_opts) as ydl:
                    # Metadata only, to reject live streams
                    info = ydl.extract_info(video_url, download=False)
                    if info.get('is_live'):
                        st.warning("⚠️ Live streams are not supported.")
                        st.stop()

                    # Actual download
                    info = ydl.extract_info(video_url, download=True)
                    file_name = ydl.prepare_filename(info)
                    if not file_name.endswith(".mp4"):
                        file_name += ".mp4"

                st.success("✅ Download completed!")
                st.write(f"**Title:** {info.get('title', 'Unknown')}")

                size_mb = os.path.getsize(file_name) / (1024 * 1024)
                st.write(f"**Size:** {size_mb:.2f} MB")

                if size_mb <= 500:
                    with open(file_name, "rb") as f:
                        st.download_button(
                            "Download to your device",
                            data=f,
                            file_name=os.path.basename(file_name),
                            mime="video/mp4"
                        )
                else:
                    st.info(
                        f"File is large ({size_mb:.2f} MB); retrieve it from `{DOWNLOAD_FOLDER}` on the server."
                    )

                if size_mb <= 200:
                    st.video(file_name)
                else:
                    st.info("Preview skipped for large video.")

            except DownloadError as de:
                st.error(f"❌ Download failed: {de}")
                st.info(
                    "A 403 may mean the video is private, region-locked, or age-restricted. "
                    "Try uploading your YouTube cookies.txt above."
                )
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
                st.text(traceback.format_exc())
