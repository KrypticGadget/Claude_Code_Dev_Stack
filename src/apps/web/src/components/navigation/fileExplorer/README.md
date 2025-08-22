# Advanced File Explorer Component

A comprehensive, production-ready file explorer component built with React, TypeScript, and Material-UI that provides enterprise-grade file management capabilities.

## Features

### 🌳 **Hierarchical Tree View**
- Expandable/collapsible directory structure
- Virtualized rendering for performance with large directories
- Smooth animations and transitions
- Custom icons for different file types

### 🔍 **Advanced Search**
- Real-time fuzzy search with Fuse.js
- Search by file name, path, and content
- Advanced search filters (file types, case sensitivity, regex)
- Recent searches history
- Exclude patterns support

### 📁 **Complete File Operations**
- Create files and folders
- Delete with confirmation dialogs
- Rename with inline editing
- Copy and paste operations
- Cut and move functionality
- Drag and drop support between folders

### ⌨️ **Keyboard Navigation**
- Full keyboard accessibility
- Standard shortcuts (Ctrl+C, Ctrl+V, F2, Delete, etc.)
- Arrow key navigation
- Enter to open files/expand folders
- Escape to cancel operations

### 🎯 **Context Menus**
- Right-click context menus for all operations
- Dynamic menu items based on file type
- Keyboard shortcut hints
- Custom actions support

### 🔄 **Real-time Synchronization**
- File system watcher integration
- Live updates when files change
- WebSocket support for multi-user environments
- Automatic refresh on external changes

### 🎨 **Rich File Type Support**
- 50+ file type icons with colors
- MIME type detection
- Extension-based categorization
- Custom icon mappings

### 📱 **Responsive Design**
- Mobile-friendly interface
- Touch-friendly interactions
- Adaptive layout for different screen sizes
- PWA support

## Components

### `FileExplorer`
Main component that orchestrates all file explorer functionality.

```tsx
import { FileExplorer } from './components/fileExplorer';

<FileExplorer
  rootPath="/project"
  height={600}
  showSearch={true}
  enableDragDrop={true}
  enableKeyboardNavigation={true}
  multiSelect={true}
  onFileSelect={(files) => console.log(files)}
  onFileOpen={(file) => console.log('Opening:', file)}
  onFileOperation={(operation) => console.log('Operation:', operation)}
/>
```

### `TreeNode`
Individual tree node component with drag-drop and context menu support.

### `FileSearchBar`
Advanced search component with filters and fuzzy matching.

### `VirtualizedTree`
High-performance virtualized tree for large directories.

## Props

### FileExplorer Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `rootPath` | `string` | `"/"` | Root directory path |
| `height` | `number` | `600` | Component height in pixels |
| `width` | `number` | `undefined` | Component width |
| `showSearch` | `boolean` | `true` | Show search bar |
| `showContextMenu` | `boolean` | `true` | Enable context menus |
| `enableDragDrop` | `boolean` | `true` | Enable drag and drop |
| `enableKeyboardNavigation` | `boolean` | `true` | Enable keyboard shortcuts |
| `enableVirtualization` | `boolean` | `true` | Use virtualized scrolling |
| `multiSelect` | `boolean` | `true` | Allow multiple selection |
| `customActions` | `ContextMenuAction[]` | `[]` | Custom context menu actions |
| `onFileSelect` | `(nodes: FileSystemNode[]) => void` | `undefined` | File selection callback |
| `onFileOpen` | `(node: FileSystemNode) => void` | `undefined` | File open callback |
| `onFileOperation` | `(operation: FileOperation) => void` | `undefined` | File operation callback |
| `onError` | `(error: string) => void` | `undefined` | Error callback |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Create new file |
| `Ctrl+Shift+N` | Create new folder |
| `F2` | Rename selected item |
| `Delete` | Delete selected items |
| `Ctrl+C` | Copy selected items |
| `Ctrl+X` | Cut selected items |
| `Ctrl+V` | Paste items |
| `F5` | Refresh directory |
| `Ctrl+F` | Focus search |
| `Ctrl+H` | Toggle hidden files |
| `Enter` | Open file/expand folder |
| `Escape` | Cancel current operation |
| `Arrow Keys` | Navigate tree |

