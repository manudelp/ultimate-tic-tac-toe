import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-svh p-6 text-center">
      <h1 className="text-5xl font-bold text-red-400 mb-4">404</h1>
      <p className="text-muted-foreground mb-6">Page not found</p>
      <Link
        href="/"
        className="px-6 py-2 bg-card hover:bg-surface-hover rounded-lg transition-colors"
      >
        Go home
      </Link>
    </div>
  );
}
