import { FileSystemNode, FileIconMapping } from '../types';

// File type mappings for icons and colors
export const FILE_ICON_MAPPINGS: FileIconMapping[] = [
  // Code files
  { extension: 'js', icon: 'javascript', color: '#f7df1e' },
  { extension: 'jsx', icon: 'react', color: '#61dafb' },
  { extension: 'ts', icon: 'typescript', color: '#3178c6' },
  { extension: 'tsx', icon: 'react', color: '#61dafb' },
  { extension: 'py', icon: 'python', color: '#3776ab' },
  { extension: 'java', icon: 'java', color: '#ed8b00' },
  { extension: 'c', icon: 'c', color: '#a8b9cc' },
  { extension: 'cpp', icon: 'cpp', color: '#00599c' },
  { extension: 'cs', icon: 'csharp', color: '#239120' },
  { extension: 'php', icon: 'php', color: '#777bb4' },
  { extension: 'rb', icon: 'ruby', color: '#cc342d' },
  { extension: 'go', icon: 'go', color: '#00add8' },
  { extension: 'rs', icon: 'rust', color: '#ce422b' },
  { extension: 'swift', icon: 'swift', color: '#fa7343' },
  { extension: 'kt', icon: 'kotlin', color: '#7f52ff' },
  
  // Web files
  { extension: 'html', icon: 'html', color: '#e34f26' },
  { extension: 'htm', icon: 'html', color: '#e34f26' },
  { extension: 'css', icon: 'css', color: '#1572b6' },
  { extension: 'scss', icon: 'sass', color: '#cf649a' },
  { extension: 'sass', icon: 'sass', color: '#cf649a' },
  { extension: 'less', icon: 'less', color: '#1d365d' },
  { extension: 'vue', icon: 'vue', color: '#4fc08d' },
  { extension: 'svelte', icon: 'svelte', color: '#ff3e00' },
  
  // Data files
  { extension: 'json', icon: 'json', color: '#ffa500' },
  { extension: 'xml', icon: 'xml', color: '#ff6600' },
  { extension: 'yaml', icon: 'yaml', color: '#cb171e' },
  { extension: 'yml', icon: 'yaml', color: '#cb171e' },
  { extension: 'toml', icon: 'toml', color: '#9c4221' },
  { extension: 'csv', icon: 'csv', color: '#217346' },
  { extension: 'sql', icon: 'database', color: '#336791' },
  
  // Document files
  { extension: 'pdf', icon: 'pdf', color: '#dc143c' },
  { extension: 'doc', icon: 'word', color: '#2b579a' },
  { extension: 'docx', icon: 'word', color: '#2b579a' },
  { extension: 'xls', icon: 'excel', color: '#217346' },
  { extension: 'xlsx', icon: 'excel', color: '#217346' },
  { extension: 'ppt', icon: 'powerpoint', color: '#d24726' },
  { extension: 'pptx', icon: 'powerpoint', color: '#d24726' },
  { extension: 'txt', icon: 'text', color: '#6c757d' },
  { extension: 'md', icon: 'markdown', color: '#000000' },
  { extension: 'rtf', icon: 'rtf', color: '#6c757d' },
  
  // Image files
  { extension: 'jpg', icon: 'image', color: '#ff6b6b' },
  { extension: 'jpeg', icon: 'image', color: '#ff6b6b' },
  { extension: 'png', icon: 'image', color: '#4ecdc4' },
  { extension: 'gif', icon: 'image', color: '#45b7d1' },
  { extension: 'svg', icon: 'svg', color: '#ffb347' },
  { extension: 'bmp', icon: 'image', color: '#ff6b6b' },
  { extension: 'ico', icon: 'image', color: '#96ceb4' },
  { extension: 'webp', icon: 'image', color: '#4ecdc4' },
  
  // Video files
  { extension: 'mp4', icon: 'video', color: '#ff4757' },
  { extension: 'avi', icon: 'video', color: '#ff4757' },
  { extension: 'mov', icon: 'video', color: '#ff4757' },
  { extension: 'wmv', icon: 'video', color: '#ff4757' },
  { extension: 'flv', icon: 'video', color: '#ff4757' },
  { extension: 'webm', icon: 'video', color: '#ff4757' },
  { extension: 'mkv', icon: 'video', color: '#ff4757' },
  
  // Audio files
  { extension: 'mp3', icon: 'audio', color: '#ff9ff3' },
  { extension: 'wav', icon: 'audio', color: '#ff9ff3' },
  { extension: 'flac', icon: 'audio', color: '#ff9ff3' },
  { extension: 'aac', icon: 'audio', color: '#ff9ff3' },
  { extension: 'ogg', icon: 'audio', color: '#ff9ff3' },
  { extension: 'wma', icon: 'audio', color: '#ff9ff3' },
  
  // Archive files
  { extension: 'zip', icon: 'archive', color: '#feca57' },
  { extension: 'rar', icon: 'archive', color: '#feca57' },
  { extension: '7z', icon: 'archive', color: '#feca57' },
  { extension: 'tar', icon: 'archive', color: '#feca57' },
  { extension: 'gz', icon: 'archive', color: '#feca57' },
  { extension: 'bz2', icon: 'archive', color: '#feca57' },
  
  // Config files
  { extension: 'env', icon: 'config', color: '#54a0ff' },
  { extension: 'config', icon: 'config', color: '#54a0ff' },
  { extension: 'ini', icon: 'config', color: '#54a0ff' },
  { extension: 'conf', icon: 'config', color: '#54a0ff' },
  { extension: 'properties', icon: 'config', color: '#54a0ff' },
  
  // System files
  { extension: 'exe', icon: 'executable', color: '#ff3838' },
  { extension: 'msi', icon: 'executable', color: '#ff3838' },
  { extension: 'deb', icon: 'executable', color: '#ff3838' },
  { extension: 'rpm', icon: 'executable', color: '#ff3838' },
  { extension: 'dmg', icon: 'executable', color: '#ff3838' },
  { extension: 'app', icon: 'executable', color: '#ff3838' },
  
  // Font files
  { extension: 'ttf', icon: 'font', color: '#2f3542' },
  { extension: 'otf', icon: 'font', color: '#2f3542' },
  { extension: 'woff', icon: 'font', color: '#2f3542' },
  { extension: 'woff2', icon: 'font', color: '#2f3542' },
  { extension: 'eot', icon: 'font', color: '#2f3542' },
];

