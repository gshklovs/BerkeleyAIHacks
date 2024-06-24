import AudioRecorder from "./components/AudioRecorder";
import { LampContainer } from "./components/aceternity/lamp";
import LinearizeText from "./live/linearizer";

export default function Home() {
  return (
    <div className="flex text-center flex-col justify-center items-center w-screen min-h-screen bg-gradient-to-br from-black to-purple-700">
      {/* <LampContainer> */}
      <div className="text-6xl ">Start Yapping</div>
      <LinearizeText />
      <AudioRecorder />
      {/* </LampContainer> */}
    </div>
  );
}
