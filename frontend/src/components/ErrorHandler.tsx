interface ErrorHandlerProps {
  message: string;
}

export default function ErrorHandler({ message }: ErrorHandlerProps) {
  return (
    <div className="w-full py-8 px-6">
      <div className="relative overflow-hidden bg-gradient-to-br from-red-950/40 via-rose-900/30 to-red-950/40 backdrop-blur-sm rounded-xl border border-red-800/30 shadow-lg">
        {/* Subtle animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_rgba(239,68,68,0.1),transparent_50%)] animate-pulse" />
        </div>
        <div className="relative flex items-start gap-4 p-6">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-red-200 mb-2">
              Something went wrong
            </h3>
            <p className="text-sm text-red-300/90 leading-relaxed break-words">
              {message}
            </p>
          </div>
        </div>
        <div className="h-1 bg-gradient-to-r from-transparent via-red-600/50 to-transparent" />
      </div>
    </div>
  );
}
