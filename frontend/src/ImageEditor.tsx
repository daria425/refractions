import { useLocation, useParams } from "react-router";
import JSONEditor from "./components/JSONEditor";
import AutoVariantEditor from "./components/AutoVariantEditor";
import EditedImagesContainer from "./components/EditedImagesContainer";
import type {
  ImageResult,
  EditorState,
  APIFetchState,
  EditedImageEntry,
} from "./types";
import { flattenStructuredPrompt } from "./utils";
import { useEffect, useMemo, useState } from "react";
import useVariantData from "./hooks/useVariantData";
import apiClient from "./api/apiClient";
import { Sparkle } from "lucide-react";
import { X, PanelTopOpen } from "lucide-react";

function ContextMenu({
  isOpen,
  onClose,
  title,
  description,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />
      {/* Slide-in panel */}
      <div className="fixed right-0 top-0 z-50 h-full w-full max-w-2xl bg-gradient-to-br from-purple-900/95 to-indigo-900/95 border-l border-white/20 shadow-2xl overflow-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-2xl font-semibold text-white">{title}</h2>
              {description && (
                <p className="text-sm text-white/70 mt-1">{description}</p>
              )}
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-white/70 hover:text-white"
              aria-label="Close"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          {/* Content */}
          <div>{children}</div>
        </div>
      </div>
    </>
  );
}
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

  const [fetchAIEditImageState, setFetchAIEditImageState] =
    useState<APIFetchState>({
      loading: false,
      error: null,
      data: null,
    });

  const [currentVariantLabel, setCurrentVariantLabel] = useState<string | null>(
    null
  );
  // # CHANGE: track edited previews with their structured prompts for compare mode
  const [editedImages, setEditedImages] = useState<EditedImageEntry[]>([]);
  const [editedIndex, setEditedIndex] = useState(0);
  const [showCompareJSON, setShowCompareJSON] = useState(false);

  const promptEntries = flattenStructuredPrompt(
    imageData.data.structured_prompt
  );
  const [textAreaJSON, setTextAreaJSON] = useState(
    JSON.stringify(imageData.data.structured_prompt, null, 2)
  );
  // # CHANGE: precompute formatted JSON snippets for quick compare toggles
  const originalStructuredPrompt = useMemo(() => {
    try {
      return JSON.stringify(imageData.data.structured_prompt, null, 2);
    } catch (error) {
      console.error("Could not stringify original structured prompt", error);
      return "";
    }
  }, [imageData.data.structured_prompt]);

  const currentEditedJSON = useMemo(() => {
    const entry = editedImages[editedIndex];
    if (!entry?.structured_prompt) return null;
    try {
      return JSON.stringify(entry.structured_prompt, null, 2);
    } catch (error) {
      console.error("Could not stringify edited structured prompt", error);
      return null;
    }
  }, [editedImages, editedIndex]);

  useEffect(() => {
    if (editedImages.length === 0) {
      setEditedIndex(0);
    }
  }, [editedImages.length]);

  useEffect(() => {
    if (editedImages.length === 0 && showCompareJSON) {
      setShowCompareJSON(false);
    }
  }, [editedImages.length, showCompareJSON]);
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

  const handleImageChange = (editedIdx: number) => {
    setEditedIndex(editedIdx);
  };
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
      const responsePayload = response?.data?.data;
      const newPath = responsePayload?.saved_path || responsePayload?.image_url;
      if (newPath) {
        const nextEntry: EditedImageEntry = {
          path: newPath,
          structured_prompt: responsePayload?.structured_prompt,
          seed: responsePayload?.seed,
        };
        setEditedImages((prev) => {
          const next = [...prev, nextEntry];
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
    // add selected variant list here
    const requestBody = {
      structured_prompt: imageData.data.structured_prompt,
      shot_type: imageData.shot_type,
      seed: imageData.data.seed,
      selected_variant_list: variants?.groups[selectedVariantLabel] || [],
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

  const fetchAIEditImage = async () => {
    setFetchAIEditImageState({
      loading: true,
      error: null,
      data: null,
    });
    try {
      const response = await apiClient.get(`/shots/${request_id}/critique`);
      console.log("AI Edit response", response.data);
      setFetchAIEditImageState({
        loading: false,
        error: null,
        data: response.data,
      });
      const responsePayload = response?.data?.data;
      const newPath = responsePayload?.saved_path || responsePayload?.image_url;
      if (newPath) {
        const nextEntry: EditedImageEntry = {
          path: newPath,
          structured_prompt: responsePayload?.structured_prompt,
          seed: responsePayload?.seed,
        };
        setEditedImages((prev) => {
          const next = [...prev, nextEntry];
          setEditedIndex(next.length - 1);
          return next;
        });
      }
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "AI Edit generation failed";
      console.error("AI Edit generation failed:", message, err);
      setFetchAIEditImageState({ loading: false, error: message, data: null });
    }
  };
  return (
    <div className="px-8 py-4 2xl:flex relative">
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-8 border border-white/20 max-w-6xl mx-auto gap-8">
        {editedImages.length > 0 && (
          <button
            type="button"
            onClick={() => setShowCompareJSON((prev) => !prev)}
            aria-pressed={showCompareJSON}
            className={`py-2 px-4 rounded-lg border border-white/20 flex items-center gap-2 transition-colors ${showCompareJSON ? "bg-purple-500/80 text-white" : "text-white hover:bg-purple-400/10"}`}
          >
            {showCompareJSON ? "Back to Images" : "Compare JSON"}
            <PanelTopOpen className="w-4 h-4" />
          </button>
        )}
        <div className="flex gap-4">
          <div>
            <div className="text-sm text-white/70 mb-1">Original</div>
            {showCompareJSON ? (
              <pre className="rounded-lg border border-white/10 bg-black/50 p-4 text-left text-xs text-emerald-100 max-w-xl max-h-[520px] overflow-auto whitespace-pre-wrap break-words">
                {originalStructuredPrompt || "Structured prompt unavailable."}
              </pre>
            ) : (
              <img
                src={`${imageData.data.saved_path}`}
                className="rounded-lg max-w-full h-auto"
              />
            )}
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
            <EditedImagesContainer
              handleImageChange={handleImageChange}
              editedImages={editedImages}
              editedIndex={editedIndex}
              showCompareJSON={showCompareJSON}
              currentEditedJSON={currentEditedJSON}
            />
          )}
        </div>
        <div>
          <h5 className="text-white font-semibold text-lg">Menu</h5>
          <div className="mt-4 gap-4 flex">
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
            <button
              onClick={fetchAIEditImage}
              disabled={fetchAIEditImageState.loading}
              className="py-2 flex gap-2 px-4 rounded-lg border border-white/20 bg-purple-400 hover:bg-purple-500 text-white"
            >
              {fetchAIEditImageState.loading ? (
                <>
                  <svg
                    className="animate-spin h-4 w-4 text-white"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-90"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                    />
                  </svg>
                  Improving…
                </>
              ) : (
                <>
                  Improve with AI
                  <Sparkle />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
      <ContextMenu
        isOpen={editorState.activeEditor === "json"}
        onClose={handleCloseEditor}
        title="Advanced JSON Editor"
        description="Open the structured FIBO prompt as JSON for precise, parameter-level editing (camera, lighting, color, composition). Instant preview on apply."
      >
        <JSONEditor
          structuredPromptJson={textAreaJSON}
          promptEntries={promptEntries}
          handleEditJson={handleEditJson}
          fetchEditImage={fetchEditImage}
        />
      </ContextMenu>

      <ContextMenu
        isOpen={editorState.activeEditor === "auto-variants"}
        onClose={handleCloseEditor}
        title="Auto-Edit"
        description="Pick a variant set (e.g., lighting or camera) and generate deterministic refinements with your current seed. One‑click 'Generate All' or single option."
      >
        <AutoVariantEditor
          selectedVariantLabel={currentVariantLabel}
          fetchVariantState={fetchVariantsState}
          imageVariants={variants}
          fetchVariants={fetchVariants}
        />
      </ContextMenu>
    </div>
  );
}
