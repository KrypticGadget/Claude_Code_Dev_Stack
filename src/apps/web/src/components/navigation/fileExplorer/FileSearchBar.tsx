import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Typography,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  History as HistoryIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { FileSearchOptions, FileSystemNode } from '../../types';
import { getNodeIcon, getNodeColor } from '../../utils/fileExplorerUtils';

interface FileSearchBarProps {
  searchQuery: string;
  searchResults: FileSystemNode[];
  isSearching?: boolean;
  placeholder?: string;
  onSearch: (query: string, options?: Partial<FileSearchOptions>) => void;
  onClear: () => void;
  onResultSelect?: (node: FileSystemNode) => void;
  maxResultsShown?: number;
  showAdvancedOptions?: boolean;
  recentSearches?: string[];
  onSaveSearch?: (query: string) => void;
  className?: string;
}

interface SearchFilters {
  caseSensitive: boolean;
  regex: boolean;
  includeContent: boolean;
  fileTypes: string[];
  excludePatterns: string[];
  maxResults: number;
}

const DEFAULT_FILTERS: SearchFilters = {
  caseSensitive: false,
  regex: false,
  includeContent: false,
  fileTypes: [],
  excludePatterns: ['.git', 'node_modules', '.DS_Store'],
  maxResults: 100
};

