"use client";

import { useEffect, useRef, useState } from "react";
import axios from "axios";

export default function AudioRecorder() {
  const [recording, setRecording] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);

    mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
      audioChunksRef.current.push(event.data);
      sendAudioData(event.data);
    };

    mediaRecorderRef.current.start(5000); // Collect audio data every 5 seconds
    setRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
  };

  const sendAudioData = async (audioChunk: Blob) => {
    try {
      const formData = new FormData();
      formData.append("file", audioChunk, "audio.wav");

      const response = await axios.post(
        "http://localhost:5328/api/record_and_build",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(response.data);
    } catch (error) {
      console.error("Error sending audio data:", error);
    }
  };

  return (
    <div>
      <h1>Audio Recorder</h1>
      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? "Stop Recording" : "Start Recording"}
      </button>
    </div>
  );
}
