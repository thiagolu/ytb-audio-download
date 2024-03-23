from flask import Flask, request, jsonify
import base64
from pydub import AudioSegment
from pytube import YouTube
from flask_cors import CORS
import ssl
from io import BytesIO
import io

# Override SSL context to avoid certificate verification issues
ssl._create_default_https_context = ssl._create_stdlib_context



app = Flask(__name__)
CORS(app)

def download_audio_stream(youtube_video_url):
    yt = YouTube(youtube_video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    buffer = io.BytesIO()
    audio_stream.stream_to_buffer(buffer)
    buffer.seek(0)
    return buffer

def modify_and_preview_audio(youtube_video_url, start_seconds, duration_seconds, pitch_semitones, loops):
    buffer = download_audio_stream(youtube_video_url)
    buffer.seek(0)

    audio_segment = AudioSegment.from_file(buffer, format="mp4")
    looped_audio = audio_segment
    # start_ms = start_seconds * 1000  # Convert start time to milliseconds
    # duration_ms = duration_seconds * 1000  # Convert duration to milliseconds
    # end_ms = start_ms + duration_ms
    # cropped_audio = audio_segment[start_ms:end_ms]

    # looped_audio = cropped_audio * loops

    # new_sample_rate = int(looped_audio.frame_rate * (2 ** (pitch_semitones / 12.0)))
    # pitch_shifted_audio = looped_audio._spawn(looped_audio.raw_data, overrides={'frame_rate': new_sample_rate})
    # pitch_shifted_audio = pitch_shifted_audio.set_frame_rate(looped_audio.frame_rate)

    # Export to buffer instead of file
    buffer = BytesIO()
    # pitch_shifted_audio.export(buffer, format="mp3")
    looped_audio.export(buffer, format="mp3")
    buffer.seek(0)

    # Encode the buffer's content to base64
    audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return audio_base64

CORS(app, supports_credentials=True, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
}})

@app.route('/modify_audio', methods=['POST'])
def modify_audio():
    data = request.json
    youtube_video_url = data['youtube_video_url']
    start_seconds = data['start_seconds']
    duration_seconds = data['duration_seconds']
    pitch_semitones = data['pitch_semitones']
    loops = data['loops']
    
    audio_base64 = modify_and_preview_audio(youtube_video_url, start_seconds, duration_seconds, pitch_semitones, loops)
    
    return jsonify({'audio_base64': audio_base64})

if __name__ == '__main__':
    app.run(debug=True, port=5001)

