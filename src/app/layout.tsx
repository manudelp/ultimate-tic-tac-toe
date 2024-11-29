import { SpeedInsights } from "@vercel/speed-insights/next";
import { Toaster } from "@/components/ui/sonner";
import localFont from "next/font/local";
import { config } from "@fortawesome/fontawesome-svg-core";
import "@fortawesome/fontawesome-svg-core/styles.css";
import "./globals.css";
import type { Metadata } from "next";
config.autoAddCss = false;

const spaceGrotesk = localFont({
  src: [
    {
      path: "./fonts/Space_Grotesk/static/SpaceGrotesk-Light.ttf",
      weight: "300",
      style: "normal",
    },
    {
      path: "./fonts/Space_Grotesk/static/SpaceGrotesk-Regular.ttf",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/Space_Grotesk/static/SpaceGrotesk-Medium.ttf",
      weight: "500",
      style: "normal",
    },
    {
      path: "./fonts/Space_Grotesk/static/SpaceGrotesk-SemiBold.ttf",
      weight: "600",
      style: "normal",
    },
    {
      path: "./fonts/Space_Grotesk/static/SpaceGrotesk-Bold.ttf",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-space-grotesk",
});

export const metadata: Metadata = {
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
}>) {
  return (
    <html lang="en">
      <body className={`antialiased ${spaceGrotesk.variable}`}>
        <main>{children}</main>
        <Toaster richColors />
        <SpeedInsights />
      </body>
    </html>
  );
}
