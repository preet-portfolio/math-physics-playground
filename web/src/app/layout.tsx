import type { Metadata } from "next";
import { Kalam, JetBrains_Mono } from "next/font/google";
import { Nav } from "@/components/Nav";
import "./globals.css";

// Web-safe stand-ins for the desktop app's macOS-only chalk fonts (Chalkboard
// SE / Chalkduster) -- next/font/google guarantees these load identically
// for every visitor, unlike relying on locally-installed system fonts.
const kalam = Kalam({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Math & Physics Playground",
  description: "Interactive math and physics demos, in your browser.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${kalam.variable} ${jetbrainsMono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col bg-[#1B2B22] text-[#EDEAE0] md:flex-row">
        <Nav />
        <main className="min-w-0 flex-1 overflow-y-auto">{children}</main>
      </body>
    </html>
  );
}
