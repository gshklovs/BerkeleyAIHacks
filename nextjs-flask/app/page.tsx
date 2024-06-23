
import RecordButton from "./components/record_button";
import LinearizeText from "./live/linearizer";

export default function Home() {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <LinearizeText/>
      <RecordButton />
    </div>
  );
}
