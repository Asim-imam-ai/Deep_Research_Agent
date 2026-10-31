"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import {Plus} from "lucide-react";
import {researchApi} from "@/lib/api";
import type {ResearchRun} from "@/lib/types";
import {RunList} from "@/components/run-list";
export default function Library(){const [runs,setRuns]=useState<ResearchRun[]>([]);const [error,setError]=useState("");const [loading,setLoading]=useState(true);useEffect(()=>{researchApi.list().then(setRuns).catch(e=>setError(e instanceof Error?e.message:"Failed to load research")).finally(()=>setLoading(false))},[]);return <div className="space-y-8"><div className="flex flex-wrap items-center justify-between gap-4"><div><p className="mb-2 text-xs font-bold uppercase tracking-[.2em] text-violet-400">Workspace / Library</p><h1 className="text-3xl font-bold">All research</h1><p className="mt-2 text-sm text-slate-400">Search, filter, and reopen your investigations.</p></div><Link href="/research/new" className="btn btn-primary"><Plus size={16}/> New research</Link></div>{error&&<p role="alert" className="text-rose-300">{error}</p>}{loading?<div className="panel p-10 text-center text-slate-400">Loading projects...</div>:<RunList runs={runs}/>}</div>}
