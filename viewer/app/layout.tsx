import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Math Flow · Research Atlas",
  description: "Explore a mathematical research ledger, hierarchical knowledge state, and immutable adjudication history.",
  openGraph: {
    title: "Math Flow · Research Atlas",
    description: "Research evolves. History remains.",
    images: [{ url: "/math-flow-research-atlas.png", width: 1731, height: 909 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Math Flow · Research Atlas",
    description: "Research evolves. History remains.",
    images: ["/math-flow-research-atlas.png"],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className={`${geistSans.variable} ${geistMono.variable}`}>{children}</body></html>;
}