// Default icons for types
export const DEFAULT_ICONS = {
  directory: { icon: 'folder', color: '#feca57' },
  file: { icon: 'file', color: '#6c757d' },
  hidden: { icon: 'file-hidden', color: '#adb5bd' },
  symlink: { icon: 'link', color: '#17a2b8' },
};

/**
 * Get the appropriate icon for a file system node
 */
export function getNodeIcon(node: FileSystemNode): string {
  if (node.type === 'directory') {
    return node.isExpanded ? 'folder-open' : 'folder';
  }

  if (!node.extension) {
    return DEFAULT_ICONS.file.icon;
  }

  const mapping = FILE_ICON_MAPPINGS.find(m => m.extension === node.extension.toLowerCase());
  return mapping?.icon || DEFAULT_ICONS.file.icon;
}

/**
 * Get the appropriate color for a file system node
 */
export function getNodeColor(node: FileSystemNode): string {
  if (node.type === 'directory') {
    return DEFAULT_ICONS.directory.color;
  }

  if (node.name.startsWith('.')) {
    return DEFAULT_ICONS.hidden.color;
  }

  if (!node.extension) {
    return DEFAULT_ICONS.file.color;
  }

  const mapping = FILE_ICON_MAPPINGS.find(m => m.extension === node.extension.toLowerCase());
  return mapping?.color || DEFAULT_ICONS.file.color;
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format date in relative or absolute format
 */
export function formatDate(date: Date): string {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) {
    return 'Today';
  } else if (diffInDays === 1) {
    return 'Yesterday';
  } else if (diffInDays < 7) {
    return `${diffInDays} days ago`;
  } else {
    return date.toLocaleDateString();
  }
}

/**
 * Validate file name
 */
