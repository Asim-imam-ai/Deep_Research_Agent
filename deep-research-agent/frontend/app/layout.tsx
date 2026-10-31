import type {Metadata} from "next";
import "./globals.css";
export const metadata:Metadata={title:"Deep Research Studio",description:"Intelligent, multi-agent research and evidence-driven reports."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