const COMMON_FILE_TYPES = [
  { label: 'TypeScript/JavaScript', extensions: ['ts', 'tsx', 'js', 'jsx'] },
  { label: 'Styles', extensions: ['css', 'scss', 'sass', 'less'] },
  { label: 'Markup', extensions: ['html', 'htm', 'xml', 'svg'] },
  { label: 'Data', extensions: ['json', 'yaml', 'yml', 'csv'] },
  { label: 'Documents', extensions: ['md', 'txt', 'pdf', 'doc', 'docx'] },
  { label: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'] },
  { label: 'Config', extensions: ['env', 'config', 'ini', 'conf', 'toml'] }
];

export const FileSearchBar: React.FC<FileSearchBarProps> = ({
  searchQuery,
  searchResults,
  isSearching = false,
  placeholder = 'Search files and folders...',
  onSearch,
  onClear,
  onResultSelect,
  maxResultsShown = 10,
  showAdvancedOptions = true,
  recentSearches = [],
  onSaveSearch,
  className
}) => {
  const [localQuery, setLocalQuery] = useState(searchQuery);
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);
  const [showResults, setShowResults] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showRecentSearches, setShowRecentSearches] = useState(false);
  const [activeFilters, setActiveFilters] = useState(0);
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Update local query when prop changes
  useEffect(() => {
    setLocalQuery(searchQuery);
  }, [searchQuery]);

  // Show/hide results based on search state
  useEffect(() => {
    setShowResults(searchResults.length > 0 || isSearching);
  }, [searchResults.length, isSearching]);

  // Count active filters
  useEffect(() => {
    let count = 0;
    if (filters.caseSensitive) count++;
    if (filters.regex) count++;
    if (filters.includeContent) count++;
    if (filters.fileTypes.length > 0) count++;
    if (filters.excludePatterns.length > DEFAULT_FILTERS.excludePatterns.length) count++;
    if (filters.maxResults !== DEFAULT_FILTERS.maxResults) count++;
    setActiveFilters(count);
  }, [filters]);

  // Handle input change with debouncing
  const handleInputChange = useCallback((value: string) => {
    setLocalQuery(value);
    
    if (value.trim()) {
      const searchOptions: Partial<FileSearchOptions> = {
        query: value,
        caseSensitive: filters.caseSensitive,
        regex: filters.regex,
        includeContent: filters.includeContent,
        fileTypes: filters.fileTypes,
        excludePatterns: filters.excludePatterns,
        maxResults: filters.maxResults
      };
      onSearch(value, searchOptions);
      setShowRecentSearches(false);
    } else {
      onClear();
      setShowRecentSearches(recentSearches.length > 0);
    }
  }, [filters, onSearch, onClear, recentSearches.length]);

  const handleClear = useCallback(() => {
    setLocalQuery('');
    onClear();
    setShowResults(false);
    setShowRecentSearches(false);
    searchInputRef.current?.focus();
  }, [onClear]);

  const handleFilterToggle = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
    setShowFilters(true);
  }, []);

  const handleFilterClose = useCallback(() => {
    setAnchorEl(null);
    setShowFilters(false);
  }, []);

  const handleFilterChange = useCallback((newFilters: Partial<SearchFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    
    if (localQuery.trim()) {
      const searchOptions: Partial<FileSearchOptions> = {
        query: localQuery,
        caseSensitive: updatedFilters.caseSensitive,
        regex: updatedFilters.regex,
        includeContent: updatedFilters.includeContent,
        fileTypes: updatedFilters.fileTypes,
        excludePatterns: updatedFilters.excludePatterns,
        maxResults: updatedFilters.maxResults
      };
      onSearch(localQuery, searchOptions);
    }
  }, [filters, localQuery, onSearch]);

  const handleFileTypeToggle = useCallback((extensions: string[]) => {
    const newFileTypes = [...filters.fileTypes];
    const allSelected = extensions.every(ext => newFileTypes.includes(ext));
    
    if (allSelected) {
      // Remove all extensions
      extensions.forEach(ext => {
        const index = newFileTypes.indexOf(ext);
        if (index > -1) newFileTypes.splice(index, 1);
      });
    } else {
      // Add all extensions
      extensions.forEach(ext => {
        if (!newFileTypes.includes(ext)) {
          newFileTypes.push(ext);
        }
      });
    }
    
    handleFilterChange({ fileTypes: newFileTypes });
  }, [filters.fileTypes, handleFilterChange]);

  const handleResultClick = useCallback((node: FileSystemNode) => {
    onResultSelect?.(node);
    setShowResults(false);
    if (onSaveSearch && localQuery.trim()) {
      onSaveSearch(localQuery);
    }
  }, [onResultSelect, onSaveSearch, localQuery]);

  const handleRecentSearchClick = useCallback((query: string) => {
    setLocalQuery(query);
    handleInputChange(query);
    setShowRecentSearches(false);
  }, [handleInputChange]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      handleClear();
    } else if (event.key === 'Enter' && localQuery.trim()) {
      if (onSaveSearch) {
        onSaveSearch(localQuery);
      }
    }
  }, [handleClear, localQuery, onSaveSearch]);

  const handleInputFocus = useCallback(() => {
    if (!localQuery.trim() && recentSearches.length > 0) {
      setShowRecentSearches(true);
    } else if (searchResults.length > 0) {
      setShowResults(true);
    }
  }, [localQuery, recentSearches.length, searchResults.length]);

  const handleInputBlur = useCallback((event: React.FocusEvent) => {
    // Don't hide results if clicking on a result item
    if (resultsRef.current?.contains(event.relatedTarget as Node)) {
      return;
    }
    setTimeout(() => {
      setShowResults(false);
      setShowRecentSearches(false);
    }, 200);
  }, []);

  const displayedResults = searchResults.slice(0, maxResultsShown);
  const hasMoreResults = searchResults.length > maxResultsShown;

  return (
    <Box className={className} sx={{ position: 'relative', width: '100%' }}>
      {/* Search Input */}
      <TextField
        ref={searchInputRef}
        fullWidth
        variant="outlined"
        placeholder={placeholder}
        value={localQuery}
        onChange={(e) => handleInputChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={handleInputFocus}
        onBlur={handleInputBlur}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <Box display="flex" alignItems="center" gap={0.5}>
                {showAdvancedOptions && (
                  <Tooltip title="Search filters">
                    <IconButton
                      size="small"
                      onClick={handleFilterToggle}
                      color={activeFilters > 0 ? 'primary' : 'default'}
                    >
                      <Badge badgeContent={activeFilters > 0 ? activeFilters : undefined} color="primary">
                        <FilterIcon />
                      </Badge>
                    </IconButton>
                  </Tooltip>
                )}
                {localQuery && (
                  <Tooltip title="Clear search">
                    <IconButton size="small" onClick={handleClear}>
                      <ClearIcon />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            </InputAdornment>
          )
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'background.paper'
          }
        }}
      />

      {/* Search Results Dropdown */}
      {(showResults || showRecentSearches) && (
        <Paper
          ref={resultsRef}
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1300,
            maxHeight: 400,
            overflow: 'auto',
            mt: 0.5,
            boxShadow: 3
          }}
        >
          {showRecentSearches ? (
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <HistoryIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Recent Searches"
                  primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                />
              </ListItem>
              {recentSearches.map((query, index) => (
                <ListItem
                  key={index}
                  button
                  onClick={() => handleRecentSearchClick(query)}
                  sx={{ pl: 4 }}
                >
                  <ListItemText primary={query} />
                </ListItem>
              ))}
            </List>
          ) : isSearching ? (
            <Box p={2} textAlign="center">
              <Typography color="text.secondary">Searching...</Typography>
            </Box>
          ) : displayedResults.length > 0 ? (
            <List dense>
              {displayedResults.map((node) => (
                <ListItem
                  key={node.id}
                  button
                  onClick={() => handleResultClick(node)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ color: getNodeColor(node) }}>
                      {node.type === 'directory' ? <FolderIcon /> : <FileIcon />}
                    </Box>
                  </ListItemIcon>
                  <ListItemText
                    primary={node.name}
                    secondary={node.path}
                    primaryTypographyProps={{
                      sx: {
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }
                    }}
                    secondaryTypographyProps={{
                      sx: {
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontSize: '0.75rem'
                      }
                    }}
                  />
                </ListItem>
              ))}
              {hasMoreResults && (
                <ListItem>
                  <ListItemText
                    primary={
                      <Typography variant="caption" color="text.secondary" align="center">
                        +{searchResults.length - maxResultsShown} more results
                      </Typography>
                    }
                  />
                </ListItem>
              )}
            </List>
          ) : localQuery.trim() ? (
            <Box p={2} textAlign="center">
              <Typography color="text.secondary">No results found</Typography>
            </Box>
          ) : null}
        </Paper>
      )}

      {/* Filter Menu */}
      <Menu
        anchorEl={anchorEl}
        open={showFilters}
        onClose={handleFilterClose}
        PaperProps={{
          sx: { width: 320, maxHeight: 500 }
        }}
      >
        <Box p={2}>
          <Typography variant="subtitle2" gutterBottom>
            Search Options
          </Typography>
          
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.caseSensitive}
                onChange={(e) => handleFilterChange({ caseSensitive: e.target.checked })}
                size="small"
              />
            }
            label="Case sensitive"
          />
          
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.regex}
                onChange={(e) => handleFilterChange({ regex: e.target.checked })}
                size="small"
              />
            }
            label="Regular expressions"
          />
          
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.includeContent}
                onChange={(e) => handleFilterChange({ includeContent: e.target.checked })}
                size="small"
              />
            }
            label="Search file contents"
          />
        </Box>

        <Divider />

        <Box p={2}>
          <Typography variant="subtitle2" gutterBottom>
            File Types
          </Typography>
          
          {COMMON_FILE_TYPES.map((group) => {
            const allSelected = group.extensions.every(ext => filters.fileTypes.includes(ext));
            const someSelected = group.extensions.some(ext => filters.fileTypes.includes(ext));
            
            return (
              <FormControlLabel
                key={group.label}
                control={
                  <Checkbox
                    checked={allSelected}
                    indeterminate={someSelected && !allSelected}
                    onChange={() => handleFileTypeToggle(group.extensions)}
                    size="small"
                  />
                }
                label={group.label}
              />
            );
          })}
          
          {filters.fileTypes.length > 0 && (
            <Box mt={1}>
              <Typography variant="caption" color="text.secondary">
                Active filters:
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                {filters.fileTypes.map((type) => (
                  <Chip
                    key={type}
                    label={type}
                    size="small"
                    onDelete={() => {
                      const newFileTypes = filters.fileTypes.filter(t => t !== type);
                      handleFilterChange({ fileTypes: newFileTypes });
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </Box>

        <Divider />

        <Box p={2}>
          <Typography variant="subtitle2" gutterBottom>
            Exclude Patterns
          </Typography>
          
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {filters.excludePatterns.map((pattern) => (
              <Chip
                key={pattern}
                label={pattern}
                size="small"
                variant={DEFAULT_FILTERS.excludePatterns.includes(pattern) ? 'filled' : 'outlined'}
                onDelete={() => {
                  const newPatterns = filters.excludePatterns.filter(p => p !== pattern);
                  handleFilterChange({ excludePatterns: newPatterns });
                }}
              />
            ))}
          </Box>

          <TextField
            fullWidth
            placeholder="Add exclude pattern..."
            size="small"
            variant="outlined"
            sx={{ mt: 1 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value && !filters.excludePatterns.includes(value)) {
                  handleFilterChange({
                    excludePatterns: [...filters.excludePatterns, value]
                  });
                  input.value = '';
                }
              }
            }}
          />
        </Box>

        <Divider />

        <Box p={2}>
          <Typography variant="subtitle2" gutterBottom>
            Max Results: {filters.maxResults}
          </Typography>
          
          <input
            type="range"
            min="10"
            max="500"
            step="10"
            value={filters.maxResults}
            onChange={(e) => handleFilterChange({ maxResults: parseInt(e.target.value) })}
            style={{ width: '100%' }}
          />
        </Box>
      </Menu>
    </Box>
  );
};