import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  IconButton,
  Collapse,
  Paper,
  Chip,
  alpha,
  useTheme,
} from "@mui/material";
import {
  Folder,
  FolderOpen,
  InsertDriveFile,
  ExpandMore,
  ExpandLess,
  ArrowForward,
} from "@mui/icons-material";

interface FileMove {
  file: string;
  relative_path: string;
  new_path: string;
  reason: string;
}

interface FolderTreeProps {
  folders: string[];
  moves: FileMove[];
}

interface TreeNode {
  name: string;
  path: string;
  isFolder: boolean;
  children: TreeNode[];
  originalPath?: string;
  isNew?: boolean;
}

const FolderTreePreview: React.FC<FolderTreeProps> = ({ folders, moves }) => {
  const theme = useTheme();
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  useEffect(() => {
    setExpanded(new Set([""]));
  }, []);

  // Build tree structure
  const buildTree = (): TreeNode => {
    const root: TreeNode = {
      name: "Proposed Organization",
      path: "",
      isFolder: true,
      children: [],
    };

    // Add folders
    folders.forEach((folderPath) => {
      const parts = folderPath.split("/");
      let current = root;

      parts.forEach((part, index) => {
        const currentPath = parts.slice(0, index + 1).join("/");
        let child = current.children.find((c) => c.name === part);

        if (!child) {
          child = {
            name: part,
            path: currentPath,
            isFolder: true,
            children: [],
            isNew: true,
          };
          current.children.push(child);
        }
        current = child;
      });
    });

    // Add files
    moves.forEach((move) => {
      const parts = move.new_path.split("/");
      const fileName = parts.pop()!;
      let current = root;

      // Navigate to parent folder
      parts.forEach((part, index) => {
        let child = current.children.find((c) => c.name === part);
        if (!child) {
          child = {
            name: part,
            path: parts.slice(0, index + 1).join("/"),
            isFolder: true,
            children: [],
          };
          current.children.push(child);
        }
        current = child;
      });

      // Add file
      current.children.push({
        name: fileName,
        path: move.new_path,
        isFolder: false,
        children: [],
        originalPath: move.relative_path,
      });
    });

    // Sort folders first, then files
    const sortTree = (node: TreeNode) => {
      node.children.sort((a, b) => {
        if (a.isFolder && !b.isFolder) return -1;
        if (!a.isFolder && b.isFolder) return 1;
        return a.name.localeCompare(b.name);
      });
      node.children.forEach(sortTree);
    };

    sortTree(root);

    // Auto-expand root

    return root;
  };

  const tree = buildTree();

  const toggleExpanded = (path: string) => {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpanded(newExpanded);
  };

  const renderTree = (node: TreeNode, level: number = 0) => {
    const isExpanded = expanded.has(node.path);

    return (
      <Box key={node.path}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            pl: level * 3,
            py: 0.5,
            "&:hover": {
              bgcolor: alpha(theme.palette.primary.main, 0.05),
            },
          }}
        >
          {node.isFolder ? (
            <>
              <IconButton
                size="small"
                onClick={() => toggleExpanded(node.path)}
                sx={{ p: 0.5 }}
              >
                {isExpanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
              {isExpanded ? (
                <FolderOpen sx={{ mr: 1, color: theme.palette.primary.main }} />
              ) : (
                <Folder sx={{ mr: 1, color: theme.palette.primary.main }} />
              )}
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 600,
                  flex: 1,
                }}
              >
                {node.name}
              </Typography>
              {node.isNew && (
                <Chip
                  label="NEW"
                  size="small"
                  color="success"
                  sx={{ ml: 1, height: 20 }}
                />
              )}
            </>
          ) : (
            <>
              <Box sx={{ width: 32 }} />
              <InsertDriveFile
                sx={{ mr: 1, color: theme.palette.text.secondary }}
              />
              <Typography variant="body2" sx={{ flex: 1 }}>
                {node.name}
              </Typography>
              {node.originalPath && (
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Typography
                    variant="caption"
                    sx={{
                      color: theme.palette.text.secondary,
                      mx: 1,
                      fontFamily: "monospace",
                      fontSize: "0.7rem",
                    }}
                  >
                    from: {node.originalPath}
                  </Typography>
                  <ArrowForward
                    sx={{ fontSize: 14, color: theme.palette.success.main }}
                  />
                </Box>
              )}
            </>
          )}
        </Box>

        {node.isFolder && isExpanded && (
          <Collapse in={isExpanded}>
            {node.children.map((child) => renderTree(child, level + 1))}
          </Collapse>
        )}
      </Box>
    );
  };

  return (
    <Paper
      sx={{
        p: 2,
        maxHeight: 600,
        overflow: "auto",
        bgcolor: alpha(theme.palette.background.paper, 0.5),
      }}
    >
      <Typography variant="h6" gutterBottom>
        Preview of New Folder Structure
      </Typography>
      {renderTree(tree)}
    </Paper>
  );
};

export default FolderTreePreview;