## File Operations

### Creating Files/Folders
```tsx
const { actions } = useFileExplorer('/project');

// Create a new file
await actions.createNode('/project/src', 'newFile.tsx', 'file');

// Create a new folder
await actions.createNode('/project/src', 'components', 'directory');
```

### File Operations
```tsx
// Delete files
await actions.deleteNodes(['/project/oldFile.js']);

// Move files
await actions.moveNodes(['/project/file.js'], '/project/archive');

// Copy files
await actions.copyNodes(['/project/file.js'], '/project/backup');

// Rename file
await actions.renameNode('/project/file.js', 'newName.js');
```

### Search
```tsx
// Basic search
await actions.searchFiles('component');

// Advanced search with options
await actions.searchFiles('*.tsx', {
  caseSensitive: false,
  regex: true,
  fileTypes: ['tsx', 'ts'],
  excludePatterns: ['node_modules', '.git'],
  maxResults: 50
});
```

## Styling

The component uses Material-UI's theming system and can be customized through:

- Theme overrides
- CSS-in-JS styling
- Custom CSS classes
- Material-UI component props

```tsx
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  components: {
    MuiTreeView: {
      styleOverrides: {
        root: {
          // Custom tree styles
        }
      }
    }
  }
});

<ThemeProvider theme={theme}>
  <FileExplorer />
</ThemeProvider>
```

## Performance

- **Virtualized Rendering**: Handles thousands of files efficiently
- **Debounced Search**: Prevents excessive API calls
- **Memoized Components**: Reduces unnecessary re-renders
- **Lazy Loading**: Loads directory contents on demand
- **Code Splitting**: Components are lazily loaded

## Accessibility

- **ARIA Labels**: Comprehensive accessibility labels
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Compatible with screen readers
- **Focus Management**: Proper focus handling
- **High Contrast**: Supports high contrast themes

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Dependencies

- React 18+
- Material-UI 5+
- TypeScript 4.5+
- react-dnd 16+
- react-window 1.8+
- fuse.js 7+
- react-hotkeys-hook 4+

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Examples

### Basic Usage
```tsx
import { FileExplorer } from './components/fileExplorer';

function App() {
  const handleFileSelect = (files) => {
    console.log('Selected files:', files);
  };

  const handleFileOpen = (file) => {
    if (file.type === 'file') {
      // Open file in editor
      openInEditor(file.path);
    }
  };

  return (
    <FileExplorer
      rootPath="/workspace"
      height={600}
      onFileSelect={handleFileSelect}
      onFileOpen={handleFileOpen}
    />
  );
}
```

### Custom Context Actions
```tsx
const customActions = [
  {
    id: 'git-add',
    label: 'Add to Git',
    icon: 'git',
    action: (nodeIds) => {
      nodeIds.forEach(id => gitAdd(nodes[id].path));
    }
  },
  {
    id: 'open-terminal',
    label: 'Open Terminal Here',
    icon: 'terminal',
    action: (nodeIds) => {
      const path = nodes[nodeIds[0]].path;
      openTerminal(path);
    }
  }
];

<FileExplorer
  customActions={customActions}
  // ... other props
/>
```

### Integration with File Server
```tsx
import { FileExplorer, useFileExplorer } from './components/fileExplorer';

function MyFileExplorer() {
  const { state, actions } = useFileExplorer('/project');
  
  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8080/files');
    
    ws.onmessage = (event) => {
      const fileEvent = JSON.parse(event.data);
      if (fileEvent.type === 'file-changed') {
        actions.refreshDirectory(fileEvent.path);
      }
    };
    
    return () => ws.close();
  }, [actions]);

  return (
    <FileExplorer
      {...state}
      onFileOperation={(operation) => {
        // Send operation to server
        fetch('/api/files/operation', {
          method: 'POST',
          body: JSON.stringify(operation)
        });
      }}
    />
  );
}
```