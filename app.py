import re
import os
from flask import Flask, request, jsonify, send_file, render_template, url_for
import yt_dlp as youtube_dl

app = Flask(__name__)

# Path to store temporarily downloaded files
DOWNLOAD_FOLDER = os.path.join('static', 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def sanitize_filename(filename):
    # Remove or replace invalid characters for Windows file names
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

@app.route('/')
def index():
    return render_template('index.html')

def download_video(link, resolution, is_playlist=False):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': not is_playlist,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        file_path = ydl.prepare_filename(info)
        sanitized_file_path = sanitize_filename(file_path)
        os.rename(file_path, sanitized_file_path)
        return sanitized_file_path, info

@app.route('/download', methods=['POST'])
def download_handler():
    data = request.json
    download_type = data.get('downloadType')
    link = data.get('link')
    resolution = data.get('resolution')

    if not link:
        return jsonify({'error': 'Invalid YouTube link'}), 400

    try:
        if download_type == 'video':
            file_path, info = download_video(link, resolution, is_playlist=False)
            file_name = sanitize_filename(f"{info['title']}.mp4")
            return jsonify({'message': 'Download complete', 'filePath': url_for('serve_file', filename=file_name)})

        elif download_type == 'playlist':
            file_path, info = download_video(link, resolution, is_playlist=True)
            playlist_title = sanitize_filename(info['title'])
            file_name = f"{playlist_title}.mp4"
            return jsonify({'message': f'{len(info["entries"])} videos downloaded from playlist', 'filePath': url_for('serve_file', filename=file_name)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloaded-file/<filename>', methods=['GET'])
def serve_file(filename):
    sanitized_filename = sanitize_filename(filename)
    file_path = os.path.join(DOWNLOAD_FOLDER, sanitized_filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
