import { readFileSync } from "node:fs";
import { debug } from "../utils/logger";
import { parseJsonlFile, type ParsedEntry } from "../utils/claude";

export interface ContextInfo {
  inputTokens: number;
  percentage: number;
  usablePercentage: number;
  contextLeftPercentage: number;
  maxTokens: number;
  usableTokens: number;
}

interface ContextUsageThresholds {
  LOW: number;
  MEDIUM: number;
}

export class ContextProvider {
  private readonly thresholds: ContextUsageThresholds = {
    LOW: 50,
    MEDIUM: 80,
  };

  getContextUsageThresholds(): ContextUsageThresholds {
    return this.thresholds;
  }

  private getContextLimit(_modelId: string): number {
    return 200000;
  }

  async calculateContextTokens(
    transcriptPath: string,
    modelId?: string
  ): Promise<ContextInfo | null> {
    try {
      debug(`Calculating context tokens from transcript: ${transcriptPath}`);

      try {
        const content = readFileSync(transcriptPath, "utf-8");
        if (!content) {
          debug("Transcript file is empty");
          return null;
        }
      } catch {
        debug("Could not read transcript file");
        return null;
      }

      const parsedEntries = await parseJsonlFile(transcriptPath);

      if (parsedEntries.length === 0) {
        debug("No entries in transcript");
        return null;
      }

      let mostRecentEntry: ParsedEntry | null = null;

      for (let i = parsedEntries.length - 1; i >= 0; i--) {
        const entry = parsedEntries[i];
        if (!entry) continue;

        if (!entry.message?.usage?.input_tokens) continue;
        if (entry.isSidechain === true) continue;

        mostRecentEntry = entry;
        debug(
          `Context segment: Found most recent entry at ${entry.timestamp.toISOString()}, stopping search`
        );
        break;
      }

      if (mostRecentEntry?.message?.usage) {
        const usage = mostRecentEntry.message.usage;
        const contextLength =
          (usage.input_tokens || 0) +
          (usage.cache_read_input_tokens || 0) +
          (usage.cache_creation_input_tokens || 0);

        const contextLimit = modelId ? this.getContextLimit(modelId) : 200000;

        debug(
          `Most recent main chain context: ${contextLength} tokens (limit: ${contextLimit})`
        );

        const percentage = Math.min(
          100,
          Math.max(0, Math.round((contextLength / contextLimit) * 100))
        );

        const usableLimit = Math.round(contextLimit * 0.75);
        const usablePercentage = Math.min(
          100,
          Math.max(0, Math.round((contextLength / usableLimit) * 100))
        );

        const contextLeftPercentage = Math.max(0, 100 - usablePercentage);

        return {
          inputTokens: contextLength,
          percentage,
          usablePercentage,
          contextLeftPercentage,
          maxTokens: contextLimit,
          usableTokens: usableLimit,
        };
      }

      debug("No main chain entries with usage data found");
      return null;
    } catch (error) {
      debug(
        `Error reading transcript: ${error instanceof Error ? error.message : String(error)}`
      );
      return null;
    }
  }
}
