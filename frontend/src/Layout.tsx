export default function Layout({ children }: { children: React.ReactNode }) {
  // # CHANGE: use custom linear gradient background
  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: "#0c0024",
        background:
          "linear-gradient(10deg, rgba(12, 0, 36, 1) 0%, rgba(26, 4, 63, 1) 35%, rgba(51, 1, 81, 1) 100%)",
      }}
    >
      {children}
    </div>
  );
}
