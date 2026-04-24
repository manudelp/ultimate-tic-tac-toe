import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Toaster } from "@/components/ui/sonner";
import { Space_Grotesk } from "next/font/google";
import type { Metadata } from "next";
import Sidebar from "@/components/layout/sidebar";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-space-grotesk",
});

const siteUrl = process.env.VERCEL_PROJECT_PRODUCTION_URL
  ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
  : process.env.VERCEL_URL
  ? `https://${process.env.VERCEL_URL}`
  : "https://utictactoe.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Ultimate Tic Tac Toe",
    template: "%s | Ultimate Tic Tac Toe",
  },
  description:
    "The ultimate strategy game. Play against AI or challenge friends online in this advanced twist on classic Tic Tac Toe.",
  openGraph: {
    images: [{ url: "/og_img.jpg", width: 1200, height: 630, alt: "Ultimate Tic Tac Toe" }],
    siteName: "Ultimate Tic Tac Toe",
    type: "website",
  },
  twitter: { card: "summary_large_image" },
  icons: { icon: "/icon.png" },
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.ReactElement {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <head>
        <meta name="theme-color" content="#111827" />
      </head>
      <body className={`antialiased ${spaceGrotesk.variable}`}>
        <Sidebar />
        <main className="md:ml-48 pb-14 md:pb-0 min-h-svh">{children}</main>
        <Toaster richColors />
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  );
}
