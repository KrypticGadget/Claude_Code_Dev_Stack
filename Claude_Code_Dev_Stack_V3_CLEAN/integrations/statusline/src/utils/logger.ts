const debug = (message: string, ...args: any[]): void => {
  if (process.env.CLAUDE_POWERLINE_DEBUG) {
    console.error(`[DEBUG] ${message}`, ...args);
  }
};

export { debug };
