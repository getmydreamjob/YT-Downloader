import streamlit as st
from yt_dlp import YoutubeDL
import os

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")

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
    if video_url.strip() == "":
        st.warning("Please enter a valid YouTube video URL.")
    else:
        with st.spinner("Downloading... Please wait..."):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    file_name = ydl.prepare_filename(info)
                st.success("✅ Download completed!")
                st.write(f"**Video Title:** {info['title']}")
                st.video(file_name)

                # Offer download link
                with open(file_name, "rb") as file:
                    btn = st.download_button(
                        label="Download to your device",
                        data=file,
                        file_name=os.path.basename(file_name),
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ Error downloading video: {e}")
