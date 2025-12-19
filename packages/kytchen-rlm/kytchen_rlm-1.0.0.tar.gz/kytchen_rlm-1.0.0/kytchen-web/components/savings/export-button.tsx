"use client"

import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { TokenMetrics } from "@/lib/api/metrics";

interface ExportButtonProps {
    data: TokenMetrics[];
}

export function ExportButton({ data }: ExportButtonProps) {
    const handleExport = () => {
        const jsonString = `data:text/json;chatset=utf-8,${encodeURIComponent(
            JSON.stringify(data, null, 2)
        )}`;
        const link = document.createElement("a");
        link.href = jsonString;
        link.download = `kytchen-metrics-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    };

    return (
        <Button onClick={handleExport} variant="outline" className="gap-2 border-2 border-black hover:bg-slate-100 shadow-[2px_2px_0_#000]">
            <Download className="w-4 h-4" />
            Export Receipts
        </Button>
    );
}
