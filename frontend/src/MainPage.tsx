import { useState } from "react";
import type { APIFetchState } from "./types";
import apiClient from "./api/apiClient";
import InitialImageForm from "./components/InitialImageForm";
import SparkleLoader from "./components/SparkleLoader";
import ErrorHandler from "./components/ErrorHandler";
import IdleStateHandler from "./components/IdleStateHandler";
import GeneratedImages from "./components/GeneratedImages";
import type { GenerationSuccessResponse } from "./types";
// # CHANGE: Wrapped API call in try/catch to handle errors and set submitState on failure

function FetchStateDisplay({ submitState }: { submitState: APIFetchState }) {
  // Determine current state
  const isIdle =
    !submitState.loading && !submitState.data && !submitState.error;
  const isLoading = submitState.loading;
  const isError = !!submitState.error;
  const isSuccess = !!submitState.data;

  // Switch based on state
  if (isIdle) {
    return (
      <IdleStateHandler text="Your generated images will appear here..." />
    );
  }

  if (isLoading) {
    return <SparkleLoader />;
  }

  if (isError) {
    return <ErrorHandler message={submitState.error || "Unknown error"} />;
  }

  if (isSuccess) {
    return <GeneratedImages results={submitState.data!.results} />;
  }

  return null;
}

export default function Main() {
  const [submitState, setSubmitState] = useState<APIFetchState>({
    loading: false,
    error: null,
    data: null,
  });
  const handleSubmit = async (
    e: React.FormEvent,
    vision: string,
    image: File
  ) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("vision", vision);
    formData.append("image_file", image);
    console.log("Form submitted:", { vision, image });
    setSubmitState({
      loading: true,
      data: null,
      error: null,
    });

    try {
      const response = await apiClient.post<{
        data: GenerationSuccessResponse;
      }>("/generate", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setSubmitState({
        loading: false,
        data: response.data,
        error: null,
      });
    } catch (err: unknown) {
      console.error("Generation error:", err);
      const message = err instanceof Error ? err.message : String(err);
      setSubmitState({
        loading: false,
        data: null,
        error: message,
      });
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 lg:flex lg:justify-center lg:gap-8">
      <div>
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Refractions</h1>
          <p className="text-xl text-purple-200">
            See your design come to life instantly
          </p>
        </div>
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
          <InitialImageForm handleSubmit={handleSubmit} />
        </div>
      </div>
      <div className="max-w-6xl mx-auto mt-12 lg:mt-0">
        <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4">
            Generated Images
          </h2>
          <FetchStateDisplay submitState={submitState} />
        </div>
      </div>
    </div>
  );
}
