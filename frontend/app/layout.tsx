import React from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "E2B Browser Use Chat",
  description: "Chat with AI to control your browser in E2B sandbox",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning>
        <Toaster position="top-center" reverseOrder={false} />
        <main className="min-h-screen">{children}</main>
      </body>
    </html>
  );
}