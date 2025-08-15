export function hexToAnsi(hex: string, isBackground: boolean): string {
  if (isBackground && (hex.toLowerCase() === "transparent" || hex.toLowerCase() === "none")) {
    return "\x1b[49m";
  }
  
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `\x1b[${isBackground ? "48" : "38"};2;${r};${g};${b}m`;
}

export function extractBgToFg(ansiCode: string): string {
  const match = ansiCode.match(/48;2;(\d+);(\d+);(\d+)/);
  if (match) {
    return `\x1b[38;2;${match[1]};${match[2]};${match[3]}m`;
  }
  return ansiCode.replace("48", "38");
}
