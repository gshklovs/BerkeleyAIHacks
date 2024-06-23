'use client'

import { useEffect, useRef, useState } from 'react';
import axios from 'axios';


export default function AudioRecorder(){
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);
    mediaRecorderRef.current.ondataavailable = (event) => {
      audioChunksRef.current.push(event.data);
      sendAudioData(event.data);
    };

    mediaRecorderRef.current.start(5000); // Collect audio data every 100 milliseconds
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  const sendAudioData = async (audioChunk) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioChunk, 'audio.wav');

      const response = await axios.post('http://localhost:5328/api/upload_audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log(response)

    } catch (error) {
      console.error('Error sending audio data:', error);
    }
  };

  return (
    <div>
      <h1>Audio Recorder</h1>
      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? 'Stop Recording' : 'Start Recording'}
      </button>
    </div>
  );
};
