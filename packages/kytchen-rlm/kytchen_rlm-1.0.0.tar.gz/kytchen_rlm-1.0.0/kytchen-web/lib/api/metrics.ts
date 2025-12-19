export interface TokenMetrics {
    run_id: string;
    dataset_id: string;
    baseline_tokens: number;    // What context-stuffing would use
    tokens_served: number;      // What Kytchen actually used
    savings_percent: number;    // (baseline - served) / baseline * 100
    cost_saved_usd: number;     // Estimated cost savings
    timestamp: string;
}

export interface MetricsSummary {
    period: string;
    group_by: string;
    data: TokenMetrics[];
}

// Mock data generator
const generateMockMetrics = (count: number): TokenMetrics[] => {
    return Array.from({ length: count }).map((_, i) => {
        const baseline = Math.floor(Math.random() * 50000) + 10000;
        const served = Math.floor(Math.random() * 2000) + 500;
        const savings = (baseline - served) / baseline * 100;
        const savedUsd = (baseline - served) / 1000 * 0.01; // Assuming $0.01 per 1k tokens

        return {
            run_id: `run_${Math.random().toString(36).substring(7)}`,
            dataset_id: `ds_${Math.random().toString(36).substring(7)}`,
            baseline_tokens: baseline,
            tokens_served: served,
            savings_percent: savings,
            cost_saved_usd: savedUsd,
            timestamp: new Date(Date.now() - i * 86400000).toISOString() // Past days
        };
    });
};

export const MetricsApi = {
    async getRuns(): Promise<TokenMetrics[]> {
        // Simulating API latency
        await new Promise(resolve => setTimeout(resolve, 800));
        return generateMockMetrics(20);
    },

    async getSummary(period: string = '7d', groupBy: string = 'dataset'): Promise<MetricsSummary> {
        await new Promise(resolve => setTimeout(resolve, 500));
        return {
            period,
            group_by: groupBy,
            data: generateMockMetrics(10)
        };
    }
};
