"use client";
import { useEffect, useRef, useState } from "react";

const RecordButton = () => {
  const [isRecording, setIsRecording] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [amplitude, setAmplitude] = useState(0);

  useEffect(() => {
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const calculateRMS = (audioData: Float32Array): number => {
    let sum = 0.0;
    for (let i = 0; i < audioData.length; i++) {
      sum += audioData[i] * audioData[i];
    }
    return Math.sqrt(sum / audioData.length);
  };

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContextRef.current = new AudioContext();
    const source = audioContextRef.current.createMediaStreamSource(stream);
    const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (event) => {
      const audioData = event.inputBuffer.getChannelData(0);
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        socketRef.current.send(audioData);
      }

      // Calculate and log the RMS intensity
      const intensity = calculateRMS(audioData);
      setAmplitude(intensity);
      console.log("Audio Intensity (RMS):", intensity);
    };

    source.connect(processor);
    processor.connect(audioContextRef.current.destination);

    mediaRecorderRef.current = new MediaRecorder(stream);
    mediaRecorderRef.current.start();
    setIsRecording(true);

    // Initialize WebSocket connection
    socketRef.current = new WebSocket("ws://localhost:5000/audio");
    socketRef.current.onopen = () => {
      console.log("WebSocket connection opened");
    };
    socketRef.current.onclose = () => {
      console.log("WebSocket connection closed");
    };
    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    if (socketRef.current) {
      socketRef.current.close();
    }
  };

  return (
    <div>
      <div className="bg-gray-700 bg-opacity-50 p-2 rounded-sm">
        <h1 className="p-4 m-1">Audio Streaming</h1>
        <button
          className="bg-blue-500 m-1 p-4 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          onClick={isRecording ? stopRecording : startRecording}
        >
          {isRecording ? "Stop Recording" : "Start Recording"}
        </button>
        <div
          className="h-4 p-4 m-1 rounded-sm bg-green-500"
          style={{ width: `${amplitude * 100}px` }}
        ></div>
      </div>
    </div>
  );
};

export default RecordButton;
