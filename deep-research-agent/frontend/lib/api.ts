import type {Analyst, Interview, Report, ResearchRun, RunStatus} from "@/lib/types";
const ROOT = "/api/backend";
export async function api<T>(path:string,init?:RequestInit):Promise<T>{
  const r = await fetch(ROOT+path,{...init,cache:"no-store",headers:{...(init?.body?{"Content-Type":"application/json"}:{}),...init?.headers}});
  if(!r.ok){const data = await r.json().catch(()=>({})); const message=typeof data?.detail === "string" ? data.detail : `Request failed (${r.status})`;throw new Error(message)}
  return r.json() as Promise<T>;
}
export const researchApi={
  list:(offset=0,limit=100)=>api<ResearchRun[]>(`/research?offset=${offset}&limit=${limit}`),
  get:(id:string)=>api<ResearchRun>(`/research/${id}`),
  create:(v:{topic:string;max_analysts:number;max_num_turns:number})=>api<ResearchRun>("/research",{method:"POST",body:JSON.stringify(v)}),
  feedback:(id:string,approved:boolean,feedback="")=>api<{run_id:string;status:RunStatus}>(`/research/${id}/feedback`,{method:"POST",body:JSON.stringify({approved,feedback})}),
  analysts:(id:string)=>api<Analyst[]>(`/research/${id}/analysts`),
  interviews:(id:string)=>api<Interview[]>(`/research/${id}/interviews`),
  report:(id:string)=>api<Report>(`/reports/${id}`),
  health:()=>api<{status:string}>("/health")
};
export const dateText=(s:string)=>new Date(s).toLocaleString(undefined,{dateStyle:"medium",timeStyle:"short"});
export const titleCase=(s:string)=>s.replaceAll("_"," ").replace(/\b\w/g,c=>c.toUpperCase());
