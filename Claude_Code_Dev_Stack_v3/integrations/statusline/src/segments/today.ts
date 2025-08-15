import { debug } from "../utils/logger";
import { PricingService } from "./pricing";
import { loadEntriesFromProjects, type ParsedEntry } from "../utils/claude";
import type { TokenBreakdown } from "./session";

export interface TodayUsageEntry {
  timestamp: Date;
  usage: {
    inputTokens: number;
    outputTokens: number;
    cacheCreationInputTokens: number;
    cacheReadInputTokens: number;
  };
  costUSD: number;
  model: string;
}

export interface TodayInfo {
  cost: number | null;
  tokens: number | null;
  tokenBreakdown: TokenBreakdown | null;
  date: string;
}

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getTotalTokens(usage: TodayUsageEntry["usage"]): number {
  return (
    usage.inputTokens +
    usage.outputTokens +
    usage.cacheCreationInputTokens +
    usage.cacheReadInputTokens
  );
}

function convertToTodayEntry(entry: ParsedEntry): TodayUsageEntry {
  return {
    timestamp: entry.timestamp,
    usage: {
      inputTokens: entry.message?.usage?.input_tokens || 0,
      outputTokens: entry.message?.usage?.output_tokens || 0,
      cacheCreationInputTokens:
        entry.message?.usage?.cache_creation_input_tokens || 0,
      cacheReadInputTokens: entry.message?.usage?.cache_read_input_tokens || 0,
    },
    costUSD: entry.costUSD || 0,
    model: entry.message?.model || "unknown",
  };
}

export class TodayProvider {
  private cache: Map<string, { data: TodayUsageEntry[]; timestamp: number }> =
    new Map();
  private readonly CACHE_TTL = 300000;

  private async loadTodayEntries(): Promise<TodayUsageEntry[]> {
    const today = new Date();
    const todayDateString = formatDate(today);

    debug(`Today segment: Loading entries for date ${todayDateString}`);

    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);

    const fileFilter = (_filePath: string, modTime: Date): boolean => {
      return modTime >= weekAgo;
    };

    const parsedEntries = await loadEntriesFromProjects(
      undefined,
      fileFilter,
      true
    );
    const todayEntries: TodayUsageEntry[] = [];

    let entriesFound = 0;

    for (const entry of parsedEntries) {
      const entryDateString = formatDate(entry.timestamp);

      if (entryDateString === todayDateString && entry.message?.usage) {
        const todayEntry = convertToTodayEntry(entry);

        if (!todayEntry.costUSD && entry.raw) {
          todayEntry.costUSD = await PricingService.calculateCostForEntry(
            entry.raw
          );
        }

        todayEntries.push(todayEntry);
        entriesFound++;
      }
    }

    debug(
      `Today segment: Found ${entriesFound} entries for today (${todayDateString})`
    );
    return todayEntries;
  }

  private async getTodayEntries(): Promise<TodayUsageEntry[]> {
    const cacheKey = "today";
    const cached = this.cache.get(cacheKey);
    const now = Date.now();

    if (cached && now - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }

    this.cache.clear();

    try {
      const entries = await this.loadTodayEntries();

      this.cache.set(cacheKey, { data: entries, timestamp: now });
      return entries;
    } catch (error) {
      debug("Error loading today's entries:", error);
      return [];
    }
  }

  async getTodayInfo(): Promise<TodayInfo> {
    try {
      const entries = await this.getTodayEntries();

      if (entries.length === 0) {
        return {
          cost: null,
          tokens: null,
          tokenBreakdown: null,
          date: formatDate(new Date()),
        };
      }

      const totalCost = entries.reduce((sum, entry) => sum + entry.costUSD, 0);
      const totalTokens = entries.reduce(
        (sum, entry) => sum + getTotalTokens(entry.usage),
        0
      );

      const tokenBreakdown = entries.reduce(
        (breakdown, entry) => ({
          input: breakdown.input + entry.usage.inputTokens,
          output: breakdown.output + entry.usage.outputTokens,
          cacheCreation:
            breakdown.cacheCreation + entry.usage.cacheCreationInputTokens,
          cacheRead: breakdown.cacheRead + entry.usage.cacheReadInputTokens,
        }),
        {
          input: 0,
          output: 0,
          cacheCreation: 0,
          cacheRead: 0,
        }
      );

      debug(
        `Today segment: $${totalCost.toFixed(2)}, ${totalTokens} tokens total`
      );

      return {
        cost: totalCost,
        tokens: totalTokens,
        tokenBreakdown,
        date: formatDate(new Date()),
      };
    } catch (error) {
      debug("Error getting today's info:", error);
      return {
        cost: null,
        tokens: null,
        tokenBreakdown: null,
        date: formatDate(new Date()),
      };
    }
  }
}
