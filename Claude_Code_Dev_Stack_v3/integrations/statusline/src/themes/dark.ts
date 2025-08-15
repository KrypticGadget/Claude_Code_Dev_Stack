import type { ColorTheme } from "./index";

export const darkTheme: ColorTheme = {
  directory: { bg: "#8b4513", fg: "#ffffff" },
  git: { bg: "#404040", fg: "#ffffff" },
  model: { bg: "#2d2d2d", fg: "#ffffff" },
  session: { bg: "#202020", fg: "#00ffff" },
  block: { bg: "#2a2a2a", fg: "#87ceeb" },
  today: { bg: "#1a1a1a", fg: "#98fb98" },
  tmux: { bg: "#2f4f2f", fg: "#90ee90" },
  context: { bg: "#4a5568", fg: "#cbd5e0" },
  metrics: { bg: "#374151", fg: "#d1d5db" },
  version: { bg: "#3a3a4a", fg: "#b8b8d0" },
  // Dev Stack segments
  agent: { bg: "#4c1d95", fg: "#e0e7ff" },
  task: { bg: "#059669", fg: "#d1fae5" },
  hook: { bg: "#dc2626", fg: "#fef2f2" },
  audio: { bg: "#7c2d12", fg: "#fef2f2" },
};
