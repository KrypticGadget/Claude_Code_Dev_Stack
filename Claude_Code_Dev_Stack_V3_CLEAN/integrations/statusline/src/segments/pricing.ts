import { debug } from "../utils/logger";

export interface ModelPricing {
  name: string;
  input: number;
  cache_write_5m: number;
  cache_write_1h: number;
  cache_read: number;
  output: number;
}
const OFFLINE_PRICING_DATA: Record<string, ModelPricing> = {
  "claude-3-haiku-20240307": {
    name: "Claude 3 Haiku",
    input: 0.25,
    output: 1.25,
    cache_write_5m: 0.3,
    cache_write_1h: 0.5,
    cache_read: 0.03,
  },
  "claude-3-5-haiku-20241022": {
    name: "Claude 3.5 Haiku",
    input: 0.8,
    output: 4.0,
    cache_write_5m: 1.0,
    cache_write_1h: 1.6,
    cache_read: 0.08,
  },
  "claude-3-5-haiku-latest": {
    name: "Claude 3.5 Haiku Latest",
    input: 1.0,
    output: 5.0,
    cache_write_5m: 1.25,
    cache_write_1h: 2.0,
    cache_read: 0.1,
  },
  "claude-3-opus-latest": {
    name: "Claude 3 Opus Latest",
    input: 15.0,
    output: 75.0,
    cache_write_5m: 18.75,
    cache_write_1h: 30.0,
    cache_read: 1.5,
  },
  "claude-3-opus-20240229": {
    name: "Claude 3 Opus",
    input: 15.0,
    output: 75.0,
    cache_write_5m: 18.75,
    cache_write_1h: 30.0,
    cache_read: 1.5,
  },
  "claude-3-5-sonnet-latest": {
    name: "Claude 3.5 Sonnet Latest",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
  "claude-3-5-sonnet-20240620": {
    name: "Claude 3.5 Sonnet",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
  "claude-3-5-sonnet-20241022": {
    name: "Claude 3.5 Sonnet",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
  "claude-opus-4-20250514": {
    name: "Claude Opus 4",
    input: 15.0,
    output: 75.0,
    cache_write_5m: 18.75,
    cache_write_1h: 30.0,
    cache_read: 1.5,
  },
  "claude-opus-4-1": {
    name: "Claude Opus 4.1",
    input: 15.0,
    output: 75.0,
    cache_write_5m: 18.75,
    cache_write_1h: 30.0,
    cache_read: 1.5,
  },
  "claude-opus-4-1-20250805": {
    name: "Claude Opus 4.1",
    input: 15.0,
    output: 75.0,
    cache_write_5m: 18.75,
    cache_write_1h: 30.0,
    cache_read: 1.5,
  },
  "claude-sonnet-4-20250514": {
    name: "Claude Sonnet 4",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
  "claude-4-opus-20250514": {
    name: "Claude 4 Opus",
    input: 15.0,
    output: 75.0,
    cache_write_5m: 18.75,
    cache_write_1h: 30.0,
    cache_read: 1.5,
  },
  "claude-4-sonnet-20250514": {
    name: "Claude 4 Sonnet",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
  "claude-3-7-sonnet-latest": {
    name: "Claude 3.7 Sonnet Latest",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
  "claude-3-7-sonnet-20250219": {
    name: "Claude 3.7 Sonnet",
    input: 3.0,
    output: 15.0,
    cache_write_5m: 3.75,
    cache_write_1h: 6.0,
    cache_read: 0.3,
  },
};

export class PricingService {
  private static memoryCache: Map<
    string,
    { data: Record<string, ModelPricing>; timestamp: number }
  > = new Map();
  private static readonly CACHE_TTL = 24 * 60 * 60 * 1000;
  private static readonly GITHUB_PRICING_URL =
    "https://raw.githubusercontent.com/Owloops/claude-powerline/main/pricing.json";

  private static getCacheFilePath(): string {
    const { homedir } = require("os");
    const { join } = require("path");
    const { mkdirSync } = require("fs");

    const cacheDir = join(homedir(), ".claude", "cache");
    try {
      mkdirSync(cacheDir, { recursive: true });
    } catch {}

    return join(cacheDir, "pricing.json");
  }

  private static loadDiskCache(): {
    data: Record<string, ModelPricing>;
    timestamp: number;
  } | null {
    try {
      const { readFileSync } = require("fs");
      const cacheFile = this.getCacheFilePath();
      const content = readFileSync(cacheFile, "utf-8");
      const cached = JSON.parse(content);

      if (cached && cached.data && cached.timestamp) {
        return cached;
      }
    } catch {}
    return null;
  }

  private static saveDiskCache(data: Record<string, ModelPricing>): void {
    try {
      const { writeFileSync } = require("fs");
      const cacheFile = this.getCacheFilePath();
      const cacheData = { data, timestamp: Date.now() };
      writeFileSync(cacheFile, JSON.stringify(cacheData));
    } catch (error) {
      debug("Failed to save pricing cache to disk:", error);
    }
  }

  static async getCurrentPricing(): Promise<Record<string, ModelPricing>> {
    const now = Date.now();

    const memCached = this.memoryCache.get("pricing");
    if (memCached && now - memCached.timestamp < this.CACHE_TTL) {
      debug(
        `Using memory cached pricing data for ${Object.keys(memCached.data).length} models`
      );
      return memCached.data;
    }

    const diskCached = this.loadDiskCache();
    if (diskCached && now - diskCached.timestamp < this.CACHE_TTL) {
      this.memoryCache.clear();
      this.memoryCache.set("pricing", diskCached);
      debug(
        `Using disk cached pricing data for ${Object.keys(diskCached.data).length} models`
      );
      return diskCached.data;
    }

    try {
      const response = await globalThis.fetch(this.GITHUB_PRICING_URL, {
        headers: {
          "User-Agent": "claude-powerline",
          "Cache-Control": "no-cache",
        },
      });

      if (response.ok) {
        const data = await response.json();

        const dataObj = data as Record<string, unknown>;
        const meta = dataObj._meta as { updated?: string } | undefined;

        const pricingData: Record<string, unknown> = {};
        for (const [key, value] of Object.entries(dataObj)) {
          if (key !== "_meta") {
            pricingData[key] = value;
          }
        }

        if (this.validatePricingData(pricingData)) {
          this.memoryCache.clear();
          this.memoryCache.set("pricing", {
            data: pricingData,
            timestamp: now,
          });
          this.saveDiskCache(pricingData);
          debug(
            `Fetched fresh pricing from GitHub for ${Object.keys(pricingData).length} models`
          );
          debug(`Pricing last updated: ${meta?.updated || "unknown"}`);
          return pricingData;
        }
      }
    } catch (error) {
      debug("Failed to fetch pricing from GitHub, using fallback:", error);
    }

    if (diskCached) {
      this.memoryCache.set("pricing", diskCached);
      debug(
        `Using stale cached pricing data for ${Object.keys(diskCached.data).length} models`
      );
      return diskCached.data;
    }

    debug(
      `Using offline pricing data for ${Object.keys(OFFLINE_PRICING_DATA).length} models`
    );
    return OFFLINE_PRICING_DATA;
  }

  private static validatePricingData(
    data: unknown
  ): data is Record<string, ModelPricing> {
    if (!data || typeof data !== "object") return false;

    for (const [, value] of Object.entries(data)) {
      if (!value || typeof value !== "object") return false;
      const pricing = value as Record<string, unknown>;

      if (
        typeof pricing.input !== "number" ||
        typeof pricing.output !== "number" ||
        typeof pricing.cache_read !== "number"
      ) {
        return false;
      }
    }

    return true;
  }

  static async getModelPricing(modelId: string): Promise<ModelPricing> {
    const allPricing = await this.getCurrentPricing();

    if (allPricing[modelId]) {
      return allPricing[modelId];
    }

    return this.fuzzyMatchModel(modelId, allPricing);
  }

  private static fuzzyMatchModel(
    modelId: string,
    allPricing: Record<string, ModelPricing>
  ): ModelPricing {
    const lowerModelId = modelId.toLowerCase();

    for (const [key, pricing] of Object.entries(allPricing)) {
      if (key.toLowerCase() === lowerModelId) {
        return pricing;
      }
    }
    const patterns = [
      {
        pattern: ["opus-4-1", "claude-opus-4-1"],
        fallback: "claude-opus-4-1-20250805",
      },
      {
        pattern: ["opus-4", "claude-opus-4"],
        fallback: "claude-opus-4-20250514",
      },
      {
        pattern: ["sonnet-4", "claude-sonnet-4"],
        fallback: "claude-sonnet-4-20250514",
      },
      {
        pattern: ["sonnet-3.7", "3-7-sonnet"],
        fallback: "claude-3-7-sonnet-20250219",
      },
      {
        pattern: ["3-5-sonnet", "sonnet-3.5"],
        fallback: "claude-3-5-sonnet-20241022",
      },
      {
        pattern: ["3-5-haiku", "haiku-3.5"],
        fallback: "claude-3-5-haiku-20241022",
      },
      { pattern: ["haiku", "3-haiku"], fallback: "claude-3-haiku-20240307" },
      { pattern: ["opus"], fallback: "claude-opus-4-20250514" },
      { pattern: ["sonnet"], fallback: "claude-3-5-sonnet-20241022" },
    ];

    for (const { pattern, fallback } of patterns) {
      if (pattern.some((p) => lowerModelId.includes(p))) {
        if (allPricing[fallback]) {
          return allPricing[fallback];
        }
      }
    }

    return (
      allPricing["claude-3-5-sonnet-20241022"] || {
        name: `${modelId} (Unknown Model)`,
        input: 3.0,
        cache_write_5m: 3.75,
        cache_write_1h: 6.0,
        cache_read: 0.3,
        output: 15.0,
      }
    );
  }

  static async calculateCostForEntry(entry: any): Promise<number> {
    const message = entry.message;
    const usage = message?.usage;
    if (!usage) return 0;

    const modelId = this.extractModelId(entry);
    const pricing = await this.getModelPricing(modelId);

    const inputTokens = usage.input_tokens || 0;
    const outputTokens = usage.output_tokens || 0;
    const cacheCreationTokens = usage.cache_creation_input_tokens || 0;
    const cacheReadTokens = usage.cache_read_input_tokens || 0;

    const inputCost = (inputTokens / 1_000_000) * pricing.input;
    const outputCost = (outputTokens / 1_000_000) * pricing.output;
    const cacheReadCost = (cacheReadTokens / 1_000_000) * pricing.cache_read;
    const cacheCreationCost =
      (cacheCreationTokens / 1_000_000) * pricing.cache_write_5m;

    return inputCost + outputCost + cacheCreationCost + cacheReadCost;
  }

  private static extractModelId(entry: any): string {
    if (entry.model && typeof entry.model === "string") {
      return entry.model;
    }

    const message = entry.message;
    if (message?.model) {
      const model = message.model;
      if (typeof model === "string") {
        return model;
      }
      return model?.id || "claude-3-5-sonnet-20241022";
    }

    if (entry.model_id && typeof entry.model_id === "string") {
      return entry.model_id;
    }

    return "claude-3-5-sonnet-20241022";
  }
}
