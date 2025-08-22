import React, { useMemo, useCallback, useRef, useEffect } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { Box, Typography } from '@mui/material';
import { FileSystemNode, VirtualizedTreeProps } from '../../types';
import { TreeNode } from './TreeNode';
import { sortNodes, filterNodes, isHiddenNode } from '../../utils/fileExplorerUtils';

interface FlatTreeNode {
  node: FileSystemNode;
  level: number;
  isVisible: boolean;
  hasChildren: boolean;
  children?: FlatTreeNode[];
}

interface VirtualizedTreeComponentProps extends VirtualizedTreeProps {
  nodes: Record<string, FileSystemNode>;
  rootNodeIds: string[];
  expandedNodes: Set<string>;
  selectedNodes: string[];
  searchQuery: string;
  searchResults: string[];
  sortBy: 'name' | 'size' | 'modified' | 'type';
  sortOrder: 'asc' | 'desc';
  showHidden: boolean;
  enableDragDrop?: boolean;
  enableContextMenu?: boolean;
  onNodeSelect: (nodeId: string, multiSelect?: boolean) => void;
  onNodeExpand: (nodeId: string) => void;
  onNodeCollapse: (nodeId: string) => void;
  onNodeRename?: (nodeId: string, newName: string) => Promise<void>;
  onNodeCreate?: (parentId: string, name: string, type: 'file' | 'directory') => Promise<void>;
  onNodeDelete?: (nodeIds: string[]) => Promise<void>;
  onNodeCopy?: (nodeIds: string[]) => void;
  onNodeCut?: (nodeIds: string[]) => void;
  onNodePaste?: (targetId: string) => Promise<void>;
  onNodeRefresh?: (nodeId: string) => Promise<void>;
}

interface TreeItemProps {
  index: number;
  style: React.CSSProperties;
  data: {
    flatNodes: FlatTreeNode[];
    selectedNodes: string[];
    expandedNodes: Set<string>;
    enableDragDrop: boolean;
    enableContextMenu: boolean;
    onNodeSelect: (nodeId: string, multiSelect?: boolean) => void;
    onNodeExpand: (nodeId: string) => void;
    onNodeCollapse: (nodeId: string) => void;
    onNodeRename?: (nodeId: string, newName: string) => Promise<void>;
    onNodeCreate?: (parentId: string, name: string, type: 'file' | 'directory') => Promise<void>;
    onNodeDelete?: (nodeIds: string[]) => Promise<void>;
    onNodeCopy?: (nodeIds: string[]) => void;
    onNodeCut?: (nodeIds: string[]) => void;
    onNodePaste?: (targetId: string) => Promise<void>;
    onNodeRefresh?: (nodeId: string) => Promise<void>;
  };
}

const TreeItem: React.FC<TreeItemProps> = ({ index, style, data }) => {
  const {
    flatNodes,
    selectedNodes,
    expandedNodes,
    enableDragDrop,
    enableContextMenu,
    onNodeSelect,
    onNodeExpand,
    onNodeCollapse,
    onNodeRename,
    onNodeCreate,
    onNodeDelete,
    onNodeCopy,
    onNodeCut,
    onNodePaste,
    onNodeRefresh
  } = data;

  const flatNode = flatNodes[index];
  if (!flatNode) {
    return <div style={style} />;
  }

  const { node, level } = flatNode;
  const isSelected = selectedNodes.includes(node.id);
  const isExpanded = expandedNodes.has(node.id);

  return (
    <div style={style}>
      <TreeNode
        node={node}
        level={level}
        isSelected={isSelected}
        isExpanded={isExpanded}
        onSelect={onNodeSelect}
        onExpand={onNodeExpand}
        onCollapse={onNodeCollapse}
        onRename={onNodeRename}
        onCreate={onNodeCreate}
        onDelete={onNodeDelete}
        onCopy={onNodeCopy}
        onCut={onNodeCut}
        onPaste={onNodePaste}
        onRefresh={onNodeRefresh}
        enableDragDrop={enableDragDrop}
        enableContextMenu={enableContextMenu}
      />
    </div>
  );
};

