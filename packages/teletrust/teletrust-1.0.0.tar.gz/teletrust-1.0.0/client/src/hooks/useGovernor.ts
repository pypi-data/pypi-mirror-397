/**
 * Hook for calling MOA Governor API
 */
import { useState } from 'react';

interface GovernResult {
    session_id: string;
    risk_score: number;
    zone: 'GREEN' | 'YELLOW' | 'RED';
    output_text: string;
    cost_usd: number;
    action_log: string[];
    prime_code_macro: number;
    prime_code_nodes: string;
    regulatory_signals: string[];
}

interface UseGovernorOptions {
    apiKey?: string;
}

export function useGovernor(options: UseGovernorOptions = {}) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<GovernResult | null>(null);

    const apiKey = options.apiKey || 'sk_example_demo';

    const govern = async (sessionId: string, text: string): Promise<GovernResult | null> => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/govern', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`,
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    text: text,
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `HTTP ${response.status}`);
            }

            const data: GovernResult = await response.json();
            setResult(data);
            return data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    return { govern, isLoading, error, result };
}
