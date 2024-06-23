from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/api/upload_audio', methods=['POST'])
def upload_audio():
    audio_data = request.data
    with open("received_audio.wav", "ab") as audio_file:
        audio_file.write(audio_data)
    return 'Audio received', 200

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5328)
    pass
