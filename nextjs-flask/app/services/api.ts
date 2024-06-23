import axios from "axios";

export async function clear(): Promise<void> {
  try {
    const response = await axios.post("/api/delete_all", {});
    console.log(response.data);
  } catch (error) {
    console.error("Error sending clear request:", error);
  }
}

export async function correlate(): Promise<void> {
  try {
    const response = await axios.post("/api/create_correlation_edges", {});
    console.log(response.data);
  } catch (error) {
    console.error("Error sending create correlation request:", error);
  }
}
