import { useState } from "react";

export default function InitialImageForm({
  handleSubmit,
}: {
  handleSubmit: (e: React.FormEvent, vision: string, image: File) => void;
}) {
  const [vision, setVision] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };
  return (
    <form
      onSubmit={(e) => {
        if (image) {
          handleSubmit(e, vision, image);
        }
      }}
      className="space-y-6"
    >
      <div>
        <label
          htmlFor="vision"
          className="block text-sm font-medium text-white mb-2"
        >
          Campaign Vision
        </label>
        <textarea
          id="vision"
          value={vision}
          onChange={(e) => setVision(e.target.value)}
          placeholder="Describe your creative vision (e.g., 'Oriental maximalism, vibrant, gold accents, intricate patterns')"
          className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          rows={4}
          required
        />
      </div>
      <div>
        <label
          htmlFor="image"
          className="block text-sm font-medium text-white mb-2"
        >
          Upload CAD Design
        </label>
        <div className="flex items-center justify-center w-full">
          <label
            htmlFor="image"
            className="flex flex-col items-center justify-center w-full h-48 border-2 border-white/30 border-dashed rounded-lg cursor-pointer bg-white/5 hover:bg-white/10 transition-colors"
          >
            {imagePreview ? (
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-full object-contain rounded-lg"
              />
            ) : (
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg
                  className="w-10 h-10 mb-3 text-purple-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <p className="mb-2 text-sm text-purple-200">
                  <span className="font-semibold">Click to upload</span> or drag
                  and drop
                </p>
                <p className="text-xs text-purple-300/70">
                  PNG, JPG or JPEG (MAX. 10MB)
                </p>
              </div>
            )}
            <input
              id="image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
              required
            />
          </label>
        </div>
        {image && (
          <p className="mt-2 text-sm text-purple-200">Selected: {image.name}</p>
        )}
      </div>
      <button
        type="submit"
        className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-600 hover:to-pink-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all shadow-lg hover:shadow-xl"
      >
        Generate Images
      </button>
    </form>
  );
}
