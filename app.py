import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import subprocess
import os
import pickle
import traceback
from openai import OpenAI
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# --- Config ---
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="YouTube Auto Mirror Uploader", page_icon="🎬")
st.title("🎬 YouTube Downloader + Mirror + Auto Upload")

video_url = st.text_input("Paste a YouTube link:", placeholder="https://www.youtube.com/watch?v=...")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Authenticate YouTube ---
def get_authenticated_service():
    if not os.path.exists("token.pickle"):
        st.error("Missing token.pickle. Please upload it in Streamlit Cloud 'Files' tab.")
        st.stop()
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

# --- AI: Title + Description ---
def generate_title_description(original_title):
    prompt = f"""Improve this YouTube title and write a short video description.

Title: "{original_title}"

Return both on two separate lines:
1. New Title
2. Description
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100,
        )
        lines = response.choices[0].message.content.strip().split("\n")
        title = lines[0].strip()
        description = lines[1].strip() if len(lines) > 1 else "Auto-uploaded via Streamlit app."
        return title, description
    except Exception as e:
        st.warning(f"AI fallback: {e}")
        return original_title, "Auto-uploaded via Streamlit app."

# --- Upload to YouTube ---
def upload_to_youtube(file_path, title, description, privacy="unlisted"):
    youtube = get_authenticated_service()
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["auto-upload", "streamlit", "mirrored"]
            },
            "status": {
                "privacyStatus": privacy
            }
        },
        media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            st.write(f"Upload progress: {int(status.progress() * 100)}%")
    return response.get("id")

# --- Main Logic ---
if st.button("Download, Mirror, and Upload"):
    if not video_url.strip():
        st.warning("Please enter a valid YouTube link.")
    else:
        with st.spinner("Processing video..."):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                    'merge_output_format': 'mp4',
                    'retries': 3,
                }

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    if info.get("is_live"):
                        st.error("Live streams are not supported.")
                        st.stop()
                    info = ydl.extract_info(video_url, download=True)
                    file_path = ydl.prepare_filename(info)
                    if not file_path.endswith(".mp4"):
                        file_path += ".mp4"

                # Mirror the video
                mirrored_path = file_path.replace(".mp4", "_mirrored.mp4")
                subprocess.run([
                    "ffmpeg", "-y", "-i", file_path,
                    "-vf", "hflip", "-c:a", "copy", mirrored_path
                ], check=True)

                # AI Title + Description
                title, description = generate_title_description(info.get("title", "Untitled"))

                # Upload to YouTube
                st.info("Uploading to YouTube...")
                video_id = upload_to_youtube(mirrored_path, title, description)
                st.success("✅ Uploaded!")
                st.markdown(f"[▶️ Watch on YouTube](https://youtube.com/watch?v={video_id})")

            except DownloadError as de:
                st.error(f"Download error: {de}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.text(traceback.format_exc())
