import axios from "axios";
import initialGenerationResponse from "../data/api/initial_generation_response.json";
let baseUrl = "http://127.0.0.1:8000";
if (import.meta.env.MODE === "production") {
  baseUrl = import.meta.env.VITE_API_URL;
}

const apiClient = axios.create({
  baseURL: baseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

const realPost = apiClient.post.bind(apiClient);

function handleEndpoint(endpoint: string, requestBody?: any, config?: any) {
  if (endpoint === "/generate" || endpoint.startsWith("/generate?")) {
    return { data: initialGenerationResponse };
  }
  // dont mock for others
  return realPost(endpoint, requestBody, config);
}

async function mockPost(endpoint: string, requestBody?: any, config?: any) {
  console.log("MockClient POST called:", { endpoint, requestBody, config });
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return handleEndpoint(endpoint, requestBody, config);
}

// if (import.meta.env.MODE !== "production") {
//   (apiClient as any).post = mockPost;
// }

export { baseUrl };
export default apiClient;
