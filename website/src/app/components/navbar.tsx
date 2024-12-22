"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"

export function Navbar() {
  return (
    <motion.nav 
      className="fixed w-full z-50 backdrop-blur-sm bg-black/30 border-b border-[#00ff94]/20"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100 }}
    >
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold text-[#00ff94] glitch-text">
            grim-repor:$<span className="animate-pulse">_</span>
          </span>
        </Link>
        <div className="flex items-center space-x-4">
          
          <Link href = "/waitlist">
          <Button className="bg-[#00ff94] text-black hover:bg-[#00ff94]/90 font-bold text-lg shadow-neon">
            ./fix-my-repo
          </Button>
          </Link>
        </div>
      </div>
    </motion.nav>
  )
}

