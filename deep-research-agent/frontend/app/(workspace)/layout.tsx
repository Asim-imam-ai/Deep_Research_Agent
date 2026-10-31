import {redirect} from "next/navigation";
import {authenticated} from "@/lib/session";
import {AppShell} from "@/components/app-shell";
export default async function WorkspaceLayout({children}:{children:React.ReactNode}){if(!(await authenticated()))redirect("/login");return <AppShell>{children}</AppShell>}
