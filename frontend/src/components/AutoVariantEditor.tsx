import type { VariantSchema, VariantItem, APIFetchState } from "../types";

type GroupName = string;

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

export default function AutoVariantEditor({
  imageVariants,
  fetchVariants,
  fetchVariantState,
  selectedVariantLabel,
}: {
  imageVariants: VariantSchema;
  fetchVariants: (variant_label: string) => Promise<void>;
  fetchVariantState: APIFetchState;
  selectedVariantLabel: string | null;
}) {
  const groups: Record<string, VariantItem[]> = imageVariants.groups;

  return (
    <div className="space-y-6 max-w-6xl  mx-auto bg-white/5 border border-white/10 rounded-xl p-4">
      <h2 className="text-lg font-semibold text-white">Variants</h2>
      {Object.entries(groups).map(([groupName, variants]) => (
        <div
          key={groupName}
          className="border border-white/10 rounded-lg p-3 bg-white/[0.04]"
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white font-medium capitalize">{groupName}</h3>
            {fetchVariantState.loading && selectedVariantLabel === groupName ? (
              <LoadingButton />
            ) : (
              <StaticButton
                onClick={() => fetchVariants(groupName)}
                isDisabled={
                  fetchVariantState.loading &&
                  selectedVariantLabel !== groupName
                }
              />
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {variants.map((v: VariantItem) => (
              <button
                key={`${groupName}:${v.variant_label}`}
                type="button"
                onClick={() => fetchVariants(v.variant_label)}
                className="px-3 py-1.5 text-sm rounded border border-white/20 bg-white/10 hover:bg-white/20 text-white relative"
                title={v.description}
              >
                {v.variant_label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
