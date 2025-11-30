import { useState } from "react";
import type { VariantSchema, VariantItem } from "../types";

type GroupName = string;

export default function AutoVariantEditor({
  imageVariants,
}: {
  imageVariants: VariantSchema;
}) {
  // Track which description is expanded per group+label
  const [openInfo, setOpenInfo] = useState<Record<string, boolean>>({});

  const toggleInfo = (group: GroupName, label: string) => {
    const key = `${group}:${label}`;
    setOpenInfo((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  if (!imageVariants || !imageVariants.groups) {
    return <div className="text-sm text-white/70">No variants available</div>;
  }

  const groups: Record<string, VariantItem[]> = imageVariants.groups;

  return (
    <div className="space-y-6">
      {Object.entries(groups).map(([groupName, variants]) => (
        <div
          key={groupName}
          className="bg-white/5 border border-white/10 rounded-xl p-4"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-white font-semibold text-base capitalize">
              {groupName}
            </h3>
            <span className="text-xs text-white/50">
              {(variants as VariantItem[]).length} options
            </span>
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            {(variants as VariantItem[]).map((v: VariantItem) => {
              const key = `${groupName}:${v.variant_label}`;
              const isOpen = !!openInfo[key];
              return (
                <div key={key} className="inline-flex items-center gap-2">
                  <button
                    type="button"
                    className="px-3 py-1.5 text-sm rounded border border-white/20 bg-white/10 hover:bg-white/20 text-white"
                  >
                    {v.variant_label}
                  </button>
                  <button
                    type="button"
                    aria-label="info"
                    className="px-2 py-1 text-xs rounded border border-white/20 bg-white/10 hover:bg-white/20 text-white"
                    onClick={() => toggleInfo(groupName, v.variant_label)}
                  >
                    i
                  </button>
                  {isOpen && (
                    <div className="ml-1 max-w-md text-xs text-white/80 bg-white/5 border border-white/10 rounded px-2 py-1">
                      {v.description}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
