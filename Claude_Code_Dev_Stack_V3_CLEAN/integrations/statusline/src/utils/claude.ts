import { readdir, readFile, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, posix } from "node:path";
import { homedir } from "node:os";
import { debug } from "./logger";

export function getClaudePaths(): string[] {
  const paths: string[] = [];

  const envPath = process.env.CLAUDE_CONFIG_DIR;
  if (envPath) {
    envPath.split(",").forEach((path) => {
      const trimmedPath = path.trim();
      if (existsSync(trimmedPath)) {
        paths.push(trimmedPath);
      }
    });
  }

  if (paths.length === 0) {
    const homeDir = homedir();
    const configPath = join(homeDir, ".config", "claude");
    const claudePath = join(homeDir, ".claude");

    if (existsSync(configPath)) {
      paths.push(configPath);
    } else if (existsSync(claudePath)) {
      paths.push(claudePath);
    }
  }

  return paths;
}

export async function findProjectPaths(
  claudePaths: string[]
): Promise<string[]> {
  const projectPaths: string[] = [];

  for (const claudePath of claudePaths) {
    const projectsDir = join(claudePath, "projects");

    if (existsSync(projectsDir)) {
      try {
        const entries = await readdir(projectsDir, { withFileTypes: true });

        for (const entry of entries) {
          if (entry.isDirectory()) {
            const projectPath = posix.join(projectsDir, entry.name);
            projectPaths.push(projectPath);
          }
        }
      } catch (error) {
        debug(`Failed to read projects directory ${projectsDir}:`, error);
      }
    }
  }

  return projectPaths;
}

export async function findTranscriptFile(
  sessionId: string
): Promise<string | null> {
  const claudePaths = getClaudePaths();
  const projectPaths = await findProjectPaths(claudePaths);

  for (const projectPath of projectPaths) {
    const transcriptPath = posix.join(projectPath, `${sessionId}.jsonl`);
    if (existsSync(transcriptPath)) {
      return transcriptPath;
    }
  }

  return null;
}

export async function getEarliestTimestamp(
  filePath: string
): Promise<Date | null> {
  try {
    const content = await readFile(filePath, "utf-8");
    const lines = content.trim().split("\n");

    let earliestDate: Date | null = null;
    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const json = JSON.parse(line);
        if (json.timestamp && typeof json.timestamp === "string") {
          const date = new Date(json.timestamp);
          if (!isNaN(date.getTime())) {
            if (earliestDate === null || date < earliestDate) {
              earliestDate = date;
            }
          }
        }
      } catch {
        continue;
      }
    }
    return earliestDate;
  } catch (error) {
    debug(`Failed to get earliest timestamp for ${filePath}:`, error);
    return null;
  }
}

export async function sortFilesByTimestamp(
  files: string[],
  oldestFirst = true
): Promise<string[]> {
  const filesWithTimestamps = await Promise.all(
    files.map(async (file) => ({
      file,
      timestamp: await getEarliestTimestamp(file),
    }))
  );

  return filesWithTimestamps
    .sort((a, b) => {
      if (a.timestamp === null && b.timestamp === null) return 0;
      if (a.timestamp === null) return 1;
      if (b.timestamp === null) return -1;
      const sortOrder = oldestFirst ? 1 : -1;
      return sortOrder * (a.timestamp.getTime() - b.timestamp.getTime());
    })
    .map((item) => item.file);
}

export async function getFileModificationDate(
  filePath: string
): Promise<Date | null> {
  try {
    const stats = await stat(filePath);
    return stats.mtime;
  } catch {
    return null;
  }
}

export interface ParsedEntry {
  timestamp: Date;
  message?: {
    id?: string;
    usage?: {
      input_tokens?: number;
      output_tokens?: number;
      cache_creation_input_tokens?: number;
      cache_read_input_tokens?: number;
    };
    model?: string;
  };
  costUSD?: number;
  isSidechain?: boolean;
  raw: Record<string, unknown>;
}

export function createUniqueHash(entry: ParsedEntry): string | null {
  const messageId =
    entry.message?.id ||
    (typeof entry.raw.message === "object" &&
    entry.raw.message !== null &&
    "id" in entry.raw.message
      ? (entry.raw.message.id as string)
      : undefined);
  const requestId =
    "requestId" in entry.raw ? (entry.raw.requestId as string) : undefined;

  if (!messageId || !requestId) {
    return null;
  }

  return `${messageId}:${requestId}`;
}

export async function parseJsonlFile(filePath: string): Promise<ParsedEntry[]> {
  try {
    const content = await readFile(filePath, "utf-8");
    const lines = content
      .trim()
      .split("\n")
      .filter((line) => line.trim());
    const entries: ParsedEntry[] = [];

    for (const line of lines) {
      try {
        const raw = JSON.parse(line);
        if (!raw.timestamp) continue;

        const entry: ParsedEntry = {
          timestamp: new Date(raw.timestamp),
          message: raw.message,
          costUSD: typeof raw.costUSD === "number" ? raw.costUSD : undefined,
          isSidechain: raw.isSidechain === true,
          raw,
        };

        entries.push(entry);
      } catch (parseError) {
        debug(`Failed to parse JSONL line: ${parseError}`);
        continue;
      }
    }

    return entries;
  } catch (error) {
    debug(`Failed to read file ${filePath}:`, error);
    return [];
  }
}

export async function loadEntriesFromProjects(
  timeFilter?: (entry: ParsedEntry) => boolean,
  fileFilter?: (filePath: string, modTime: Date) => boolean,
  sortFiles = false
): Promise<ParsedEntry[]> {
  const entries: ParsedEntry[] = [];
  const claudePaths = getClaudePaths();
  const projectPaths = await findProjectPaths(claudePaths);
  const processedHashes = new Set<string>();

  const allFiles: string[] = [];
  for (const projectPath of projectPaths) {
    try {
      const files = await readdir(projectPath);
      const jsonlFiles = files.filter((file) => file.endsWith(".jsonl"));

      const fileStatsPromises = jsonlFiles.map(async (file) => {
        const filePath = posix.join(projectPath, file);
        if (existsSync(filePath)) {
          const mtime = await getFileModificationDate(filePath);
          return { filePath, mtime };
        }
        return null;
      });

      const fileStats = await Promise.all(fileStatsPromises);

      for (const stat of fileStats) {
        if (
          stat?.mtime &&
          (!fileFilter || fileFilter(stat.filePath, stat.mtime))
        ) {
          allFiles.push(stat.filePath);
        }
      }
    } catch (dirError) {
      debug(`Failed to read project directory ${projectPath}:`, dirError);
      continue;
    }
  }

  if (sortFiles) {
    const sortedFiles = await sortFilesByTimestamp(allFiles, false);
    allFiles.length = 0;
    allFiles.push(...sortedFiles);
  }

  for (const filePath of allFiles) {
    const fileEntries = await parseJsonlFile(filePath);
    for (const entry of fileEntries) {
      const uniqueHash = createUniqueHash(entry);
      if (uniqueHash && processedHashes.has(uniqueHash)) {
        debug(`Skipping duplicate entry: ${uniqueHash}`);
        continue;
      }

      if (uniqueHash) {
        processedHashes.add(uniqueHash);
      }

      if (!timeFilter || timeFilter(entry)) {
        entries.push(entry);
      }
    }
  }

  return entries;
}