export function isValidFileName(name: string): boolean {
  if (!name || name.trim() === '') return false;
  
  // Windows forbidden characters
  const forbidden = /[<>:"/\\|?*]/;
  if (forbidden.test(name)) return false;
  
  // Reserved names on Windows
  const reserved = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$/i;
  if (reserved.test(name)) return false;
  
  // Check for control characters
  if (/[\x00-\x1f\x80-\x9f]/.test(name)) return false;
  
  // Check length
  if (name.length > 255) return false;
  
  return true;
}

/**
 * Get relative path from full path
 */
export function getRelativePath(fullPath: string, basePath: string): string {
  if (!fullPath.startsWith(basePath)) {
    return fullPath;
  }
  
  const relative = fullPath.slice(basePath.length);
  return relative.startsWith('/') || relative.startsWith('\\') ? relative.slice(1) : relative;
}

/**
 * Parse file extension from name
 */
export function getFileExtension(fileName: string): string | undefined {
  const lastDot = fileName.lastIndexOf('.');
  if (lastDot === -1 || lastDot === 0) return undefined;
  return fileName.slice(lastDot + 1).toLowerCase();
}

/**
 * Get MIME type based on file extension
 */
export function getMimeType(extension: string): string {
  const mimeTypes: Record<string, string> = {
    // Text
    'txt': 'text/plain',
    'md': 'text/markdown',
    'html': 'text/html',
    'htm': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',
    'json': 'application/json',
    'xml': 'application/xml',
    'csv': 'text/csv',
    
    // Images
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'svg': 'image/svg+xml',
    'webp': 'image/webp',
    'bmp': 'image/bmp',
    'ico': 'image/x-icon',
    
    // Video
    'mp4': 'video/mp4',
    'webm': 'video/webm',
    'ogv': 'video/ogg',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'wmv': 'video/x-ms-wmv',
    'flv': 'video/x-flv',
    'mkv': 'video/x-matroska',
    
    // Audio
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'ogg': 'audio/ogg',
    'flac': 'audio/flac',
    'aac': 'audio/aac',
    'wma': 'audio/x-ms-wma',
    
    // Documents
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    
    // Archives
    'zip': 'application/zip',
    'rar': 'application/vnd.rar',
    '7z': 'application/x-7z-compressed',
    'tar': 'application/x-tar',
    'gz': 'application/gzip',
    'bz2': 'application/x-bzip2',
  };
  
  return mimeTypes[extension.toLowerCase()] || 'application/octet-stream';
}

/**
 * Sort file system nodes
 */
export function sortNodes(
  nodes: FileSystemNode[],
  sortBy: 'name' | 'size' | 'modified' | 'type',
  sortOrder: 'asc' | 'desc'
): FileSystemNode[] {
  const sorted = [...nodes].sort((a, b) => {
    // Always put directories first
    if (a.type !== b.type) {
      return a.type === 'directory' ? -1 : 1;
    }
    
    let comparison = 0;
    
    switch (sortBy) {
      case 'name':
        comparison = a.name.localeCompare(b.name, undefined, { numeric: true });
        break;
      case 'size':
        comparison = (a.size || 0) - (b.size || 0);
        break;
      case 'modified':
        comparison = a.modified.getTime() - b.modified.getTime();
        break;
      case 'type':
        const aExt = a.extension || '';
        const bExt = b.extension || '';
        comparison = aExt.localeCompare(bExt);
        break;
    }
    
    return sortOrder === 'desc' ? -comparison : comparison;
  });
  
  return sorted;
}

/**
 * Filter nodes based on search query
 */
export function filterNodes(nodes: FileSystemNode[], query: string): FileSystemNode[] {
  if (!query.trim()) return nodes;
  
  const searchTerm = query.toLowerCase();
  return nodes.filter(node => 
    node.name.toLowerCase().includes(searchTerm) ||
    node.path.toLowerCase().includes(searchTerm) ||
    (node.extension && node.extension.toLowerCase().includes(searchTerm))
  );
}

/**
 * Check if node is hidden
 */
export function isHiddenNode(node: FileSystemNode): boolean {
  return node.name.startsWith('.');
}

/**
 * Generate unique node ID
 */
export function generateNodeId(path: string): string {
  return btoa(path).replace(/[^a-zA-Z0-9]/g, '');
}

/**
 * Get parent path from file path
 */
export function getParentPath(path: string): string {
  const separator = path.includes('/') ? '/' : '\\';
  const parts = path.split(separator);
  return parts.slice(0, -1).join(separator) || separator;
}

/**
 * Join paths correctly
 */
export function joinPaths(...parts: string[]): string {
  return parts
    .filter(part => part && part.trim())
    .map(part => part.replace(/[\/\\]+$/, ''))
    .join('/')
    .replace(/\\/g, '/');
}

/**
 * Check if path is ancestor of another path
 */
export function isAncestorPath(ancestorPath: string, descendantPath: string): boolean {
  const normalizedAncestor = ancestorPath.replace(/\\/g, '/');
  const normalizedDescendant = descendantPath.replace(/\\/g, '/');
  
  return normalizedDescendant.startsWith(normalizedAncestor + '/') || 
         normalizedDescendant === normalizedAncestor;
}

/**
 * Debounce function for search
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Throttle function for frequent operations
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}