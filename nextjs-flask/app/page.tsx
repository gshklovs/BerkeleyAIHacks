import AudioRecorder from "./components/AudioRecorder";
import LinearizeText from "./live/linearizer";

export default function Home() {
  return (
    <div className="flex flex-col justify-center items-center w-screen min-h-screen">
      <LinearizeText />
      <AudioRecorder />
    </div>
  );
}
