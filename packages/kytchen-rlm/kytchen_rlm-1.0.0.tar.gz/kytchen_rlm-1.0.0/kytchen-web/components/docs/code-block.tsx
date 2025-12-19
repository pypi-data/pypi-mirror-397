"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface CodeBlockProps {
  children: string
  language?: string
  showLineNumbers?: boolean
  filename?: string
}

export function CodeBlock({
  children,
  language = "bash",
  showLineNumbers = false,
  filename,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="my-6 relative group">
      {filename && (
        <div className="bg-foreground/10 px-4 py-2 font-mono text-xs text-foreground/70 border-b border-foreground/20">
          {filename}
        </div>
      )}
      <div className="bg-foreground text-background p-6 font-mono text-sm overflow-x-auto shadow-[8px_8px_0px_0px_rgba(0,0,0,0.2)] relative">
        <Button
          onClick={handleCopy}
          variant="ghost"
          size="sm"
          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-background/10 hover:bg-background/20 text-background"
        >
          {copied ? "Heard!" : "Copy"}
        </Button>
        <pre className={showLineNumbers ? "line-numbers" : ""}>
          <code className={language ? `language-${language}` : ""}>
            {children}
          </code>
        </pre>
      </div>
    </div>
  )
}

interface InlineCodeProps {
  children: string
}

export function InlineCode({ children }: InlineCodeProps) {
  return (
    <code className="bg-foreground/10 text-foreground px-1.5 py-0.5 rounded font-mono text-sm">
      {children}
    </code>
  )
}
