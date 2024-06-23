import LinearizeText from "./live/linearizer";
import Image from "next/image";
import AudioRecorder from "./components/AudioRecorder";

export default function Home() {
  return (
    <div className="flex justify-center items-center h-screen bg-[#d1cab7] text-[##221128]">
      <Image src="/logo.jpg" width={100} height={100} alt="logo" />
      <div className="w-[100%] border">
        <div className="text-5xl text-center text-green-500  mb-2">
          YapTrack
        </div>
        <div className="text-2xl text-center font-light">
          The meeting guide that keeps you on track
        </div>

        <AudioRecorder />
        <LinearizeText />
      </div>
    </div>
  );
}
// TODO Quantify interruptions and speaking time
// TODO Keep track ofagenda if it is followed
