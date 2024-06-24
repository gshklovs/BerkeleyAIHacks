"use client";
import { useEffect, useState } from "react";
import axios from "axios";
import { LampContainer } from "../components/aceternity/lamp";
import { AnimatedList } from "@/components/magicui/animated-list";

export default function LinearizeText() {
  const [data, setData] = useState<any[]>([]);
  const [currentTopic, setCurrentTopic] = useState("");
  const [currentLength, setCurrentLength] = useState(0);
  const [curHtml, setCurHtml] = useState<JSX.Element | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const currentResponse = await axios.post(
          process.env.NEXT_PUBLIC_API_URL + "/api/current_path"
        );
        const topicResponse = await axios.get(
          process.env.NEXT_PUBLIC_API_URL + "/api/current_topic"
        );

        const current = currentResponse.data;
        const topic = topicResponse.data;
        const entries = Object.values(current);

        if (topic === currentTopic && entries.length === currentLength) {
          // No changes, do nothing
          return;
        }

        const updatedData = [...entries];

        setData(updatedData);
        setCurrentLength(entries.length);
        setCurrentTopic(topic);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 3000);

    return () => clearInterval(interval);
  }, [currentTopic, currentLength]);

  return (
    <div className="w-full text-6xl pt-16">
      {data.length > 0 ? (
        <>
          <div className="bg-black/20 relative flex max-h-[400px] min-h-[400px] w-full max-w-[32rem] flex-col overflow-hidden rounded-lg border bg-background p-6 shadow-lg">
            <AnimatedList>{data}</AnimatedList>
          </div>
          <div>
            Current topic:
            <div className="max-w-full bg-blue-500/20 outline-blue-500 text-white px-2 py-1 rounded-md text-sm font-medium mr-2 border border-blue-500">
              {currentTopic}
            </div>
          </div>
          <div>
            Current path:
            <div className="max-w-full bg-blue-500/20 outline-blue-500 text-white px-2 py-1 rounded-md text-sm font-medium mr-2 border border-blue-500">
              {JSON.stringify(data)}
            </div>
          </div>{" "}
        </>
      ) : (
        <div></div>
      )}
    </div>
  );
}
