import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import FolderOpenIcon from "@mui/icons-material/FolderOpen";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import axios from "axios";

const API_URL = "http://localhost:8765/api";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

interface Task {
  task_id: string;
  status: string;
  progress: number;
  message: string;
}

function App() {
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [apiConnected, setApiConnected] = useState(false);
  const [scanResults, setScanResults] = useState<any>(null);

  // Check API connection
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await axios.get(`${API_URL}/`);
        setApiConnected(response.status === 200);
      } catch (error) {
        setApiConnected(false);
      }
    };

    checkApi();
    const interval = setInterval(checkApi, 5000);
    return () => clearInterval(interval);
  }, []);

  // Poll task status
  useEffect(() => {
    if (
      !currentTask ||
      currentTask.status === "completed" ||
      currentTask.status === "failed"
    ) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(
          `${API_URL}/task/${currentTask.task_id}`
        );
        const task = response.data;
        setCurrentTask(task);

        if (task.status === "completed") {
          setIsScanning(false);
          // Get scan results
          const resultsResponse = await axios.get(
            `${API_URL}/scan/${task.task_id}/results`
          );
          setScanResults(resultsResponse.data);
        } else if (task.status === "failed") {
          setIsScanning(false);
        }
      } catch (error) {
        console.error("Error polling task:", error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [currentTask]);

  const handleSelectFolder = async () => {
    const folder = await (window as any).electron.selectFolder();
    if (folder) {
      setSelectedFolder(folder);
      setScanResults(null);
    }
  };

  const handleStartScan = async () => {
    if (!selectedFolder) return;

    setIsScanning(true);
    try {
      const response = await axios.post(`${API_URL}/scan`, {
        path: selectedFolder,
        max_files: 1000,
      });

      setCurrentTask({
        task_id: response.data.task_id,
        status: "pending",
        progress: 0,
        message: "Starting scan...",
      });
    } catch (error) {
      console.error("Error starting scan:", error);
      setIsScanning(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          File Organizer
        </Typography>

        {!apiConnected && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Python API is not running. Please start it with: python api.py
          </Alert>
        )}

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Select a folder to organize
          </Typography>

          <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<FolderOpenIcon />}
              onClick={handleSelectFolder}
              disabled={isScanning}
            >
              Choose Folder
            </Button>

            {selectedFolder && (
              <Typography variant="body2" color="text.secondary">
                {selectedFolder}
              </Typography>
            )}
          </Box>

          <Button
            variant="contained"
            color="success"
            startIcon={<PlayArrowIcon />}
            onClick={handleStartScan}
            disabled={!selectedFolder || !apiConnected || isScanning}
            fullWidth
          >
            Start Scan
          </Button>
        </Paper>

        {currentTask && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
            >
              <Typography variant="h6">Scanning Progress</Typography>
              <Chip
                label={currentTask.status}
                color={
                  currentTask.status === "completed" ? "success" : "primary"
                }
                size="small"
              />
            </Box>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              {currentTask.message}
            </Typography>

            <LinearProgress
              variant="determinate"
              value={currentTask.progress * 100}
              sx={{ mt: 2 }}
            />
          </Paper>
        )}

        {scanResults && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Scan Results
            </Typography>

            <List>
              <ListItem>
                <ListItemText
                  primary="Total Files"
                  secondary={scanResults.analysis?.total_files || 0}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Files Scanned"
                  secondary={scanResults.files?.length || 0}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Organized Folders Found"
                  secondary={
                    scanResults.analysis?.organized_folders?.length || 0
                  }
                />
              </ListItem>
            </List>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
