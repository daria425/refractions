export default function EditedImagesContainer({
  editedImages,
  editedIndex,
  handleImageChange,
}: {
  editedImages: string[];
  handleImageChange: (editedIdx: number) => void;
  editedIndex: number;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <div className="text-sm text-white/70">
          Edited {editedIndex + 1} / {editedImages.length}
        </div>
        {editedImages.length > 1 && (
          <div className="flex gap-2">
            <button
              type="button"
              className="px-2 py-1 text-xs rounded border border-white/20 bg-white/10 hover:bg-white/20"
              onClick={() =>
                handleImageChange(
                  (editedIndex - 1 + editedImages.length) % editedImages.length
                )
              }
              disabled={editedImages.length === 1}
            >
              Prev
            </button>
            <button
              type="button"
              className="px-2 py-1 text-xs rounded border border-white/20 bg-white/10 hover:bg-white/20"
              onClick={() =>
                handleImageChange((editedIndex + 1) % editedImages.length)
              }
              disabled={editedImages.length === 1}
            >
              Next
            </button>
          </div>
        )}
      </div>
      <img
        src={editedImages[editedIndex]}
        className="rounded-lg max-w-full h-auto"
      />
    </div>
  );
}
