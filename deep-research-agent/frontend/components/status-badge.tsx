import type {RunStatus} from "@/lib/types";
import {titleCase} from "@/lib/api";
const colors:Record<RunStatus,string>={queued:"bg-slate-500/15 text-slate-300 border-slate-500/30",running:"bg-sky-500/15 text-sky-300 border-sky-500/30",awaiting_feedback:"bg-amber-500/15 text-amber-300 border-amber-500/30",completed:"bg-emerald-500/15 text-emerald-300 border-emerald-500/30",failed:"bg-rose-500/15 text-rose-300 border-rose-500/30"};
export function StatusBadge({status}:{status:RunStatus}){return <span className={`tag inline-flex items-center gap-2 ${colors[status]}`}><span className="h-1.5 w-1.5 rounded-full bg-current"/>{titleCase(status)}</span>}
