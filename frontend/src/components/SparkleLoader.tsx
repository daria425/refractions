export default function SparkleLoader() {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      {/* Sparkle Container */}
      <div className="relative w-32 h-32 mb-6">
        {/* Central Glow */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 rounded-full blur-xl opacity-60 animate-pulse" />

        {/* Rotating Sparkles */}
        <div className="absolute inset-0 animate-spin-slow">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="absolute w-3 h-3 bg-white rounded-full shadow-lg shadow-purple-400/50"
              style={{
                top: "50%",
                left: "50%",
                transform: `rotate(${i * 45}deg) translateY(-48px) scale(${
                  1 + (i % 2) * 0.3
                })`,
                animation: `sparkle 2s ease-in-out ${i * 0.2}s infinite`,
              }}
            />
          ))}
        </div>

        {/* Inner Rotating Ring */}
        <div className="absolute inset-4 animate-spin-reverse">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-gradient-to-br from-pink-300 to-purple-300 rounded-full"
              style={{
                top: "50%",
                left: "50%",
                transform: `rotate(${i * 60}deg) translateY(-32px)`,
                animation: `twinkle 1.5s ease-in-out ${i * 0.15}s infinite`,
              }}
            />
          ))}
        </div>

        {/* Center Star */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-full animate-pulse shadow-lg shadow-purple-400" />
        </div>
      </div>

      {/* Text */}
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold text-white animate-pulse">
          Generating
        </h3>
        <p className="text-purple-200 text-sm">
          Creating your campaign images...
        </p>
      </div>

      {/* Inline styles for custom animations */}
      <style>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        @keyframes spin-reverse {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }
        
        @keyframes sparkle {
          0%, 100% { opacity: 1; transform: rotate(var(--rotation)) translateY(-48px) scale(1); }
          50% { opacity: 0.3; transform: rotate(var(--rotation)) translateY(-48px) scale(0.6); }
        }
        
        @keyframes twinkle {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.2; }
        }
        
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
        
        .animate-spin-reverse {
          animation: spin-reverse 2s linear infinite;
        }
      `}</style>
    </div>
  );
}
