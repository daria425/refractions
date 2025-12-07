import { X } from "lucide-react";
import { useMemo } from "react";

// # CHANGE: Helper to highlight diff lines
function highlightDiff(obj1: any, obj2: any): string {
  const lines1 = JSON.stringify(obj1, null, 2).split("\n");
  const lines2 = JSON.stringify(obj2, null, 2).split("\n");
  const maxLines = Math.max(lines1.length, lines2.length);

  const result: string[] = [];
  for (let i = 0; i < maxLines; i++) {
    const line =
      (i < lines1.length ? lines1[i] : "") ||
      (i < lines2.length ? lines2[i] : "");
    result.push(line);
  }
  return result.join("\n");
}

function HighlightedJSON({ obj, otherObj }: { obj: any; otherObj: any }) {
  const lines = useMemo(() => {
    const thisLines = JSON.stringify(obj, null, 2).split("\n");
    const otherLines = JSON.stringify(otherObj, null, 2).split("\n");
    return thisLines.map((line, idx) => ({
      text: line,
      isDifferent: otherLines[idx] !== line,
    }));
  }, [obj, otherObj]);

  return (
    <pre className="flex-1 text-xs text-emerald-100 bg-black/50 p-4 rounded-lg border border-white/10 overflow-y-auto overflow-x-hidden whitespace-pre-wrap break-words">
      {lines.map((line, idx) => (
        <div
          key={idx}
          className={line.isDifferent ? "font-bold text-yellow-200" : ""}
        >
          {line.text}
        </div>
      ))}
    </pre>
  );
}

export default function JsonDiffViewer({
  structuredPrompt1,
  structuredPrompt2,
  onClose,
}: {
  structuredPrompt1: Record<string, any>;
  structuredPrompt2: Record<string, any>;
  onClose: () => void;
}) {
  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      {/* Modal */}
      <div className="fixed inset-4 z-50 bg-gradient-to-br from-purple-900/95 to-indigo-900/95 border border-white/20 shadow-2xl rounded-xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/20">
          <h2 className="text-xl font-semibold text-white">JSON Comparison</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-white/70 hover:text-white"
            aria-label="Close"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        {/* Split view */}
        <div className="flex-1 grid grid-cols-2 gap-4 p-4 overflow-hidden">
          <div className="flex flex-col overflow-hidden">
            <h3 className="text-sm text-white/70 mb-2">Original</h3>
            <HighlightedJSON
              obj={structuredPrompt1}
              otherObj={structuredPrompt2}
            />
          </div>
          <div className="flex flex-col overflow-hidden">
            <h3 className="text-sm text-white/70 mb-2">Edited</h3>
            <HighlightedJSON
              obj={structuredPrompt2}
              otherObj={structuredPrompt1}
            />
          </div>
        </div>
      </div>
    </>
  );
}
