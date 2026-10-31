import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME, credentialMatches, issueSession, sessionMaxAge } from "@/lib/session";
export const runtime = "nodejs";
export async function POST(request: NextRequest) {
  let body: unknown;
  try { body = await request.json(); } catch { return NextResponse.json({ detail: "Invalid JSON" }, { status: 400 }); }
  if (typeof body !== "object" || body === null || !("username" in body) || !("password" in body)) return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
  const { username, password } = body as {username: unknown; password: unknown};
  if (typeof username !== "string" || typeof password !== "string" || !credentialMatches(username, password)) return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
  const result = NextResponse.json({ ok: true });
  result.cookies.set(COOKIE_NAME, issueSession(), { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: sessionMaxAge });
  return result;
}
export async function DELETE() {
  const result = NextResponse.json({ ok: true });
  result.cookies.set(COOKIE_NAME, "", { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: 0 });
  return result;
}
