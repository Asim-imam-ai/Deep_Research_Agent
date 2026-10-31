import { NextRequest, NextResponse } from "next/server";
import { authenticated } from "@/lib/session";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
type Context = { params: Promise<{path: string[]}> };
const UUID = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
const allowed = [new RegExp("^research$"), new RegExp(`^research/${UUID}$`), new RegExp(`^research/${UUID}/(feedback|stream|analysts|interviews)$`), new RegExp(`^reports/${UUID}$`), /^health$/];
async function proxy(request: NextRequest, context: Context) {
  if (!(await authenticated())) return NextResponse.json({detail:"Sign in required"},{status:401});
  // Browser same-origin requests only; restrict cross-origin state changes.
  const origin = request.headers.get("origin");
  if (request.method !== "GET" && origin && origin !== request.nextUrl.origin) return NextResponse.json({detail:"Cross-origin request rejected"},{status:403});
  const {path} = await context.params; const endpoint = path.join("/");
  if (!allowed.some(p => p.test(endpoint))) return NextResponse.json({detail:"Unknown route"},{status:404});
  if (request.method === "POST" && !(/^(research|research\/.+\/feedback)$/.test(endpoint))) return NextResponse.json({detail:"Method not allowed"},{status:405});
  const base = process.env.BACKEND_API_URL; const key = process.env.BACKEND_API_KEY;
  if (!base || !key) return NextResponse.json({detail:"Backend not configured"},{status:503});
  try {
    const target = new URL(`/api/v1/${endpoint}`, base); target.search = request.nextUrl.search;
    const headers = new Headers({"X-API-Key":key});
    if (request.method === "POST") headers.set("Content-Type","application/json");
    const last = request.headers.get("Last-Event-ID"); if (last) headers.set("Last-Event-ID",last);
    const upstream = await fetch(target,{method:request.method,headers,body:request.method === "POST"?await request.text():undefined,cache:"no-store",signal:request.signal,redirect:"manual"});
    const h = new Headers({"Content-Type":upstream.headers.get("Content-Type") || "application/json", "Cache-Control":"no-store", "X-Content-Type-Options":"nosniff"});
    if (endpoint.endsWith("/stream")) h.set("X-Accel-Buffering","no");
    return new Response(upstream.body,{status:upstream.status,headers:h});
  } catch { return NextResponse.json({detail:"Backend unavailable. Ensure FastAPI is running."},{status:502}); }
}
export async function GET(r:NextRequest,c:Context){return proxy(r,c)}
export async function POST(r:NextRequest,c:Context){return proxy(r,c)}
