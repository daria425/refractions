// CHANGE: Center the JSONEditor using absolute positioning with left/top and transform
import type { ImageResult } from "../types";
import { CodeXml } from "lucide-react";
export default function JSONEditor({ imageData }: { imageData: ImageResult }) {
  return (
    <div className="p-8 bg-white/5 rounded-lg border border-white/20 space-y-4">
      <div className="flex align-center gap-4">
        <CodeXml className="text-white/80" />
        <h4 className="text-white/80 text-lg font-semibold">
          Advanced JSON Editor
        </h4>
      </div>
      <div className="w-full overflow-auto max-w-lg max-h-[60vh] rounded-lg">
        <pre className="whitespace-pre-wrap bg-white/80 p-4">
          {JSON.stringify(imageData.data.structured_prompt, null, 2)}
        </pre>
      </div>
    </div>
  );
}
