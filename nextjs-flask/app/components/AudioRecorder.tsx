"use client";

import { use, useEffect, useRef, useState } from "react";
import ShinyButton from "./magicui/shiny-button";
import axios from "axios";
import { clear, correlate } from "../services/api";

export default function AudioRecorder() {
  const [recording, setRecording] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const startNewRecording = () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      mediaRecorderRef.current = new MediaRecorder(stream);

      // Reset the chunks array to start a fresh recording
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
        audioChunksRef.current.push(event.data);
        sendAudioData(event.data);
      };

      mediaRecorderRef.current.start(); // Start recording immediately
      console.log("Recording started at:", new Date().toLocaleTimeString());
    };

    startNewRecording();
    intervalRef.current = setInterval(startNewRecording, 7000); // Start new recording every 30 seconds

    setRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setRecording(false);
  };

  const sendAudioData = async (audioChunk: Blob) => {
    try {
      const formData = new FormData();
      formData.append("file", audioChunk, "audio.wav");
      console.log("Sending audio data at:", new Date().toLocaleTimeString());
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
    <>
      <div className="flex justify-center">
        <div className="my-4 mx-2">
          <button
            className={`${
              recording
                ? " bg-pink-500 hover:bg-pink-700"
                : "bg-blue-500  hover:bg-blue-700"
            }  text-white font-bold w-full rounded-2xl px-4 py-2`}
            onClick={recording ? stopRecording : startRecording}
          >
            {recording ? "Stop Recording" : "Record"}
          </button>
        </div>
        <div className="my-4 mx-2">
          <button
            className="bg-blue-500 rounded-2xl px-4 py-2 hover:bg-blue-700 text-white font-bold w-full"
            onClick={clear}
          >
            Clear
          </button>
        </div>
        <div className="my-4 mx-2">
          <button
            className="bg-blue-500 rounded-2xl px-4 py-2 hover:bg-blue-700 text-white font-bold w-full"
            onClick={correlate}
          >
            Corellate
          </button>
        </div>
      </div>
    </>
  );
}
