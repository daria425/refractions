import type { VariantSchema, VariantItem } from "../types";

type GroupName = string;

export default function AutoVariantEditor({
  imageVariants,
  fetchVariants,
}: {
  imageVariants: VariantSchema;
  fetchVariants: (variant_label: string) => Promise<void>;
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
            <button
              type="button"
              onClick={() => fetchVariants(groupName)}
              className="text-xs px-3 py-1 rounded border border-indigo-400/30 bg-indigo-500/30 hover:bg-indigo-500/40 text-indigo-100"
            >
              Generate All
            </button>
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
