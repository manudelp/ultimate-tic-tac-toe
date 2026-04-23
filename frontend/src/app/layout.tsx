import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Toaster } from "@/components/ui/sonner";
import { Space_Grotesk } from "next/font/google";
import type { Metadata } from "next";
import Header from "@/components/layout/header";
import Footer from "@/components/layout/footer";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-space-grotesk",
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.VERCEL_URL
      ? `https://${process.env.VERCEL_URL}`
      : "https://utictactoe.online"
  ),
  title: "Ultimate Tic Tac Toe - The Ultimate Strategy Game",
  description:
    "Engage in the ultimate strategy challenge with Ultimate Tic Tac Toe. Test your skills and outsmart your opponents in this advanced version of the classic game.",
  openGraph: {
    images: [
      {
        url: "/og_img.jpg",
        width: 1200,
        height: 630,
        alt: "Ultimate Tic Tac Toe Logo",
      },
    ],
    siteName: "Ultimate Tic Tac Toe",
    title: "Ultimate Tic Tac Toe - The Ultimate Strategy Game",
    description:
      "Engage in the ultimate strategy challenge with Ultimate Tic Tac Toe. Test your skills and outsmart your opponents in this advanced version of the classic game.",
    url: "https://utictactoe.online",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body className={`antialiased ${spaceGrotesk.variable}`}>
        <Header />
        <main className="min-h-svh pt-10 sm:pt-0">{children}</main>
        <Toaster richColors />
        <Footer />
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  );
}
