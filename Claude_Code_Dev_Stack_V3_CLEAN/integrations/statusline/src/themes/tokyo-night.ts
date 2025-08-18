import type { ColorTheme } from "./index";

export const tokyoNightTheme: ColorTheme = {
  directory: { bg: "#2f334d", fg: "#82aaff" },
  git: { bg: "#1e2030", fg: "#c3e88d" },
  model: { bg: "#191b29", fg: "#fca7ea" },
  session: { bg: "#222436", fg: "#86e1fc" },
  block: { bg: "#2d3748", fg: "#7aa2f7" },
  today: { bg: "#1a202c", fg: "#4fd6be" },
  tmux: { bg: "#191b29", fg: "#4fd6be" },
  context: { bg: "#414868", fg: "#c0caf5" },
  metrics: { bg: "#3d59a1", fg: "#c0caf5" },
  version: { bg: "#292e42", fg: "#bb9af7" },
  // Dev Stack segments
  agent: { bg: "#bb9af7", fg: "#191b29" },
  task: { bg: "#c3e88d", fg: "#191b29" },
  hook: { bg: "#f7768e", fg: "#191b29" },
  audio: { bg: "#ff9e64", fg: "#191b29" },
};