export const VirtualizedTree: React.FC<VirtualizedTreeComponentProps> = ({
  height,
  width,
  itemHeight,
  overscan = 5,
  nodes,
  rootNodeIds,
  expandedNodes,
  selectedNodes,
  searchQuery,
  searchResults,
  sortBy,
  sortOrder,
  showHidden,
  enableDragDrop = true,
  enableContextMenu = true,
  onNodeSelect,
  onNodeExpand,
  onNodeCollapse,
  onNodeRename,
  onNodeCreate,
  onNodeDelete,
  onNodeCopy,
  onNodeCut,
  onNodePaste,
  onNodeRefresh
}) => {
  const listRef = useRef<List>(null);

  // Build flat tree structure for virtualization
  const flatNodes = useMemo(() => {
    const buildFlatTree = (nodeIds: string[], level = 0): FlatTreeNode[] => {
      const result: FlatTreeNode[] = [];

      // Get and sort nodes
      const nodeList = nodeIds
        .map(id => nodes[id])
        .filter(Boolean);

      const sortedNodes = sortNodes(nodeList, sortBy, sortOrder);
      
      // Filter based on search and visibility settings
      const filteredNodes = searchQuery 
        ? sortedNodes.filter(node => searchResults.includes(node.id))
        : sortedNodes.filter(node => showHidden || !isHiddenNode(node));

      for (const node of filteredNodes) {
        const flatNode: FlatTreeNode = {
          node,
          level,
          isVisible: true,
          hasChildren: node.type === 'directory' && (node.children?.length || 0) > 0
        };

        result.push(flatNode);

        // Add children if expanded
        if (node.type === 'directory' && expandedNodes.has(node.id) && node.children) {
          const childFlatNodes = buildFlatTree(node.children, level + 1);
          result.push(...childFlatNodes);
        }
      }

      return result;
    };

    return buildFlatTree(rootNodeIds);
  }, [
    nodes,
    rootNodeIds,
    expandedNodes,
    searchQuery,
    searchResults,
    sortBy,
    sortOrder,
    showHidden
  ]);

  // Scroll to selected node
  useEffect(() => {
    if (selectedNodes.length > 0 && listRef.current) {
      const selectedNodeId = selectedNodes[0];
      const index = flatNodes.findIndex(flatNode => flatNode.node.id === selectedNodeId);
      if (index >= 0) {
        listRef.current.scrollToItem(index, 'smart');
      }
    }
  }, [selectedNodes, flatNodes]);

  const itemData = useMemo(() => ({
    flatNodes,
    selectedNodes,
    expandedNodes,
    enableDragDrop,
    enableContextMenu,
    onNodeSelect,
    onNodeExpand,
    onNodeCollapse,
    onNodeRename,
    onNodeCreate,
    onNodeDelete,
    onNodeCopy,
    onNodeCut,
    onNodePaste,
    onNodeRefresh
  }), [
    flatNodes,
    selectedNodes,
    expandedNodes,
    enableDragDrop,
    enableContextMenu,
    onNodeSelect,
    onNodeExpand,
    onNodeCollapse,
    onNodeRename,
    onNodeCreate,
    onNodeDelete,
    onNodeCopy,
    onNodeCut,
    onNodePaste,
    onNodeRefresh
  ]);

  if (flatNodes.length === 0) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height={height}
        width={width}
      >
        <Typography color="text.secondary">
          {searchQuery ? 'No search results found' : 'No files or folders to display'}
        </Typography>
      </Box>
    );
  }

  return (
    <List
      ref={listRef}
      height={height}
      width={width}
      itemCount={flatNodes.length}
      itemSize={itemHeight}
      itemData={itemData}
      overscanCount={overscan}
    >
      {TreeItem}
    </List>
  );
};

// Wrapper component with AutoSizer
export const AutoSizedVirtualizedTree: React.FC<
  Omit<VirtualizedTreeComponentProps, 'height' | 'width'>
> = (props) => {
  return (
    <AutoSizer>
      {({ height, width }) => (
        <VirtualizedTree
          {...props}
          height={height}
          width={width}
        />
      )}
    </AutoSizer>
  );
};