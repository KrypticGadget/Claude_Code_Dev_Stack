import { execSync } from "node:child_process";
import { debug } from "../utils/logger";

export class TmuxService {
  getSessionId(): string | null {
    try {
      if (!process.env.TMUX_PANE) {
        debug(`TMUX_PANE not set, not in tmux session`);
        return null;
      }

      debug(`Getting tmux session ID, TMUX_PANE: ${process.env.TMUX_PANE}`);

      const sessionId = execSync("tmux display-message -p '#S'", {
        encoding: "utf8",
        timeout: 1000,
      }).trim();

      debug(`Tmux session ID: ${sessionId || "empty"}`);

      return sessionId || null;
    } catch (error) {
      debug(`Error getting tmux session ID:`, error);
      return null;
    }
  }

  isInTmux(): boolean {
    return !!process.env.TMUX_PANE;
  }
}