import { Toaster } from "@/components/ui/sonner";
import { Space_Grotesk } from "next/font/google";
import type { Metadata } from "next";
import Header from "@/components/layout/header";
import ThemeProvider from "@/components/ui/theme-provider";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-space-grotesk",
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://utictactoe.com.ar";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Ultimate Tic Tac Toe",
    template: "%s | Ultimate Tic Tac Toe",
  },
  description:
    "The ultimate strategy game. Play against AI or challenge friends online in this advanced twist on classic Tic Tac Toe.",
  openGraph: {
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "Ultimate Tic Tac Toe" }],
    siteName: "Ultimate Tic Tac Toe",
    type: "website",
  },
  twitter: { card: "summary_large_image" },
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/icon.png", sizes: "512x512", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.ReactElement {
  return (
    <html lang="en" data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#111827" />
      </head>
      <body className={`antialiased ${spaceGrotesk.variable}`}>
        <ThemeProvider>
          <Header />
          <main>{children}</main>
          <Toaster richColors />
        </ThemeProvider>
      </body>
    </html>
  );
}
