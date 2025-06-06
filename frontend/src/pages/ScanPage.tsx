import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  alpha,
  useTheme,
  CircularProgress,
  Divider,
} from "@mui/material";
import {
  FolderOpen,
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
  Info,
  ExpandMore,
  ExpandLess,
  Description,
  Image,
  Code,
  Archive,
  MovieCreation,
  AudioFile,
  Refresh,
} from "@mui/icons-material";
import { api, TaskStatus } from "../services/api";
import { useAppState } from "../contexts/AppStateContext";

interface ScanPageProps {
  apiConnected: boolean;
}

interface FileTypeStats {
  [key: string]: number;
}

const ScanPage: React.FC<ScanPageProps> = ({ apiConnected }) => {
  const theme = useTheme();
  const [selectedFolder, setSelectedFolder] = useState<string>("");
  const [isScanning, setIsScanning] = useState(false);
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);
  const [scanResults, setScanResults] = useState<any>(null);
  const [error, setError] = useState<string>("");
  const [expandedSections, setExpandedSections] = useState({
    fileTypes: true,
    recentFiles: false,
    organizedFolders: false,
  });

  useEffect(() => {
    // Load last selected folder
    const savedFolder = localStorage.getItem("selectedFolder");
    if (savedFolder) {
      setSelectedFolder(savedFolder);
    }

    // Check for in-progress scan
    const savedTaskId = localStorage.getItem("currentScanTask");
    if (savedTaskId) {
      checkTaskStatus(savedTaskId);
    }
  }, []);

  const checkTaskStatus = async (taskId: string) => {
    try {
      const status = await api.getTaskStatus(taskId);
      setCurrentTask(status);

      if (status.status === "running" || status.status === "pending") {
        setIsScanning(true);
        pollTaskStatus(taskId);
      } else if (status.status === "completed") {
        const results = await api.getScanResults(taskId);
        setScanResults(results);
        localStorage.removeItem("currentScanTask");
      }
    } catch (error) {
      console.error("Error checking task status:", error);
      localStorage.removeItem("currentScanTask");
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await api.getTaskStatus(taskId);
        setCurrentTask(status);

        if (status.status === "completed") {
          clearInterval(interval);
          setIsScanning(false);
          const results = await api.getScanResults(taskId);
          setScanResults(results);
          localStorage.removeItem("currentScanTask");

          // Update stats
          const stats = JSON.parse(
            localStorage.getItem("organizerStats") || "{}"
          );
          stats.lastScan = new Date().toLocaleDateString();
          localStorage.setItem("organizerStats", JSON.stringify(stats));
        } else if (status.status === "failed") {
          clearInterval(interval);
          setIsScanning(false);
          setError(status.error || "Scan failed");
          localStorage.removeItem("currentScanTask");
        }
      } catch (error) {
        clearInterval(interval);
        setIsScanning(false);
        setError("Failed to get scan status");
        localStorage.removeItem("currentScanTask");
      }
    }, 1000);
  };

  const handleSelectFolder = async () => {
    const folder = await (window as any).electron.selectFolder();
    if (folder) {
      setSelectedFolder(folder);
      localStorage.setItem("selectedFolder", folder);
      setError("");
      setScanResults(null);
    }
  };

  const handleStartScan = async () => {
    if (!selectedFolder) return;

    setIsScanning(true);
    setError("");
    setScanResults(null);

    try {
      const response = await api.startScan(selectedFolder);
      localStorage.setItem("currentScanTask", response.task_id);
      setCurrentTask({
        task_id: response.task_id,
        status: "pending",
        progress: 0,
        message: "Starting scan...",
      });
      pollTaskStatus(response.task_id);
    } catch (error: any) {
      setIsScanning(false);
      setError(error.response?.data?.detail || "Failed to start scan");
    }
  };

  const handleStopScan = () => {
    // In a real implementation, you'd call an API to cancel the task
    setIsScanning(false);
    localStorage.removeItem("currentScanTask");
  };

  const getFileIcon = (extension: string) => {
    if ([".jpg", ".png", ".gif", ".svg", ".hiec"].includes(extension))
      return <Image />;
    if ([".mp4", ".avi", ".mov", ".mkv"].includes(extension))
      return <MovieCreation />;
    if ([".mp3", ".wav", ".flac"].includes(extension)) return <AudioFile />;
    if ([".zip", ".rar", ".7z"].includes(extension)) return <Archive />;
    if ([".py", ".js", ".html", ".css"].includes(extension)) return <Code />;
    return <Description />;
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight={600}>
          Scan Files
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analyze your folder structure and identify files that need
          organization
        </Typography>
      </Box>

      {!apiConnected && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Backend API is not connected. Please start the Python backend.
        </Alert>
      )}

      {/* Folder Selection */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Select Folder
        </Typography>

        <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<FolderOpen />}
            onClick={handleSelectFolder}
            disabled={isScanning}
          >
            Choose Folder
          </Button>

          {selectedFolder && (
            <Typography
              variant="body2"
              sx={{
                flex: 1,
                p: 2,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                borderRadius: 2,
                fontFamily: "monospace",
              }}
            >
              {selectedFolder}
            </Typography>
          )}
        </Box>

        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={isScanning ? <Stop /> : <PlayArrow />}
            onClick={isScanning ? handleStopScan : handleStartScan}
            disabled={!selectedFolder || !apiConnected}
            fullWidth
            sx={{
              background: isScanning
                ? theme.palette.error.main
                : `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
            }}
          >
            {isScanning ? "Stop Scan" : "Start Scan"}
          </Button>
        </Box>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Scan Progress */}
      {currentTask && isScanning && (
        <Paper sx={{ p: 4, mb: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography variant="h6" sx={{ flex: 1 }}>
              Scanning in Progress
            </Typography>
            <Chip label={currentTask.status} color="primary" size="small" />
          </Box>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            {currentTask.message}
          </Typography>

          <LinearProgress
            variant="determinate"
            value={currentTask.progress * 100}
            sx={{ mt: 2, height: 8, borderRadius: 4 }}
          />

          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            {Math.round(currentTask.progress * 100)}% complete
          </Typography>
        </Paper>
      )}

      {/* Scan Results */}
      {scanResults && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Files
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {scanResults.analysis?.total_files || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Files Scanned
                  </Typography>
                  <Typography variant="h4" color="secondary">
                    {scanResults.files?.length || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    File Types
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {Object.keys(scanResults.analysis?.file_types || {}).length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Organized Folders
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {scanResults.analysis?.organized_folders?.length || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* File Types Breakdown */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
              }}
              onClick={() => toggleSection("fileTypes")}
            >
              <Typography variant="h6">File Types Distribution</Typography>
              <IconButton>
                {expandedSections.fileTypes ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>

            <Collapse in={expandedSections.fileTypes}>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                {Object.entries(scanResults.analysis?.file_types || {})
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .slice(0, 12)
                  .map(([ext, count]) => (
                    <Grid item xs={6} sm={4} md={3} key={ext}>
                      <Box
                        sx={{
                          p: 2,
                          borderRadius: 2,
                          bgcolor: alpha(theme.palette.primary.main, 0.1),
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                        }}
                      >
                        {getFileIcon(ext)}
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="subtitle2">
                            {ext || "No extension"}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {count} files
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                  ))}
              </Grid>
            </Collapse>
          </Paper>

          {/* Action Buttons */}
          <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => (window.location.href = "/organize")}
              sx={{
                background: `linear-gradient(135deg, ${theme.palette.success.main} 0%, ${theme.palette.success.dark} 100%)`,
              }}
            >
              Generate Organization Plan
            </Button>

            <Button
              variant="outlined"
              size="large"
              startIcon={<Refresh />}
              onClick={handleStartScan}
            >
              Rescan Folder
            </Button>
          </Box>
        </>
      )}
    </Container>
  );
};

export default ScanPage;
