import { SpeedInsights } from "@vercel/speed-insights/next";
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

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
        url: "/icon.png",
        width: 800,
        height: 600,
        alt: "Ultimate Tic Tac Toe Logo",
      },
    ],
    siteName: "Ultimate Tic Tac Toe",
    title: "Ultimate Tic Tac Toe - The Ultimate Strategy Game",
    description:
      "Engage in the ultimate strategy challenge with Ultimate Tic Tac Toe. Test your skills and outsmart your opponents in this advanced version of the classic game.",
    url: "https://utictactoe.vercel.app",
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
        <SpeedInsights />
      </body>
    </html>
  );
}
