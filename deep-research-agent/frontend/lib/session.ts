import "server-only";
import { createHmac, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";

export const COOKIE_NAME = "drs_session";
const MAX_AGE = 60 * 60 * 12;
function secret(): string { const value = process.env.SESSION_SECRET; if (!value || value.length < 32) throw new Error("SESSION_SECRET must contain at least 32 characters"); return value; }
export function credentialMatches(user: string, password: string): boolean {
  const expectedUser = process.env.FRONTEND_USERNAME || "admin";
  const expectedPassword = process.env.FRONTEND_PASSWORD;
  if (!expectedPassword || expectedPassword.length < 12) return false;
  const match = (a: string, b: string) => { const x = createHmac("sha256", secret()).update(a).digest(); const y = createHmac("sha256", secret()).update(b).digest(); return timingSafeEqual(x,y); };
  return match(user,expectedUser) && match(password,expectedPassword);
}
export function issueSession(): string {
  const expires = Date.now() + MAX_AGE * 1000;
  const body = `v1.${expires}`;
  const sig = createHmac("sha256", secret()).update(body).digest("hex");
  return `${body}.${sig}`;
}
export function verifySession(value?: string): boolean {
  if (!value) return false;
  const bits = value.split(".");
  if (bits.length !== 3 || bits[0] !== "v1") return false;
  const expiry = Number(bits[1]);
  if (!Number.isSafeInteger(expiry) || expiry <= Date.now()) return false;
  const body = `${bits[0]}.${bits[1]}`;
  const actual = Buffer.from(bits[2], "hex");
  const expected = createHmac("sha256", secret()).update(body).digest();
  return actual.length === expected.length && timingSafeEqual(actual, expected);
}
export async function authenticated(): Promise<boolean> { return verifySession((await cookies()).get(COOKIE_NAME)?.value); }
export const sessionMaxAge = MAX_AGE;
