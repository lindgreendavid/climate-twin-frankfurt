import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Climate Twin Frankfurt — the Frankfurt urban heat island, measured",
  description:
    "An accessible reanalysis of real DWD station records comparing urban Frankfurt (Westend) against DWD's own designated rural/reference counterpart station, with uncertainty shown before any warming or trend conclusion.",
  applicationName: "Climate Twin Frankfurt",
  keywords: [
    "urban heat island",
    "Frankfurt",
    "DWD",
    "climate data",
    "urban climate",
    "reproducible research",
    "web accessibility",
  ],
  openGraph: {
    title: "Climate Twin Frankfurt",
    description:
      "How much warmer is urban Frankfurt than DWD's own rural/reference counterpart station, with what uncertainty? A reproducible reanalysis of real DWD daily records.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Climate Twin Frankfurt",
    description:
      "A reproducible reanalysis of Frankfurt's urban heat island using real DWD station data.",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>{children}</body>
    </html>
  );
}
