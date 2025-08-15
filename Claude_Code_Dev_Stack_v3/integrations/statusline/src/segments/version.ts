import { execSync } from "node:child_process";
import { debug } from "../utils/logger";

export interface VersionInfo {
  version: string | null;
}

export class VersionProvider {
  private cachedVersion: string | null = null;
  private cacheTimestamp: number = 0;
  private readonly CACHE_TTL = 30000;

  getClaudeVersion(): string | null {
    const now = Date.now();
    if (
      this.cachedVersion !== null &&
      now - this.cacheTimestamp < this.CACHE_TTL
    ) {
      return this.cachedVersion;
    }

    try {
      const output = execSync("claude --version", {
        encoding: "utf8",
        timeout: 1000,
      }).trim();

      const match = output.match(/^([\d.]+)/);
      if (match) {
        this.cachedVersion = `v${match[1]}`;
        this.cacheTimestamp = now;
        debug(`Claude Code version: ${this.cachedVersion}`);
        return this.cachedVersion;
      }

      debug(`Could not parse version from: ${output}`);
      return null;
    } catch (error) {
      debug(`Error getting Claude Code version:`, error);
      return null;
    }
  }

  async getVersionInfo(): Promise<VersionInfo> {
    const version = this.getClaudeVersion();
    return { version };
  }
}
