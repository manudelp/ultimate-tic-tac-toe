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
      </body>
    </html>
  );
}
