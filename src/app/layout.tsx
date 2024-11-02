import { SpeedInsights } from "@vercel/speed-insights/next";
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const spaceGrotesk = localFont({
  src: "./fonts/Space_Grotesk/static/SpaceGrotesk-Regular.ttf",
  variable: "--font-regular",
  weight: "400",
});
const spaceGroteskBold = localFont({
  src: "./fonts/Space_Grotesk/static/SpaceGrotesk-Bold.ttf",
  variable: "--font-bold",
  weight: "700",
});

export const metadata: Metadata = {
  title: "Ultimate Tic Tac Toe",
  description: "Play Ultimate Tic Tac Toe!",
  openGraph: {
    images: [
      {
        url: "public/icon.png",
        width: 800,
        height: 600,
        alt: "Ultimate Tic Tac Toe",
      },
    ],
    siteName: "Ultimate Tic Tac Toe",
    title: "Ultimate Tic Tac Toe",
    description: "Play Ultimate Tic Tac Toe!",
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
      <body
        className={`antialiased ${spaceGrotesk.variable} ${spaceGroteskBold.variable}`}
      >
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
