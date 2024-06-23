"use client";
import { useEffect, useState } from "react";
import axios from "axios";
import { cn } from "@/lib/utils";
import { AnimatedList } from "@/components/magicui/animated-list";

export default function LinearizeText() {
  const [data, setData] = useState([]);
  const [CurrentTopic, setCurrentTopic] = useState("");
  const [CurrLength, setCurrentLength] = useState(0);

  function createList() {
    const ideas = Object.entries(data);
    const ideasLength = Object.entries(data).length;
    return (
      <div className="relative flex max-h-[400px] min-h-[400px] w-full max-w-[32rem] flex-col overflow-hidden rounded-lg border bg-background p-6 shadow-lg">
        <AnimatedList>{data}</AnimatedList>
      </div>
    );
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const current = (
          await axios.get(process.env.NEXT_PUBLIC_API_URL + "/api/current_path")
        ).data; // Replace with your API endpoint
        const topic = (
          await axios.get(
            process.env.NEXT_PUBLIC_API_URL + "/api/current_topic"
          )
        ).data;
        console.log("DATA : DATA : DATA : DATA");
        console.log(current);
        console.log(topic);
        const entries = Object.values(current);

        if (current === CurrentTopic) {
          if (entries.length != CurrLength) {
            const two = [...data, ...entries];
            setData(current);
            setCurrentLength(entries.length);
          }
        } else {
          setData(current);
          setCurrentTopic(topic);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 3000);

    return () => clearInterval(interval);
  }, [CurrentTopic, CurrLength]);

  return <div>{createList()}</div>;
}
