from flask import Flask, request, render_template_string
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# Create download directory
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# HTML template
HTML_TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>Video Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; color: #333; }
        .container { background-color: white; padding: 20px; border-radius: 10px; width: 500px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"] { width: 100%; padding: 10px; font-size: 16px; margin-bottom: 10px; }
        button { padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        a { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 YouTube & TikTok Video Downloader</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Paste YouTube or TikTok link here..." required>
            <button type="submit">Download</button>
        </form>
        {% if message %}<p>{{ message }}</p>{% endif %}
        {% if file_path %}
            <p>✅ File ready: <a href="{{ file_path }}" target="_blank">{{ file_path }}</a></p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ''
    file_path = ''
    if request.method == 'POST':
        video_url = request.form['url']

        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                file_path = downloaded_file
                message = '✅ Download completed!'
        except Exception as e:
            message = f'❌ Error: {str(e)}'

    return render_template_string(HTML_TEMPLATE, message=message, file_path=file_path)

if __name__ == '__main__':
    app.run(debug=True)
