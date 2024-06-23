import Image from "next/image";
import Link from "next/link";
import RecordButton from "./components/record_button";

export default function Home() {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <RecordButton />
    </div>
  );
}
