from flask import Flask, request, jsonify, send_file, render_template
import os
import yt_dlp as youtube_dl

app = Flask(__name__)

# Path to store downloaded files
DOWNLOAD_FOLDER = os.path.join('static', 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

def download_video(link, resolution, is_playlist=False):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': not is_playlist,  # Avoid playlist download for single video
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        return info

@app.route('/download', methods=['POST'])
def download_handler():
    data = request.json
    download_type = data.get('downloadType')
    link = data.get('link')
    resolution = data.get('resolution')
    apply_resolution_to_all = data.get('applyResolutionToAll', False)

    if not link:
        return jsonify({'error': 'Invalid YouTube link'}), 400

    try:
        # Handle single video download
        if download_type == 'video':
            info = download_video(link, resolution, is_playlist=False)
            video_title = info['title']
            file_name = f"{video_title}.mp4"
            return jsonify({'message': 'Download complete', 'filePath': file_name})

        # Handle playlist download
        elif download_type == 'playlist':
            info = download_video(link, resolution, is_playlist=True)
            playlist_title = info['title']
            file_name = f"{playlist_title} (Playlist)"
            return jsonify({'message': f'{len(info["entries"])} videos downloaded from playlist', 'filePath': file_name})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloaded-file/<filename>', methods=['GET'])
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True)
