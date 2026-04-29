"use server";

import { cookies } from "next/headers";
import { API_URL } from "@/lib/api";
import { redirect } from "next/navigation";

export async function loginAction(prevState: any, formData: FormData) {
  const email = formData.get("email");
  const password = formData.get("password");

  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    return { error: errorData.detail || "Invalid credentials" };
  }

  const setCookie = res.headers.get("set-cookie");
  if (setCookie) {
    const match = setCookie.match(/access_token=([^;]+)/);
    if (match) {
      const cookieStore = await cookies();
      cookieStore.set("access_token", match[1], {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 604800,
      });
    }
  }

  redirect("/admin");
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
  redirect("/login");
}
