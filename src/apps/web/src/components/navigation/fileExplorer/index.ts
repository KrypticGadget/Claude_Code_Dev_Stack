// File Explorer Components
export { FileExplorer } from './FileExplorer';
export { TreeNode } from './TreeNode';
export { FileSearchBar } from './FileSearchBar';
export { VirtualizedTree, AutoSizedVirtualizedTree } from './VirtualizedTree';

// Re-export types for convenience
export type {
  FileSystemNode,
  FileExplorerState,
  FileOperation,
  FileWatchEvent,
  FileSearchOptions,
  FilePreview,
  ContextMenuAction,
  FileIconMapping,
  KeyboardShortcut,
  VirtualizedTreeProps,
  FileExplorerProps,
  UseFileExplorerReturn
} from '../../types';

// Re-export hook
export { useFileExplorer } from '../../hooks/useFileExplorer';

// Re-export utilities
export {
  getNodeIcon,
  getNodeColor,
  formatFileSize,
  formatDate,
  isValidFileName,
  getRelativePath,
  getFileExtension,
  getMimeType,
  sortNodes,
  filterNodes,
  isHiddenNode,
  generateNodeId,
  getParentPath,
  joinPaths,
  isAncestorPath,
  debounce,
  throttle,
  FILE_ICON_MAPPINGS,
  DEFAULT_ICONS
} from '../../utils/fileExplorerUtils';