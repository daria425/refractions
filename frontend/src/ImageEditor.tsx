import { useLocation } from "react-router";
import JSONEditor from "./components/JSONEditor";
import type { ImageResult, EditorState } from "./types";
import { flattenStructuredPrompt } from "./utils";
import { useState } from "react";
export default function ImageEditor() {
  const location = useLocation();
  const imageData = location.state as ImageResult;
  const [editorState, setEditorState] = useState<EditorState>({
    activeEditor: null,
  });
  const promptEntries = flattenStructuredPrompt(
    imageData.data.structured_prompt
  );
  const [textAreaJSON, setTextAreaJSON] = useState(
    JSON.stringify(imageData.data.structured_prompt, null, 2)
  );

  const handleEditJson = (newValue: string) => {
    setTextAreaJSON(newValue);
  };
  function handleOpenJSONEditor(editorContent: Record<string, any>) {
    setEditorState({
      activeEditor: "json",
      editorContent,
    });
  }
  function handleCloseEditor() {
    setEditorState({ activeEditor: null });
  }
  return (
    <div className="px-8 py-4 flex relative">
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-8 lg:flex border border-white/20 max-w-6xl mx-auto gap-8">
        <div>
          <img src={`${imageData.data.saved_path}`}></img>
        </div>

        <div className="flex flex-col gap-2">
          <button className="py-2 px-4 rounded-lg border border-white/20 bg-purple-100 hover:bg-purple-200">
            Advanced JSON Editor
          </button>
          <button className="py-2 px-4 rounded-lg border border-white/20 bg-purple-100 hover:bg-purple-200">
            Auto-Edit
          </button>
        </div>
      </div>
      <JSONEditor
        structuredPromptJson={textAreaJSON}
        promptEntries={promptEntries}
        handleEditJson={handleEditJson}
      />
    </div>
  );
}
