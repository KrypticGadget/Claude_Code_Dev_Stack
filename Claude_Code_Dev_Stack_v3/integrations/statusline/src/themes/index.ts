import { darkTheme } from "./dark";
import { lightTheme } from "./light";
import { nordTheme } from "./nord";
import { tokyoNightTheme } from "./tokyo-night";
import { rosePineTheme } from "./rose-pine";

export interface SegmentColor {
  bg: string;
  fg: string;
}

export interface ColorTheme {
  directory: SegmentColor;
  git: SegmentColor;
  model: SegmentColor;
  session: SegmentColor;
  block: SegmentColor;
  today: SegmentColor;
  tmux: SegmentColor;
  context: SegmentColor;
  metrics: SegmentColor;
  version: SegmentColor;
  // Dev Stack segments
  agent: SegmentColor;
  task: SegmentColor;
  hook: SegmentColor;
  audio: SegmentColor;
}

export interface PowerlineColors {
  reset: string;
  modeBg: string;
  modeFg: string;
  gitBg: string;
  gitFg: string;
  modelBg: string;
  modelFg: string;
  sessionBg: string;
  sessionFg: string;
  blockBg: string;
  blockFg: string;
  todayBg: string;
  todayFg: string;
  tmuxBg: string;
  tmuxFg: string;
  contextBg: string;
  contextFg: string;
  metricsBg: string;
  metricsFg: string;
  versionBg: string;
  versionFg: string;
  // Dev Stack colors
  agentBg: string;
  agentFg: string;
  taskBg: string;
  taskFg: string;
  hookBg: string;
  hookFg: string;
  audioBg: string;
  audioFg: string;
}

export const BUILT_IN_THEMES: Record<string, ColorTheme> = {
  dark: darkTheme,
  light: lightTheme,
  nord: nordTheme,
  "tokyo-night": tokyoNightTheme,
  "rose-pine": rosePineTheme,
};

export function getTheme(themeName: string): ColorTheme | null {
  return BUILT_IN_THEMES[themeName] || null;
}

export { darkTheme, lightTheme, nordTheme, tokyoNightTheme, rosePineTheme };
