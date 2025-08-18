interface TokenBreakdown {
  input: number;
  output: number;
  cacheCreation: number;
  cacheRead: number;
}

export function formatCost(cost: number | null): string {
  if (cost === null) return "$0.00";
  if (cost < 0.01) return "<$0.01";
  return `$${cost.toFixed(2)}`;
}

export function formatTokens(tokens: number | null): string {
  if (tokens === null) return "0 tokens";
  if (tokens === 0) return "0 tokens";
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(1)}M tokens`;
  } else if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}K tokens`;
  }
  return `${tokens} tokens`;
}

export function formatTokenBreakdown(breakdown: TokenBreakdown | null): string {
  if (!breakdown) return "0 tokens";

  const parts: string[] = [];

  if (breakdown.input > 0) {
    parts.push(`${formatTokens(breakdown.input).replace(" tokens", "")}in`);
  }

  if (breakdown.output > 0) {
    parts.push(`${formatTokens(breakdown.output).replace(" tokens", "")}out`);
  }

  if (breakdown.cacheCreation > 0 || breakdown.cacheRead > 0) {
    const totalCached = breakdown.cacheCreation + breakdown.cacheRead;
    parts.push(`${formatTokens(totalCached).replace(" tokens", "")}cached`);
  }

  return parts.length > 0 ? parts.join(" + ") : "0 tokens";
}
