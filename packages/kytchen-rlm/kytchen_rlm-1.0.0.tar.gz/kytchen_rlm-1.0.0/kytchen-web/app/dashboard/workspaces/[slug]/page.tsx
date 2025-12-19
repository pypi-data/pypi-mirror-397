import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Upload, Play, FileText, Activity } from "lucide-react"

export default function WorkspaceOverviewPage({ params }: { params: { slug: string } }) {
   return (
      <div className="space-y-8">
         <div className="flex items-center justify-between">
            <div>
               <h1 className="font-serif text-3xl mb-1">{params.slug}</h1>
               <p className="font-mono text-xs text-muted-foreground uppercase">Workspace Overview</p>
            </div>
            <div className="flex gap-2">
               <Link href={`/dashboard/workspaces/${params.slug}/datasets`}>
                  <Button variant="outline" className="gap-2">
                     <Upload className="w-4 h-4" /> Upload Data
                  </Button>
               </Link>
               <Link href={`/dashboard/workspaces/${params.slug}/runs/new`}>
                  <Button className="gap-2">
                     <Play className="w-4 h-4" /> New Run
                  </Button>
               </Link>
            </div>
         </div>

         <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card className="h-full">
               <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                     <Activity className="w-5 h-5" /> Recent Activity
                  </CardTitle>
               </CardHeader>
               <CardContent>
                  <div className="font-mono text-sm text-muted-foreground text-center py-8">
                     No runs yet. Start exploring your data.
                  </div>
               </CardContent>
            </Card>

            <Card className="h-full">
               <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                     <FileText className="w-5 h-5" /> Quick Stats
                  </CardTitle>
               </CardHeader>
               <CardContent className="space-y-4">
                  <div className="flex justify-between items-center border-b border-foreground/10 pb-2">
                     <span className="font-mono text-sm">Datasets</span>
                     <span className="font-mono font-bold">0</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-foreground/10 pb-2">
                     <span className="font-mono text-sm">Total Runs</span>
                     <span className="font-mono font-bold">0</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-foreground/10 pb-2">
                     <span className="font-mono font-bold">0 MB</span>
                  </div>
               </CardContent>
            </Card>
         </div>
      </div>
   )
}
