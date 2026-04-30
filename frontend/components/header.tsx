"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, ShieldCheck } from "lucide-react"

import { AuthDialog } from "@/components/auth-dialogs"
import { HeaderSearch } from "@/components/header-search"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button, buttonVariants } from "@/components/ui/button"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { cn } from "@/lib/utils"
import CreatePostDialog from "./create-post-dialog"

const navItems = [
  { href: "/news", label: "News" },
  { href: "/timeline", label: "News Timeline" },
  { href: "/analytics", label: "Analytics" },
  { href: "/agent-config", label: "Configure Agent" },
  { href: "/admin", label: "Admin" },
]

function NavLinks({ className }: { className?: string }) {
  return (
    <nav className={cn("flex items-center gap-1", className)}>
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            buttonVariants({ variant: "ghost", size: "sm" }),
            "text-muted-foreground hover:text-foreground"
          )}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  )
}

export function Header() {
  const pathname = usePathname()

  if (pathname === "/") {
    return null
  }

  return (
    <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-heading text-base font-semibold">
          Pulse
        </Link>

        <div className="hidden items-center gap-3 md:flex">
          <HeaderSearch />
          {/* <CreatePostDialog /> */}
          <NavLinks />
          <div className="h-6 w-px bg-border" />
          <ThemeToggle />
          <AuthDialog />
        </div>

        <Sheet>
          <SheetTrigger render={<Button variant="outline" size="icon" className="md:hidden" />}>
            <Menu className="size-4" />
            <span className="sr-only">Open menu</span>
          </SheetTrigger>
          <SheetContent className="w-[min(22rem,calc(100vw-2rem))]">
            <SheetHeader>
              <SheetTitle className="flex items-center gap-2">
                <ShieldCheck className="size-4" />
                Pulse
              </SheetTitle>
            </SheetHeader>
            <div className="grid gap-2 px-4">
              {navItems.map((item) => (
                <SheetClose
                  key={item.href}
                  render={
                    <Link
                      href={item.href}
                      className={cn(
                        buttonVariants({ variant: "ghost" }),
                        "w-full justify-start"
                      )}
                    />
                  }
                >
                  {item.label}
                </SheetClose>
              ))}
            </div>
            <div className="mt-auto grid gap-2 p-4">
              <HeaderSearch />
              <div className="flex items-center justify-between rounded-lg border p-2">
                <span className="text-sm font-medium">Theme</span>
                <ThemeToggle />
              </div>
              <AuthDialog />
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  )
}
