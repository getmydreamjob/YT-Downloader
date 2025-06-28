import streamlit as st
from yt_dlp import YoutubeDL
import os
import traceback

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")

# Custom styles
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
                    'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                    'merge_output_format': 'mp4',
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    
                    if info.get('is_live'):
                        st.warning("⚠️ Live streams are not supported. Please provide a regular video URL.")
                        return
                    
                    file_name = ydl.prepare_filename(info)
                    if not file_name.endswith(".mp4"):
                        file_name += ".mp4"  # Ensure extension

                st.success("✅ Download completed!")
                st.write(f"**Video Title:** {info['title']}")

                file_size = os.path.getsize(file_name)
                size_mb = file_size / (1024 * 1024)

                st.write(f"**File size:** {size_mb:.2f} MB")

                if size_mb > 500:
                    st.info(f"The file is too large for in-browser download button. "
                            f"You can find it in the `{DOWNLOAD_FOLDER}` folder on the server.")
                else:
                    with open(file_name, "rb") as file:
                        st.download_button(
                            label="Download to your device",
                            data=file,
                            file_name=os.path.basename(file_name),
                            mime="video/mp4"
                        )

                # Display preview if reasonable size
                if size_mb < 200:
                    st.video(file_name)
                else:
                    st.info("The video is large, so preview is skipped.")

            except Exception as e:
                st.error(f"❌ Error downloading video: {e}")
                st.text(traceback.format_exc())
