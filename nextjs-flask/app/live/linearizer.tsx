'use client'
import { useEffect, useState } from "react";
import axios from 'axios';
import { cn } from "@/lib/utils";
import { AnimatedList } from "@/components/magicui/animated-list";
 
interface Item {
  name: string;
  description: string;
  icon: string;
  color: string;
  time: string;
}

export default function LinearizeText(){
    const [data, setData] = useState({});

    function createList(){
        const ideas = Object.entries(data);
        const ideasLength = Object.entries(data).length
        return(<AnimatedList>
            ideas
        </AnimatedList>)


    }

    useEffect(() => {
        const fetchData = async () => {
          try {
            const response = await axios.get(process.env.NEXT_PUBLIC_API_URL + ""); // Replace with your API endpoint
            setData(response.data.json());
          } catch (error) {
            console.error('Error fetching data:', error);
          }
        };
    
        fetchData();
    
        const interval = setInterval(() => {
          fetchData();
        }, 3000); 



        return () => clearInterval(interval);
      }, []);

    return(<div></div>)
}