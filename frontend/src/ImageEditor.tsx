import { useLocation } from "react-router";
import type { ImageResult } from "./types";
import { flattenStructuredPrompt } from "./utils";
export default function ImageEditor() {
  const location = useLocation();
  const imageData = location.state as ImageResult;
  console.log("Editing image data:", imageData);
  const promptEntries = flattenStructuredPrompt(
    imageData.data.structured_prompt
  );
  console.log("Prompt Entries:", promptEntries);
  return (
    <div className="px-8 py-4">
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-8 lg:flex border border-white/20 max-w-6xl mx-auto gap-8">
        <div>
          <img src={`${imageData.data.image_url}`}></img>
        </div>
        <div>
          <h2 className="text-2xl font-semibold text-white mb-4 mt-6">
            Generation Details
          </h2>
          <div className="flex flex-col gap-2">
            {promptEntries.map((entry) => {
              return (
                <button className="py-2 px-4 rounded-lg border border-white/20 bg-purple-100 hover:bg-purple-200">
                  {entry.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
