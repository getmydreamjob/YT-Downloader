import streamlit as st
from yt_dlp import YoutubeDL
import os
import traceback

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
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
                }

                with YoutubeDL(ydl_opts) as ydl:
                    # 1) Fetch metadata only, to reject live streams up front
                    info = ydl.extract_info(video_url, download=False)
                    if info.get('is_live'):
                        st.warning("⚠️ Live streams are not supported. Please provide a regular video URL.")
                        st.stop()

                    # 2) Now perform the actual download
                    info = ydl.extract_info(video_url, download=True)
                    file_name = ydl.prepare_filename(info)
                    if not file_name.endswith(".mp4"):
                        file_name += ".mp4"

                st.success("✅ Download completed!")
                st.write(f"**Video Title:** {info.get('title', 'Unknown')}")

                file_size = os.path.getsize(file_name)
                size_mb = file_size / (1024 * 1024)
                st.write(f"**File size:** {size_mb:.2f} MB")

                # If file is reasonably small, offer in-browser download
                if size_mb <= 500:
                    with open(file_name, "rb") as f:
                        st.download_button(
                            label="Download to your device",
                            data=f,
                            file_name=os.path.basename(file_name),
                            mime="video/mp4"
                        )
                else:
                    st.info(
                        f"The file is large ({size_mb:.2f} MB) and cannot be served via the browser download button. "
                        f"Please retrieve it from the `{DOWNLOAD_FOLDER}` folder on the server."
                    )

                # Preview small videos only
                if size_mb <= 200:
                    st.video(file_name)
                else:
                    st.info("Preview skipped for large video.")

            except Exception as e:
                st.error(f"❌ Error downloading video: {e}")
                st.text(traceback.format_exc())
