import { useLocation, useParams } from "react-router";
import JSONEditor from "./components/JSONEditor";
import AutoVariantEditor from "./components/AutoVariantEditor";
import type { ImageResult, EditorState, APIFetchState } from "./types";
import { flattenStructuredPrompt } from "./utils";
import { useState } from "react";
import useVariantData from "./hooks/useVariantData";
import apiClient from "./api/apiClient";
// import variants from "./config/variants.json";
export default function ImageEditor() {
  const location = useLocation();
  const { request_id } = useParams();
  const imageData = location.state as ImageResult;
  const { fetchedVariants: variants } = useVariantData(request_id!);
  const [editorState, setEditorState] = useState<EditorState>({
    activeEditor: null,
  });

  const [fetchImageEditState, setFetchImageEditState] = useState<APIFetchState>(
    {
      loading: false,
      error: null,
      data: null,
    }
  );

  const [fetchVariantsState, setFetchVariantsState] = useState<APIFetchState>({
    loading: false,
    error: null,
    data: null,
  });

  const [currentVariantLabel, setCurrentVariantLabel] = useState<string | null>(
    null
  );
  // # CHANGE: keep a small list of edited image paths to preview
  const [editedImages, setEditedImages] = useState<string[]>([]);
  const [editedIndex, setEditedIndex] = useState(0);

  const promptEntries = flattenStructuredPrompt(
    imageData.data.structured_prompt
  );
  const [textAreaJSON, setTextAreaJSON] = useState(
    JSON.stringify(imageData.data.structured_prompt, null, 2)
  );
  const handleEditJson = (newValue: string) => {
    setTextAreaJSON(newValue);
  };
  function handleOpenJSONEditor() {
    setEditorState({
      activeEditor: "json",
    });
  }
  function handleOpenAutoEditor() {
    setEditorState({
      activeEditor: "auto-variants",
    });
  }
  function handleCloseEditor() {
    setEditorState({ activeEditor: null });
  }

  const fetchEditImage = async (editQuery: string) => {
    if (editQuery !== "from_structured_prompt") return;
    let parsed: any;
    try {
      parsed = JSON.parse(textAreaJSON);
    } catch (e) {
      console.error("Invalid JSON in editor");
      setFetchImageEditState({
        loading: false,
        error: "Invalid JSON",
        data: null,
      });
      return;
    }
    setFetchImageEditState({ loading: true, error: null, data: null });

    const requestBody = {
      user_structured_prompt: parsed,
      shot_type: imageData.shot_type,
    };
    console.log("Will submit request with:", requestBody);

    try {
      const response = await apiClient.post(
        `/edit/${request_id}?method=${editQuery}`,
        requestBody
      );
      console.log("Edit response:", response.data);
      setFetchImageEditState({
        loading: false,
        error: null,
        data: response.data,
      });
      const newPath =
        response?.data?.data?.saved_path || response?.data?.data?.image_url;
      if (newPath) {
        setEditedImages((prev) => {
          const next = [...prev, newPath];
          setEditedIndex(next.length - 1);
          return next;
        });
      }
    } catch (err: any) {
      const message =
        err?.response?.data?.detail || err?.message || "Edit failed";
      console.error("Edit failed:", message, err);
      setFetchImageEditState({ loading: false, error: message, data: null });
    }
  };

  const fetchVariants = async (selectedVariantLabel: string) => {
    const requestBody = {
      structured_prompt: imageData.data.structured_prompt,
      shot_type: imageData.shot_type,
      seed: imageData.data.seed,
    };
    console.log("Will submit request with:", requestBody);
    setCurrentVariantLabel(selectedVariantLabel);
    setFetchVariantsState({
      loading: true,
      error: null,
      data: null,
    });
    try {
      const response = await apiClient.post(
        `/shots/${request_id}/variants/${selectedVariantLabel}`,
        requestBody
      );
      console.log("Variants response:", response.data);
      setFetchVariantsState({
        loading: false,
        error: null,
        data: response.data,
      });
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Variant generation failed";
      console.error("Variant generation failed:", message, err);
      setFetchVariantsState({ loading: false, error: message, data: null });
      setCurrentVariantLabel(null);
    }
  };
  return (
    <div className="px-8 py-4 2xl:flex relative">
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-8 border border-white/20 max-w-6xl mx-auto gap-8">
        <div className="flex gap-4">
          <div>
            <div className="text-sm text-white/70 mb-1">Original</div>
            <img
              src={`${imageData.data.saved_path}`}
              className="rounded-lg max-w-full h-auto"
            />
          </div>
          {fetchImageEditState.loading && (
            <div className="text-sm text-yellow-200">Generating edit…</div>
          )}
          {fetchImageEditState.error && (
            <div className="text-sm text-red-300">
              {fetchImageEditState.error}
            </div>
          )}
          {editedImages.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="text-sm text-white/70">
                  Edited {editedIndex + 1} / {editedImages.length}
                </div>
                {editedImages.length > 1 && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="px-2 py-1 text-xs rounded border border-white/20 bg-white/10 hover:bg-white/20"
                      onClick={() =>
                        setEditedIndex(
                          (i) =>
                            (i - 1 + editedImages.length) % editedImages.length
                        )
                      }
                    >
                      Prev
                    </button>
                    <button
                      type="button"
                      className="px-2 py-1 text-xs rounded border border-white/20 bg-white/10 hover:bg-white/20"
                      onClick={() =>
                        setEditedIndex((i) => (i + 1) % editedImages.length)
                      }
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
              <img
                src={editedImages[editedIndex]}
                className="rounded-lg max-w-full h-auto"
              />
            </div>
          )}
        </div>
        <div>
          <h5 className="text-white font-semibold text-lg">Menu</h5>
          <div className="mt-4">
            <button
              className="py-2 px-4 rounded-lg border border-white/20 bg-purple-100/20 hover:bg-purple-200 text-white"
              onClick={handleOpenJSONEditor}
            >
              Advanced JSON Editor
            </button>
            <button
              onClick={handleOpenAutoEditor}
              className="py-2 px-4 rounded-lg border border-white/20 bg-purple-100/20 hover:bg-purple-200 text-white"
            >
              Auto-Edit
            </button>
          </div>
        </div>
      </div>
      {editorState.activeEditor === "json" && (
        <JSONEditor
          structuredPromptJson={textAreaJSON}
          promptEntries={promptEntries}
          handleEditJson={handleEditJson}
          fetchEditImage={fetchEditImage}
        />
      )}
      {editorState.activeEditor === "auto-variants" && (
        <AutoVariantEditor
          selectedVariantLabel={currentVariantLabel}
          fetchVariantState={fetchVariantsState}
          imageVariants={variants}
          fetchVariants={fetchVariants}
        />
      )}
    </div>
  );
}
