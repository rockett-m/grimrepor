import type { Metadata } from "next"
import { JetBrains_Mono } from 'next/font/google'
import "./globals.css"
import { Navbar } from "./components/navbar"

const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Grim-Repor | Reviving Dead Repositories",
  description: "AI-powered tool that brings your broken dependencies back to life",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${jetbrainsMono.className} bg-black`}>
        <div className="min-h-screen bg-[#000]/90 text-[#00ff94]">
          <div className="fixed inset-0 bg-[url('/grid.svg')] bg-repeat [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] pointer-events-none" />
          <div className="scanline" />
          <Navbar />
          {children}
        </div>
      </body>
    </html>
  )
}

