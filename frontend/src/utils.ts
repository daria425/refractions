import type { PromptEntry } from "./types";
function flattenStructuredPrompt(
  obj: Record<string, any>,
  parentKey = ""
): PromptEntry[] {
  // # CHANGE: explicitly type entries and function return to avoid implicit any[]
  const entries: PromptEntry[] = [];

  Object.entries(obj).forEach(([key, value]) => {
    const path = parentKey ? `${parentKey}.${key}` : key;

    // CHANGE: Convert snake_case to readable labels
    const label = key
      .replace(/_/g, " ")
      .replace(/^./, (str) => str.toUpperCase());

    entries.push({
      label,
      value,
      path,
    });
  });

  return entries;
}

export { flattenStructuredPrompt };
