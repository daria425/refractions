export default function Layout({ children }: { children: React.ReactNode }) {
  // # CHANGE: use custom linear gradient background
  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: "#0c0024",
        background:
          "linear-gradient(10deg, rgba(12, 0, 36, 1) 0%, rgba(50, 9, 121, 1) 35%, rgba(109, 2, 176, 1) 100%)",
      }}
    >
      {children}
    </div>
  );
}
