"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

interface DocSection {
  title: string
  items: {
    title: string
    href: string
  }[]
}

const docSections: DocSection[] = [
  {
    title: "Getting Started",
    items: [
      { title: "Fire Your First Order", href: "/docs/getting-started" },
    ],
  },
  {
    title: "Core Concepts",
    items: [
      { title: "Overview", href: "/docs/concepts" },
      { title: "BYOLLM (Your LLM, Your Bill)", href: "/docs/concepts/byollm" },
    ],
  },
  {
    title: "MCP Integration",
    items: [
      { title: "Overview", href: "/docs/mcp" },
      { title: "Claude Desktop", href: "/docs/mcp/claude-desktop" },
      { title: "Cursor", href: "/docs/mcp/cursor" },
      { title: "Windsurf", href: "/docs/mcp/windsurf" },
      { title: "Claude Code", href: "/docs/mcp/claude-code" },
    ],
  },
  {
    title: "API Reference",
    items: [
      { title: "Overview", href: "/docs/api" },
      { title: "MCP Tools", href: "/docs/api/tools" },
    ],
  },
]

export function DocsSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r border-foreground bg-surface-elevated p-6 overflow-y-auto">
      <nav className="space-y-8">
        {docSections.map((section) => (
          <div key={section.title}>
            <div className="font-mono text-xs uppercase tracking-widest font-bold mb-3 text-foreground/70">
              {section.title}
            </div>
            <ul className="space-y-2">
              {section.items.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={cn(
                      "block font-mono text-sm py-1 px-2 -mx-2 rounded transition-colors",
                      pathname === item.href
                        ? "bg-foreground text-background font-bold"
                        : "hover:bg-foreground/10 text-foreground"
                    )}
                  >
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  )
}
