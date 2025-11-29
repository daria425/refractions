// CHANGE: Center the JSONEditor using absolute positioning with left/top and transform
import type React from "react";
import type { ImageResult, PromptEntry } from "../types";
import { CodeXml } from "lucide-react";

// CHANGE: Sidebar with prompt entries + editable textarea. No state wiring yet.
export default function JSONEditor({
  structuredPromptJson,
  promptEntries,
  handleEditJson,
}: {
  handleEditJson: (newValue: string) => void;
  structuredPromptJson: string;
  promptEntries: PromptEntry[];
}) {
  // SUGGESTION: Maintain local component state for:
  // - textareaValue: string (JSON text). Initialize with JSON.stringify(imageData.data.structured_prompt, null, 2)
  // - selectedPath: string | null. When a sidebar button is clicked, set selectedPath and visually highlight the corresponding key.
  // You can lift this state to parent if you want to coordinate Apply & Regenerate.

  return (
    <div className="p-8 bg-white/5 rounded-lg border border-white/20">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <CodeXml className="text-white/80" />
        <h4 className="text-white/80 text-lg font-semibold">
          Advanced JSON Editor
        </h4>
      </div>

      {/* Layout: Sidebar + Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sidebar: Prompt Entry Keys */}
        <aside className="lg:col-span-4 bg-white/5 rounded-lg border border-white/10 p-3">
          <p className="text-white/70 text-sm mb-2">Sections</p>
          <div className="flex flex-col gap-2">
            {promptEntries?.map((entry) => (
              <button
                key={entry.path}
                // SUGGESTION: onClick={() => setSelectedPath(entry.path)}
                className="w-full text-left px-3 py-2 rounded-md bg-white/10 hover:bg-white/20 border border-white/10 text-white/90"
                data-path={entry.path}
                title={entry.path}
              >
                {entry.label}
              </button>
            ))}
          </div>
        </aside>

        {/* Editor: Textarea JSON */}
        <section className="lg:col-span-8">
          <div className="w-full rounded-lg overflow-hidden border border-white/20 bg-white/10">
            {/* # CHANGE: Bind value to textareaValue and onChange to update it */}
            <textarea
              className="w-full h-[60vh] p-4 font-mono text-sm text-white/90 bg-transparent outline-none resize-none"
              value={structuredPromptJson}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                handleEditJson(e.target.value)
              }
              spellCheck={false}
            />
          </div>

          {/* Helper actions (wire up later) */}
          <div className="mt-3 flex flex-wrap gap-2">
            {/* SUGGESTION: Implement handlers: onValidate, onPrettify, onCopy, onDownload, onApply */}
            <button className="px-3 py-2 rounded-md bg-purple-600 text-white hover:bg-purple-700">
              Validate
            </button>
            <button className="px-3 py-2 rounded-md bg-white/10 text-white hover:bg-white/20 border border-white/20">
              Prettify
            </button>
            <button className="px-3 py-2 rounded-md bg-white/10 text-white hover:bg-white/20 border border-white/20">
              Copy
            </button>
            <button className="px-3 py-2 rounded-md bg-white/10 text-white hover:bg-white/20 border border-white/20">
              Download JSON
            </button>
            <button className="px-3 py-2 rounded-md bg-pink-600 text-white hover:bg-pink-700">
              Apply & Regenerate
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
