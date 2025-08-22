import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  Info as InfoIcon,
  Launch as LaunchIcon,
  Code as CodeIcon,
  Visibility as PreviewIcon,
  Download as DownloadIcon,
  Share as ShareIcon
} from '@mui/icons-material';
import { FileExplorer, FileSystemNode, FileOperation } from '../../components/fileExplorer';

interface FileDetails {
  node: FileSystemNode | null;
  operation: FileOperation | null;
}

export const FileExplorerPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [selectedFiles, setSelectedFiles] = useState<FileSystemNode[]>([]);
  const [fileDetails, setFileDetails] = useState<FileDetails>({
    node: null,
    operation: null
  });
  const [previewDialog, setPreviewDialog] = useState<{
    open: boolean;
    node: FileSystemNode | null;
  }>({
    open: false,
    node: null
  });

  const handleFileSelect = useCallback((nodes: FileSystemNode[]) => {
    setSelectedFiles(nodes);
    if (nodes.length === 1) {
      setFileDetails({ ...fileDetails, node: nodes[0] });
    } else {
      setFileDetails({ ...fileDetails, node: null });
    }
  }, [fileDetails]);

  const handleFileOpen = useCallback((node: FileSystemNode) => {
    if (node.type === 'file') {
      setPreviewDialog({ open: true, node });
    }
  }, []);

  const handleFileOperation = useCallback((operation: FileOperation) => {
    setFileDetails({ ...fileDetails, operation });
    console.log('File operation:', operation);
  }, [fileDetails]);

  const handleError = useCallback((error: string) => {
    console.error('File explorer error:', error);
  }, []);

  const formatFileInfo = (node: FileSystemNode) => {
    const info = [];
    
    if (node.type === 'file' && node.size !== undefined) {
      const size = node.size < 1024 ? `${node.size} B` :
                   node.size < 1024 * 1024 ? `${(node.size / 1024).toFixed(1)} KB` :
                   `${(node.size / (1024 * 1024)).toFixed(1)} MB`;
      info.push(`Size: ${size}`);
    }
    
    if (node.extension) {
      info.push(`Type: ${node.extension.toUpperCase()} file`);
    }
    
    if (node.mimeType) {
      info.push(`MIME: ${node.mimeType}`);
    }
    
    info.push(`Created: ${node.created.toLocaleDateString()}`);
    info.push(`Modified: ${node.modified.toLocaleDateString()}`);
    
    if (node.permissions) {
      const perms = [];
      if (node.permissions.read) perms.push('Read');
      if (node.permissions.write) perms.push('Write');
      if (node.permissions.execute) perms.push('Execute');
      info.push(`Permissions: ${perms.join(', ')}`);
    }
    
    return info;
  };

  const getPreviewContent = (node: FileSystemNode) => {
    if (!node || node.type !== 'file') return null;

    // In a real implementation, this would fetch file content from the server
    const mockContent = {
      'package.json': JSON.stringify({
        "name": "file-explorer-demo",
        "version": "1.0.0",
        "description": "Advanced file explorer with React",
        "main": "index.tsx",
        "dependencies": {
          "react": "^18.2.0",
          "react-dom": "^18.2.0",
          "@mui/material": "^5.14.18"
        }
      }, null, 2),
      'README.md': `# File Explorer Demo

This is an advanced file explorer component built with React, TypeScript, and Material-UI.

## Features

- **Tree View**: Hierarchical file/folder display with expand/collapse
- **File Operations**: Create, delete, move, copy, rename files and folders
- **Search Functionality**: Real-time file search with fuzzy matching
- **Real-time Synchronization**: Watch file system changes and update UI
- **Drag-Drop Support**: Drag files between folders, external file drops
- **Keyboard Navigation**: Full keyboard accessibility with shortcuts
- **Context Menus**: Right-click menus for file operations
- **File Icons**: Type-specific icons for different file extensions

## Usage

\`\`\`tsx
import { FileExplorer } from './components/fileExplorer';

function App() {
  return (
    <FileExplorer
      rootPath="/project"
      height={600}
      enableDragDrop={true}
      enableKeyboardNavigation={true}
      onFileSelect={(files) => console.log(files)}
      onFileOpen={(file) => console.log('Open:', file)}
    />
  );
}
\`\`\`
`,
      'App.tsx': `import React from 'react';
import { FileExplorer } from './components/fileExplorer';

export const App: React.FC = () => {
  return (
    <div className="app">
      <header>
        <h1>File Explorer Demo</h1>
      </header>
      <main>
        <FileExplorer
          rootPath="/"
          height={600}
          showSearch={true}
          enableDragDrop={true}
          enableKeyboardNavigation={true}
          onFileSelect={(files) => {
            console.log('Selected files:', files);
          }}
          onFileOpen={(file) => {
            console.log('Opening file:', file);
          }}
        />
      </main>
    </div>
  );
};`
    };

    return mockContent[node.name as keyof typeof mockContent] || `// Content of ${node.name}
// This is a preview of the file content.
// In a real implementation, this would be loaded from the server.

console.log('File: ${node.name}');
console.log('Path: ${node.path}');
console.log('Type: ${node.type}');
`;
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Advanced File Explorer
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          A comprehensive file explorer component with tree view, search, drag-drop, 
          keyboard navigation, and real-time synchronization capabilities.
        </Typography>
        
        <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
          <Chip label="React" color="primary" variant="outlined" />
          <Chip label="TypeScript" color="primary" variant="outlined" />
          <Chip label="Material-UI" color="primary" variant="outlined" />
          <Chip label="Drag & Drop" color="secondary" variant="outlined" />
          <Chip label="Virtual Scrolling" color="secondary" variant="outlined" />
          <Chip label="Keyboard Navigation" color="secondary" variant="outlined" />
          <Chip label="Real-time Sync" color="secondary" variant="outlined" />
        </Box>

        {selectedFiles.length > 0 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Selected {selectedFiles.length} item(s): {selectedFiles.map(f => f.name).join(', ')}
          </Alert>
        )}
      </Box>

      <Grid container spacing={3}>
        {/* File Explorer */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2}>
            <FileExplorer
              rootPath="/"
              height={isMobile ? 400 : 600}
              showSearch={true}
              showContextMenu={true}
              enableDragDrop={true}
              enableKeyboardNavigation={true}
              enableVirtualization={true}
              multiSelect={true}
              onFileSelect={handleFileSelect}
              onFileOpen={handleFileOpen}
              onFileOperation={handleFileOperation}
              onError={handleError}
            />
          </Paper>
        </Grid>

        {/* Side Panel */}
        <Grid item xs={12} md={4}>
          <Box display="flex" flexDirection="column" gap={2}>
            {/* File Details */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <InfoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  File Details
                </Typography>
                
                {fileDetails.node ? (
                  <>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      {fileDetails.node.type === 'directory' ? 
                        <FolderIcon color="primary" /> : 
                        <FileIcon color="action" />
                      }
                      <Typography variant="subtitle1" component="div">
                        {fileDetails.node.name}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {fileDetails.node.path}
                    </Typography>
                    
                    <List dense>
                      {formatFileInfo(fileDetails.node).map((info, index) => (
                        <ListItem key={index} disableGutters>
                          <ListItemText 
                            primary={info}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {fileDetails.node.type === 'file' && (
                      <Box mt={2} display="flex" gap={1}>
                        <Tooltip title="Preview file">
                          <IconButton 
                            size="small" 
                            onClick={() => setPreviewDialog({ open: true, node: fileDetails.node })}
                          >
                            <PreviewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Open in editor">
                          <IconButton size="small">
                            <CodeIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download">
                          <IconButton size="small">
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Share">
                          <IconButton size="small">
                            <ShareIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    )}
                  </>
                ) : (
                  <Typography color="text.secondary">
                    Select a file or folder to view details
                  </Typography>
                )}
              </CardContent>
            </Card>

            {/* Recent Operations */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Operations
                </Typography>
                
                {fileDetails.operation ? (
                  <Box>
                    <Typography variant="body2" gutterBottom>
                      <strong>{fileDetails.operation.type.toUpperCase()}</strong>
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {fileDetails.operation.timestamp.toLocaleTimeString()}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {fileDetails.operation.source.join(', ')}
                      {fileDetails.operation.target && ` → ${fileDetails.operation.target}`}
                      {fileDetails.operation.newName && ` → ${fileDetails.operation.newName}`}
                    </Typography>
                  </Box>
                ) : (
                  <Typography color="text.secondary">
                    No recent operations
                  </Typography>
                )}
              </CardContent>
            </Card>

            {/* Keyboard Shortcuts */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Keyboard Shortcuts
                </Typography>
                
                <List dense>
                  {[
                    { key: 'Ctrl+N', action: 'New File' },
                    { key: 'Ctrl+Shift+N', action: 'New Folder' },
                    { key: 'F2', action: 'Rename' },
                    { key: 'Delete', action: 'Delete' },
                    { key: 'Ctrl+C', action: 'Copy' },
                    { key: 'Ctrl+X', action: 'Cut' },
                    { key: 'Ctrl+V', action: 'Paste' },
                    { key: 'F5', action: 'Refresh' },
                    { key: 'Ctrl+F', action: 'Search' },
                    { key: 'Ctrl+H', action: 'Toggle Hidden' }
                  ].map((shortcut) => (
                    <ListItem key={shortcut.key} disableGutters>
                      <ListItemText
                        primary={
                          <Box display="flex" justifyContent="space-between">
                            <Typography variant="body2">
                              {shortcut.action}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {shortcut.key}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>

      {/* File Preview Dialog */}
      <Dialog
        open={previewDialog.open}
        onClose={() => setPreviewDialog({ open: false, node: null })}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { height: '80vh' } }}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <FileIcon />
            {previewDialog.node?.name}
            <Chip 
              label={previewDialog.node?.extension?.toUpperCase() || 'FILE'} 
              size="small" 
              variant="outlined" 
            />
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box
            component="pre"
            sx={{
              backgroundColor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100',
              p: 2,
              borderRadius: 1,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              lineHeight: 1.5,
              height: '100%'
            }}
          >
            {getPreviewContent(previewDialog.node!)}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog({ open: false, node: null })}>
            Close
          </Button>
          <Button variant="contained" startIcon={<LaunchIcon />}>
            Open in Editor
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};