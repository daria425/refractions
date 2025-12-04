import type {
  VariantSchema,
  VariantItem,
  APIFetchState,
  ImageResult,
} from "../types";
import { useState } from "react";

function GeneratedVariantModal({
  variantResults,
  onClose,
}: {
  variantResults: ImageResult[];
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative max-w-4xl max-h-[80vh] overflow-auto bg-white/10 border border-white/20 rounded-xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3 right-3 text-white/70 hover:text-white text-2xl leading-none"
          aria-label="Close"
        >
          ×
        </button>

        <h3 className="text-white text-lg font-semibold mb-4">
          Generated Variants
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {variantResults.map((res, idx) => (
            <div
              key={idx}
              className="border border-white/10 rounded-lg overflow-hidden bg-white/5"
            >
              <img
                src={res.data.saved_path}
                alt={`Variant ${idx + 1}`}
                className="w-full h-auto object-cover"
              />
              <div className="p-2 text-xs text-white/70">
                {res.label || "variant"}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
function StaticButton({
  isDisabled,
  onClick,
}: {
  isDisabled: boolean;
  onClick: () => Promise<void>;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isDisabled}
      className="text-xs px-3 py-1 rounded border border-indigo-400/30 bg-indigo-500/30 hover:bg-indigo-500/40 text-indigo-100"
    >
      Generate All
    </button>
  );
}

// CHANGE: Removed unused SuccessButton (replaced with inline version in ActionButton logic)

function LoadingButton() {
  return (
    <button
      type="button"
      disabled
      className="text-xs px-3 py-1 rounded border border-indigo-400/30 bg-indigo-500/30 text-indigo-100 flex items-center gap-2"
    >
      <svg
        className="animate-spin h-3.5 w-3.5 text-indigo-200"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
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
      Generating…
    </button>
  );
}

function LoadingVariants() {
  return (
    <div className="text-white/70 text-sm italic">Loading variants...</div>
  );
}
function LoadedVariants({
  imageVariants,
  fetchVariants: bulkFetchVariants,
  fetchVariantState,
  selectedVariantLabel,
}: {
  imageVariants: VariantSchema;
  fetchVariants: (variant_label: string) => Promise<void>;
  fetchVariantState: APIFetchState;
  selectedVariantLabel: string | null;
}) {
  const groups: Record<string, VariantItem[]> = imageVariants.groups;
  const [showVariantModal, setShowVariantModal] = useState(false);
  const handleCloseVariantModal = () => {
    setShowVariantModal(false);
  };
  const handleShowVariantModal = () => {
    setShowVariantModal(true);
  };
  return (
    <>
      {Object.entries(groups).map(([groupName, variants]) => {
        // CHANGE: Extract button state logic
        const isLoading =
          fetchVariantState.loading && selectedVariantLabel === groupName;
        const isSuccess =
          fetchVariantState.data &&
          fetchVariantState.data.status === "completed" &&
          selectedVariantLabel === groupName;
        const isDisabled =
          fetchVariantState.loading && selectedVariantLabel !== groupName;

        let ActionButton;
        if (isLoading) {
          ActionButton = <LoadingButton />;
        } else if (isSuccess) {
          ActionButton = (
            <button
              type="button"
              onClick={handleShowVariantModal}
              className="text-xs px-3 py-1 cursor-pointer rounded border border-green-400/30 bg-green-500/30 hover:bg-green-500/40 text-green-100 flex items-center gap-2"
            >
              <svg
                className="h-4 w-4 text-green-200"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 6.293a1 1 0 00-1.414 0L9 12.586l-2.293-2.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l7-7a1 1 0 000-1.414z"
                  clipRule="evenodd"
                />
              </svg>
              View Results
            </button>
          );
        } else {
          ActionButton = (
            <StaticButton
              onClick={() => bulkFetchVariants(groupName)}
              isDisabled={isDisabled}
            />
          );
        }

        return (
          <div
            key={groupName}
            className="border border-white/10 rounded-lg p-3 bg-white/[0.04]"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-white font-medium capitalize">{groupName}</h3>
              {ActionButton}
              {isSuccess &&
                fetchVariantState.data?.results &&
                showVariantModal && (
                  <GeneratedVariantModal
                    variantResults={fetchVariantState.data.results}
                    onClose={handleCloseVariantModal}
                  />
                )}
            </div>
            <div className="flex flex-wrap gap-2">
              {variants.map((v: VariantItem) => (
                <button
                  key={`${groupName}:${v.variant_label}`}
                  type="button"
                  className="px-3 py-1.5 text-sm rounded border border-white/20 bg-white/10 hover:bg-white/20 text-white relative"
                  title={v.description}
                >
                  {v.variant_label}
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
}
export default function AutoVariantEditor({
  imageVariants,
  fetchVariants: bulkFetchVariants,
  fetchVariantState,
  selectedVariantLabel,
}: {
  imageVariants: VariantSchema | null;
  fetchVariants: (variant_label: string) => Promise<void>;
  fetchVariantState: APIFetchState;
  selectedVariantLabel: string | null;
}) {
  return (
    <div className="space-y-6 max-w-6xl  mx-auto bg-white/5 border border-white/10 rounded-xl p-4">
      <h2 className="text-lg font-semibold text-white">Variants</h2>
      {imageVariants ? (
        <LoadedVariants
          imageVariants={imageVariants}
          fetchVariants={bulkFetchVariants}
          fetchVariantState={fetchVariantState}
          selectedVariantLabel={selectedVariantLabel}
        />
      ) : (
        <LoadingVariants />
      )}
    </div>
  );
}
