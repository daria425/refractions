import { useState } from "react";
import { useNavigate } from "react-router";
import type { GeneratedImagesResults } from "../types";
export default function GeneratedImages({ results }: GeneratedImagesResults) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const nav = useNavigate();
  // Filter only successful results with image URLs
  const successfulImages = results.filter(
    (r) => r.status === "ok" && r.data?.image_url
  );

  if (successfulImages.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-purple-200">No images generated successfully.</p>
      </div>
    );
  }

  const currentImage = successfulImages[currentIndex];

  const goToPrevious = () => {
    setCurrentIndex((prev) =>
      prev === 0 ? successfulImages.length - 1 : prev - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prev) =>
      prev === successfulImages.length - 1 ? 0 : prev + 1
    );
  };

  return (
    <div className="space-y-6">
      {/* Image Slider */}
      <div className="relative group max-w-lg mx-auto">
        {/* Main Image Container */}
        <div className="relative aspect-[4/5] bg-white/5 rounded-2xl overflow-hidden border border-white/20">
          <img
            src={currentImage.data!.image_url}
            alt={`${currentImage.shot_type} shot`}
            className="w-full h-full object-contain relative"
          />
          {/* Navigation Arrows */}
          {successfulImages.length > 1 && (
            <>
              {/* Previous Button */}
              <button
                onClick={goToPrevious}
                className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/10 backdrop-blur-md rounded-full border border-white/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/20"
                aria-label="Previous image"
              >
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>

              {/* Next Button */}
              <button
                onClick={goToNext}
                className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/10 backdrop-blur-md rounded-full border border-white/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/20"
                aria-label="Next image"
              >
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </>
          )}
        </div>

        {/* Image Counter */}
        {successfulImages.length > 1 && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 bg-black/60 backdrop-blur-sm rounded-full border border-white/20">
            <p className="text-white text-sm font-medium">
              {currentIndex + 1} / {successfulImages.length}
            </p>
          </div>
        )}
      </div>
      <button
        onClick={() =>
          nav(`/edit/${currentImage.data.request_id}`, { state: currentImage })
        }
        className="text-white font-semibold px-4 py-2 bg-gradient-to-r from-purple-600/90 to-pink-600/90 backdrop-blur-sm rounded-lg border border-white/20"
      >
        Edit
      </button>
      {/* Thumbnail Navigation */}
      {successfulImages.length > 1 && (
        <div className="flex gap-3 justify-center flex-wrap">
          {successfulImages.map((img, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`relative w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                index === currentIndex
                  ? "border-purple-500 scale-110 shadow-lg shadow-purple-500/50"
                  : "border-white/20 hover:border-purple-400/50 opacity-60 hover:opacity-100"
              }`}
            >
              <img
                src={img.data!.saved_path}
                alt={`${img.shot_type} thumbnail`}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end justify-center pb-1">
                <p className="text-white text-xs font-medium capitalize">
                  {img.shot_type}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
