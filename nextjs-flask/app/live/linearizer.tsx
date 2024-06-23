'use client'
import { useEffect, useState } from "react";
import axios from 'axios';
import { cn } from "@/lib/utils";
import { AnimatedList } from "@/components/magicui/animated-list";
 

function Notification(text : string) {
    return (
      <figure
        className={cn(
          "relative mx-auto min-h-fit w-full max-w-[400px] transform cursor-pointer overflow-hidden rounded-2xl p-4",
          // animation styles
          "transition-all duration-200 ease-in-out hover:scale-[103%]",
          // light styles
          "bg-white [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
          // dark styles
          "transform-gpu dark:bg-transparent dark:backdrop-blur-md dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
        )}
      >
        <div className="flex flex-row items-center gap-3">
          <div className="flex flex-col overflow-hidden">
            <p className="text-sm font-normal dark:text-white/60">
              {text}
            </p>
          </div>
        </div>
      </figure>
    );
  };

  

export default function LinearizeText(){
    const [data, setData] = useState([])
    const [CurrentTopic, setCurrentTopic] = useState("")
    const [CurrLength, setCurrentLength] = useState(0);
    

    function createList(){
        const ideas = Object.entries(data);
        const ideasLength = Object.entries(data).length
        return(    
        <div className="relative flex max-h-[400px] min-h-[400px] w-full max-w-[32rem] flex-col overflow-hidden rounded-lg border bg-background p-6 shadow-lg">
        <p>{data}</p>

      </div>)


    }

    useEffect(() => {
        const fetchData = async () => {
          try {
            const current = (await axios.get(process.env.NEXT_PUBLIC_API_URL + "/api/current_path")).data; // Replace with your API endpoint
            const response = (await axios.get(process.env.NEXT_PUBLIC_API_URL + "/api/current_topic")).data;
            console.log("DATA : DATA : DATA : DATA")
            console.log(current)
            console.log(response)
            const entries = Object.values(response)

            if (current === CurrentTopic){
                
                if (entries.length != CurrLength){
                    const two = [...data, ...entries]
                    setData(response)
                    setCurrentLength(entries.length);
                }
            }
            else{
                
                setData(response);
                setCurrentTopic(current)
            }
            
          } catch (error) {
            console.error('Error fetching data:', error);
          }
        };
    
        fetchData();
    
        const interval = setInterval(() => {
          fetchData();
        }, 3000); 

        



        return () => clearInterval(interval);
      }, [CurrentTopic, CurrLength]);

    return(<div>{createList()}</div>)
}