import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { SearchAddon } from 'xterm-addon-search';
import { CanvasAddon } from 'xterm-addon-canvas';
import { WebglAddon } from 'xterm-addon-webgl';
import { AttachAddon } from 'xterm-addon-attach';
import { SerializeAddon } from 'xterm-addon-serialize';
import { Box, Paper, useTheme } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { useHotkeys } from 'react-hotkeys-hook';
import 'xterm/css/xterm.css';

import { useTerminalStore } from '../../store/terminalStore';
import { TerminalSession, TerminalDragDropData } from '../../types/terminal';
import { TerminalContextMenu } from './TerminalContextMenu';
import { TerminalSearch } from './TerminalSearch';

interface TerminalProps {
  sessionId: string;
  className?: string;
  onTitleChange?: (title: string) => void;
  onCommand?: (command: string) => void;
  onResize?: (cols: number, rows: number) => void;
}

export const Terminal: React.FC<TerminalProps> = ({
  sessionId,
  className,
  onTitleChange,
  onCommand,
  onResize
}) => {
  const theme = useTheme();
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const searchAddonRef = useRef<SearchAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number } | null>(null);
  const [showSearch, setShowSearch] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const {
    config,
    getSessionById,
    updateSession,
    addToHistory,
    addCommandHistory,
    updateConfig
  } = useTerminalStore();

  const session = getSessionById(sessionId);

  // Initialize terminal
  useEffect(() => {
    if (!terminalRef.current || !session) return;

    const terminal = new XTerm({
      theme: {
        foreground: config.theme.foreground,
        background: config.theme.background,
        cursor: config.theme.cursor,
        cursorAccent: config.theme.cursorAccent,
        selection: config.theme.selection,
        black: config.theme.black,
        red: config.theme.red,
        green: config.theme.green,
        yellow: config.theme.yellow,
        blue: config.theme.blue,
        magenta: config.theme.magenta,
        cyan: config.theme.cyan,
        white: config.theme.white,
        brightBlack: config.theme.brightBlack,
        brightRed: config.theme.brightRed,
        brightGreen: config.theme.brightGreen,
        brightYellow: config.theme.brightYellow,
        brightBlue: config.theme.brightBlue,
        brightMagenta: config.theme.brightMagenta,
        brightCyan: config.theme.brightCyan,
        brightWhite: config.theme.brightWhite
      },
      fontSize: config.fontSize,
      fontFamily: config.fontFamily,
      fontWeight: config.fontWeight,
      fontWeightBold: config.fontWeightBold,
      lineHeight: config.lineHeight,
      letterSpacing: config.letterSpacing,
      scrollback: config.scrollback,
      cursorBlink: config.cursorBlink,
      cursorStyle: config.cursorStyle,
      bellSound: config.bellSound,
      allowTransparency: config.allowTransparency,
      macOptionIsMeta: config.macOptionIsMeta,
      rightClickSelectsWord: config.rightClickSelectsWord,
      fastScrollModifier: config.fastScrollModifier,
      fastScrollSensitivity: config.fastScrollSensitivity,
      scrollSensitivity: config.scrollSensitivity,
      cols: session.size.cols,
      rows: session.size.rows
    });

    // Add addons
    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    const searchAddon = new SearchAddon();
    const serializeAddon = new SerializeAddon();

    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);
    terminal.loadAddon(searchAddon);
    terminal.loadAddon(serializeAddon);

    // Add renderer addon based on config
    if (config.rendererType === 'canvas') {
      terminal.loadAddon(new CanvasAddon());
    } else if (config.rendererType === 'webgl') {
      try {
        terminal.loadAddon(new WebglAddon());
      } catch (error) {
        console.warn('WebGL addon failed, falling back to canvas:', error);
        terminal.loadAddon(new CanvasAddon());
      }
    }

    terminal.open(terminalRef.current);
    fitAddon.fit();

    // Store references
    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;
    searchAddonRef.current = searchAddon;

    // Handle terminal events
    terminal.onData((data) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'data',
          sessionId,
          data
        }));
      }
    });

    terminal.onResize(({ cols, rows }) => {
      updateSession(sessionId, { size: { cols, rows } });
      onResize?.(cols, rows);
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'resize',
          sessionId,
          cols,
          rows
        }));
      }
    });

    terminal.onTitleChange((title) => {
      updateSession(sessionId, { title });
      onTitleChange?.(title);
    });

    let currentCommand = '';
    terminal.onData((data) => {
      if (data === '\r') {
        // Enter pressed
        if (currentCommand.trim()) {
          addToHistory(sessionId, currentCommand.trim());
          addCommandHistory({
            command: currentCommand.trim(),
            timestamp: new Date(),
            cwd: session.cwd,
            sessionId
          });
          onCommand?.(currentCommand.trim());
        }
        currentCommand = '';
      } else if (data === '\x7f' || data === '\b') {
        // Backspace
        currentCommand = currentCommand.slice(0, -1);
      } else if (data.charCodeAt(0) >= 32) {
        // Printable character
        currentCommand += data;
      }
    });

    // Connect to WebSocket for PTY communication
    connectWebSocket();

    return () => {
      terminal.dispose();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId, config]);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`ws://localhost:3001/terminal/${sessionId}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log(`Terminal WebSocket connected for session ${sessionId}`);
      
      // Request PTY creation
      ws.send(JSON.stringify({
        type: 'create',
        sessionId,
        shell: session?.shell || 'bash',
        cwd: session?.cwd || process.cwd?.() || '/',
        env: session?.environment || {},
        cols: session?.size.cols || 80,
        rows: session?.size.rows || 24
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'data':
          if (xtermRef.current) {
            xtermRef.current.write(message.data);
          }
          break;
        case 'exit':
          console.log(`Terminal session ${sessionId} exited with code ${message.exitCode}`);
          if (xtermRef.current) {
            xtermRef.current.write(`\r\n[Process exited with code ${message.exitCode}]\r\n`);
          }
          break;
        case 'error':
          console.error('Terminal error:', message.error);
          if (xtermRef.current) {
            xtermRef.current.write(`\r\n[Error: ${message.error}]\r\n`);
          }
          break;
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log(`Terminal WebSocket disconnected for session ${sessionId}`);
    };

    ws.onerror = (error) => {
      console.error('Terminal WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  }, [sessionId, session]);

  // Handle file drops
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (!xtermRef.current) return;

    acceptedFiles.forEach((file) => {
      const path = (file as any).path || file.name;
      xtermRef.current?.write(`"${path}" `);
    });
  }, []);

  const { getRootProps, isDragActive } = useDropzone({
    onDrop,
    noClick: true,
    noKeyboard: true
  });

  // Keyboard shortcuts
  useHotkeys('ctrl+shift+f', () => setShowSearch(true), { enableOnTags: ['INPUT'] });
  useHotkeys('ctrl+shift+c', () => {
    if (xtermRef.current && xtermRef.current.hasSelection()) {
      navigator.clipboard.writeText(xtermRef.current.getSelection());
    }
  }, { enableOnTags: ['INPUT'] });
  useHotkeys('ctrl+shift+v', () => {
    navigator.clipboard.readText().then((text) => {
      if (xtermRef.current) {
        xtermRef.current.write(text);
      }
    });
  }, { enableOnTags: ['INPUT'] });
  useHotkeys('ctrl+=', () => {
    const newSize = Math.min(config.fontSize + 1, 32);
    updateConfig({ fontSize: newSize });
  });
  useHotkeys('ctrl+-', () => {
    const newSize = Math.max(config.fontSize - 1, 8);
    updateConfig({ fontSize: newSize });
  });
  useHotkeys('ctrl+0', () => {
    updateConfig({ fontSize: 14 });
  });

  // Fit terminal on window resize
  useEffect(() => {
    const handleResize = () => {
      if (fitAddonRef.current) {
        setTimeout(() => fitAddonRef.current?.fit(), 0);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle context menu
  const handleContextMenu = useCallback((event: React.MouseEvent) => {
    event.preventDefault();
    setContextMenu({ x: event.clientX, y: event.clientY });
  }, []);

  const handleCloseContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  // Terminal actions
  const handleCopy = useCallback(() => {
    if (xtermRef.current && xtermRef.current.hasSelection()) {
      navigator.clipboard.writeText(xtermRef.current.getSelection());
    }
    setContextMenu(null);
  }, []);

  const handlePaste = useCallback(() => {
    navigator.clipboard.readText().then((text) => {
      if (xtermRef.current) {
        xtermRef.current.write(text);
      }
    });
    setContextMenu(null);
  }, []);

  const handleClear = useCallback(() => {
    if (xtermRef.current) {
      xtermRef.current.clear();
    }
    setContextMenu(null);
  }, []);

  const handleSelectAll = useCallback(() => {
    if (xtermRef.current) {
      xtermRef.current.selectAll();
    }
    setContextMenu(null);
  }, []);

  const handleSearch = useCallback((query: string, options?: { caseSensitive?: boolean; wholeWord?: boolean; regex?: boolean }) => {
    if (searchAddonRef.current && xtermRef.current) {
      searchAddonRef.current.findNext(query, options);
    }
  }, []);

  if (!session) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height="100%"
        color="text.secondary"
      >
        Session not found
      </Box>
    );
  }

  return (
    <Box
      {...getRootProps()}
      sx={{
        height: '100%',
        width: '100%',
        position: 'relative',
        backgroundColor: config.theme.background,
        border: isDragActive ? `2px dashed ${theme.palette.primary.main}` : 'none',
        opacity: isDragActive ? 0.8 : 1,
        transition: 'opacity 0.2s ease-in-out'
      }}
      className={className}
      onContextMenu={handleContextMenu}
    >
      <Box
        ref={terminalRef}
        sx={{
          height: '100%',
          width: '100%',
          '& .xterm': {
            height: '100% !important',
            width: '100% !important'
          },
          '& .xterm-viewport': {
            width: '100% !important'
          }
        }}
      />

      {isDragActive && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            color: 'white',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            zIndex: 1000
          }}
        >
          Drop files to insert paths
        </Box>
      )}

      {!isConnected && (
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            padding: '4px 8px',
            backgroundColor: 'error.main',
            color: 'error.contrastText',
            borderRadius: 1,
            fontSize: '0.75rem',
            zIndex: 1000
          }}
        >
          Disconnected
        </Box>
      )}

      <TerminalContextMenu
        open={!!contextMenu}
        anchorPosition={contextMenu}
        onClose={handleCloseContextMenu}
        onCopy={handleCopy}
        onPaste={handlePaste}
        onSelectAll={handleSelectAll}
        onClear={handleClear}
        onSearch={() => setShowSearch(true)}
        hasSelection={xtermRef.current?.hasSelection() || false}
      />

      <TerminalSearch
        open={showSearch}
        onClose={() => setShowSearch(false)}
        onSearch={handleSearch}
        terminalRef={xtermRef}
        searchAddon={searchAddonRef.current}
      />
    </Box>
  );
};