import { Header } from "@/components/marketing/header"
import { Footer } from "@/components/marketing/footer"
import { DocsSidebar } from "@/components/docs/sidebar"

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1">
        <DocsSidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-8 md:p-12">
            <article className="prose prose-lg prose-headings:font-serif prose-headings:font-bold prose-p:font-serif prose-p:text-lg prose-p:leading-relaxed prose-a:text-foreground prose-a:underline prose-a:decoration-2 prose-a:underline-offset-4 hover:prose-a:decoration-4 prose-code:font-mono prose-code:text-sm prose-pre:font-mono prose-pre:text-sm max-w-none">
              {children}
            </article>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  )
}
