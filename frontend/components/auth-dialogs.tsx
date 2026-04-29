"use client"

import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

function Field({
  id,
  label,
  type = "text",
  placeholder,
}: {
  id: string
  label: string
  type?: string
  placeholder: string
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input id={id} type={type} placeholder={placeholder} />
    </div>
  )
}

export function AuthDialog() {
  const [mode, setMode] = useState<"login" | "register">("login")
  const isLogin = mode === "login"

  return (
    <Dialog>
      <DialogTrigger render={<Button />}>Login / Register</DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isLogin ? "Login" : "Create account"}</DialogTitle>
          <DialogDescription>
            {isLogin
              ? "Access your Pulse workspace with your registered email."
              : "Register a team account to manage news publishing."}
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 rounded-lg border bg-muted p-1">
          <Button
            type="button"
            variant="ghost"
            className={cn(
              "text-muted-foreground hover:text-foreground",
              isLogin
                ? "bg-background text-foreground shadow-sm hover:bg-background"
                : "hover:bg-transparent"
            )}
            onClick={() => setMode("login")}
          >
            Login
          </Button>
          <Button
            type="button"
            variant="ghost"
            className={cn(
              "text-muted-foreground hover:text-foreground",
              !isLogin
                ? "bg-background text-foreground shadow-sm hover:bg-background"
                : "hover:bg-transparent"
            )}
            onClick={() => setMode("register")}
          >
            Register
          </Button>
        </div>
        <form className="grid gap-4">
          {!isLogin && <Field id="register-name" label="Name" placeholder="Your name" />}
          <Field
            id={`${mode}-email`}
            label="Email"
            type="email"
            placeholder="you@example.com"
          />
          <Field
            id={`${mode}-password`}
            label="Password"
            type="password"
            placeholder={isLogin ? "Password" : "Create a password"}
          />
          {!isLogin && (
            <div className="grid gap-2">
              <Label htmlFor="register-team">Team notes</Label>
              <Textarea id="register-team" placeholder="Tell us about your team" />
            </div>
          )}
          <DialogFooter>
            <Button type="submit" className="w-full sm:w-auto">
              {isLogin ? "Login" : "Register"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
