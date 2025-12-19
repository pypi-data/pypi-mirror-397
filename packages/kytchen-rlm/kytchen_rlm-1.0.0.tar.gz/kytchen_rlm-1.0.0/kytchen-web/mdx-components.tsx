import type { MDXComponents } from "mdx/types"
import { CodeBlock, InlineCode } from "@/components/docs/code-block"

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    // Override default code rendering
    code: ({ children, className, ...props }) => {
      // Inline code (no language specified)
      if (!className) {
        return <InlineCode>{String(children)}</InlineCode>
      }

      // Code blocks
      const language = className?.replace("language-", "") || "text"
      return (
        <CodeBlock language={language} {...props}>
          {String(children).trim()}
        </CodeBlock>
      )
    },
    // You can override other components here
    ...components,
  }
}
