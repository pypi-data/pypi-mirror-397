import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ToolParam {
  name: string
  type: string
  required?: boolean
  default?: string
  description: string
}

interface ToolCardProps {
  name: string
  description: string
  parameters: ToolParam[]
  returns?: string
  example?: string
}

export function ToolCard({
  name,
  description,
  parameters,
  returns,
  example,
}: ToolCardProps) {
  return (
    <Card className="p-6 mb-6 border-2 border-foreground shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)]">
      <div className="flex items-start justify-between mb-4">
        <h3 className="font-mono text-xl font-bold text-foreground">{name}</h3>
        <Badge variant="outline" className="font-mono text-xs">
          TOOL
        </Badge>
      </div>

      <p className="font-serif text-lg mb-6 text-foreground/80">{description}</p>

      <div className="space-y-4">
        <div>
          <h4 className="font-mono text-sm font-bold uppercase tracking-wider mb-3 text-foreground/70">
            Parameters
          </h4>
          <div className="space-y-3">
            {parameters.map((param) => (
              <div
                key={param.name}
                className="border-l-2 border-foreground/20 pl-4 py-1"
              >
                <div className="flex items-center gap-2 mb-1">
                  <code className="font-mono text-sm font-bold text-foreground">
                    {param.name}
                  </code>
                  <Badge
                    variant={param.required ? "default" : "secondary"}
                    className="text-xs font-mono"
                  >
                    {param.type}
                  </Badge>
                  {param.required && (
                    <Badge variant="destructive" className="text-xs font-mono">
                      required
                    </Badge>
                  )}
                  {param.default && (
                    <span className="text-xs font-mono text-foreground/50">
                      default: {param.default}
                    </span>
                  )}
                </div>
                <p className="text-sm text-foreground/70">{param.description}</p>
              </div>
            ))}
          </div>
        </div>

        {returns && (
          <div>
            <h4 className="font-mono text-sm font-bold uppercase tracking-wider mb-2 text-foreground/70">
              Returns
            </h4>
            <p className="text-sm font-mono bg-foreground/5 p-3 rounded">
              {returns}
            </p>
          </div>
        )}

        {example && (
          <div>
            <h4 className="font-mono text-sm font-bold uppercase tracking-wider mb-2 text-foreground/70">
              Example
            </h4>
            <pre className="bg-foreground text-background p-4 rounded font-mono text-sm overflow-x-auto">
              <code>{example}</code>
            </pre>
          </div>
        )}
      </div>
    </Card>
  )
}
