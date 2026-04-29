"use client"

import { usePathname } from "next/navigation"

import { Header } from "@/components/header"
import { cn } from "@/lib/utils"

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const isHome = pathname === "/"

  if (isHome) {
    return children
  }

  return (
    <>
      <Header />
      <main className={cn("mx-auto flex w-full max-w-7xl flex-1 flex-col border-x")}>
        {children}
      </main>
    </>
  )
}
