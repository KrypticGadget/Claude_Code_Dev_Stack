import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  IconButton,
  Box,
  Checkbox,
  FormControlLabel,
  Typography,
  Paper,
  Chip
} from '@mui/material';
import {
  Close,
  Search,
  NavigateNext,
  NavigateBefore,
  KeyboardArrowUp,
  KeyboardArrowDown
} from '@mui/icons-material';
import { Terminal } from 'xterm';
import { SearchAddon } from 'xterm-addon-search';

interface TerminalSearchProps {
  open: boolean;
  onClose: () => void;
  onSearch: (query: string, options?: { caseSensitive?: boolean; wholeWord?: boolean; regex?: boolean }) => void;
  terminalRef: React.RefObject<Terminal | null>;
  searchAddon: SearchAddon | null;
}

export const TerminalSearch: React.FC<TerminalSearchProps> = ({
  open,
  onClose,
  onSearch,
  terminalRef,
  searchAddon
}) => {
  const [query, setQuery] = useState('');
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [wholeWord, setWholeWord] = useState(false);
  const [useRegex, setUseRegex] = useState(false);
  const [currentMatch, setCurrentMatch] = useState(0);
  const [totalMatches, setTotalMatches] = useState(0);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when dialog opens
  useEffect(() => {
    if (open && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  // Load search history from localStorage
  useEffect(() => {
    const history = localStorage.getItem('terminal-search-history');
    if (history) {
      try {
        setSearchHistory(JSON.parse(history));
      } catch (error) {
        console.error('Failed to load search history:', error);
      }
    }
  }, []);

  // Save search history to localStorage
  const saveSearchHistory = useCallback((newHistory: string[]) => {
    localStorage.setItem('terminal-search-history', JSON.stringify(newHistory));
    setSearchHistory(newHistory);
  }, []);

  // Add query to search history
  const addToHistory = useCallback((searchQuery: string) => {
    if (!searchQuery.trim() || searchHistory.includes(searchQuery)) return;
    
    const newHistory = [searchQuery, ...searchHistory.slice(0, 19)]; // Keep last 20 searches
    saveSearchHistory(newHistory);
  }, [searchHistory, saveSearchHistory]);

  // Perform search
  const performSearch = useCallback((searchQuery: string, direction: 'next' | 'previous' = 'next') => {
    if (!searchAddon || !searchQuery.trim()) return;

    const options = {
      caseSensitive,
      wholeWord,
      regex: useRegex
    };

    try {
      if (direction === 'next') {
        const found = searchAddon.findNext(searchQuery, options);
        if (found) {
          setCurrentMatch(prev => prev + 1);
        }
      } else {
        const found = searchAddon.findPrevious(searchQuery, options);
        if (found) {
          setCurrentMatch(prev => Math.max(1, prev - 1));
        }
      }

      onSearch(searchQuery, options);
    } catch (error) {
      console.error('Search error:', error);
    }
  }, [searchAddon, caseSensitive, wholeWord, useRegex, onSearch]);

  // Handle search input change
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = event.target.value;
    setQuery(newQuery);
    setHistoryIndex(-1);

    if (newQuery.trim()) {
      performSearch(newQuery);
    } else {
      setCurrentMatch(0);
      setTotalMatches(0);
    }
  }, [performSearch]);

  // Handle Enter key
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    switch (event.key) {
      case 'Enter':
        event.preventDefault();
        if (query.trim()) {
          addToHistory(query);
          performSearch(query, event.shiftKey ? 'previous' : 'next');
        }
        break;

      case 'Escape':
        event.preventDefault();
        onClose();
        break;

      case 'ArrowUp':
        event.preventDefault();
        if (searchHistory.length > 0) {
          const newIndex = Math.min(historyIndex + 1, searchHistory.length - 1);
          setHistoryIndex(newIndex);
          setQuery(searchHistory[newIndex]);
        }
        break;

      case 'ArrowDown':
        event.preventDefault();
        if (historyIndex > 0) {
          const newIndex = historyIndex - 1;
          setHistoryIndex(newIndex);
          setQuery(searchHistory[newIndex]);
        } else if (historyIndex === 0) {
          setHistoryIndex(-1);
          setQuery('');
        }
        break;

      case 'F3':
        event.preventDefault();
        if (query.trim()) {
          performSearch(query, event.shiftKey ? 'previous' : 'next');
        }
        break;
    }
  }, [query, historyIndex, searchHistory, performSearch, addToHistory, onClose]);

  // Handle next/previous buttons
  const handleNext = useCallback(() => {
    if (query.trim()) {
      performSearch(query, 'next');
    }
  }, [query, performSearch]);

  const handlePrevious = useCallback(() => {
    if (query.trim()) {
      performSearch(query, 'previous');
    }
  }, [query, performSearch]);

  // Clear search
  const handleClear = useCallback(() => {
    setQuery('');
    setCurrentMatch(0);
    setTotalMatches(0);
    setHistoryIndex(-1);
    inputRef.current?.focus();
  }, []);

  // Handle search history item click
  const handleHistoryClick = useCallback((historyQuery: string) => {
    setQuery(historyQuery);
    setHistoryIndex(-1);
    performSearch(historyQuery);
  }, [performSearch]);

  if (!open) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          position: 'fixed',
          top: 20,
          right: 20,
          left: 'auto',
          bottom: 'auto',
          margin: 0,
          minWidth: 400,
          maxWidth: 500
        }
      }}
      disableAutoFocus
      disableEnforceFocus
    >
      <DialogContent sx={{ p: 2 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Search color="action" />
          <TextField
            ref={inputRef}
            fullWidth
            size="small"
            placeholder="Search in terminal..."
            value={query}
            onChange={handleSearchChange}
            onKeyDown={handleKeyDown}
            InputProps={{
              endAdornment: (
                <Box display="flex" alignItems="center" gap={0.5}>
                  {totalMatches > 0 && (
                    <Typography variant="caption" color="text.secondary">
                      {currentMatch}/{totalMatches}
                    </Typography>
                  )}
                  <IconButton size="small" onClick={handlePrevious} disabled={!query.trim()}>
                    <NavigateBefore fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={handleNext} disabled={!query.trim()}>
                    <NavigateNext fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={handleClear}>
                    <Close fontSize="small" />
                  </IconButton>
                </Box>
              )
            }}
          />
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>

        <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
          <FormControlLabel
            control={
              <Checkbox
                size="small"
                checked={caseSensitive}
                onChange={(e) => setCaseSensitive(e.target.checked)}
              />
            }
            label="Case sensitive"
            sx={{ fontSize: '0.875rem' }}
          />
          <FormControlLabel
            control={
              <Checkbox
                size="small"
                checked={wholeWord}
                onChange={(e) => setWholeWord(e.target.checked)}
              />
            }
            label="Whole word"
            sx={{ fontSize: '0.875rem' }}
          />
          <FormControlLabel
            control={
              <Checkbox
                size="small"
                checked={useRegex}
                onChange={(e) => setUseRegex(e.target.checked)}
              />
            }
            label="Regex"
            sx={{ fontSize: '0.875rem' }}
          />
        </Box>

        {searchHistory.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Recent searches:
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
              {searchHistory.slice(0, 5).map((historyQuery, index) => (
                <Chip
                  key={index}
                  label={historyQuery}
                  size="small"
                  variant="outlined"
                  onClick={() => handleHistoryClick(historyQuery)}
                  sx={{
                    fontSize: '0.75rem',
                    height: 24,
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
        )}

        <Box mt={2} pt={1} borderTop={1} borderColor="divider">
          <Typography variant="caption" color="text.secondary">
            <strong>Shortcuts:</strong> Enter (next), Shift+Enter (previous), F3 (next), Shift+F3 (previous), ↑↓ (history)
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
};