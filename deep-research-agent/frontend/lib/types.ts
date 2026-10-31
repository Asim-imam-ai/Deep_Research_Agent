export type RunStatus = "queued"|"running"|"awaiting_feedback"|"completed"|"failed";
export type ResearchRun = {id:string;topic:string;status:RunStatus;max_analysts:number;max_num_turns:number;created_at:string;updated_at:string;error:string|null};
export type Analyst = {name:string;role:string;affiliation:string;description:string};
export type Interview = {analyst_name:string;transcript:string};
export type Report = {id:string;run_id:string;title:string;markdown:string;data:Record<string,unknown>};
export type ResearchEvent = {id:number;kind:string;payload:Record<string,unknown>};
