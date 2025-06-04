import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Collapse,
  alpha,
  useTheme,
  Grid,
  Divider,
} from "@mui/material";
import {
  AutoAwesome,
  PlayArrow,
  CheckCircle,
  Warning,
  Info,
  ExpandMore,
  ExpandLess,
  Folder,
  ArrowForward,
  Download,
  Preview,
  RestartAlt,
} from "@mui/icons-material";
import { api, TaskStatus } from "../services/api";
import FolderTreePreview from "../components/FolderTreePreview";

interface OrganizePlanMove {
  file: string;
  relative_path: string;
  new_path: string;
  reason: string;
}

interface OrganizePlan {
  folders: string[];
  moves: OrganizePlanMove[];
}

interface OrganizePageProps {
  apiConnected: boolean;
}

const OrganizePage: React.FC<OrganizePageProps> = ({ apiConnected }) => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [plan, setPlan] = useState<OrganizePlan | null>(null);
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string>("");
  const [expandedMoves, setExpandedMoves] = useState<Set<number>>(new Set());
  const [confirmDialog, setConfirmDialog] = useState(false);
  const [isDryRun, setIsDryRun] = useState(true);
  const [selectedFolder, setSelectedFolder] = useState<string>("");

  const steps = ["Generate Plan", "Review Plan", "Execute Organizatxion"];

  useEffect(() => {
    const savedState = localStorage.getItem("organizePageState");
    if (savedState) {
      const state = JSON.parse(savedState);
      if (state.activeStep !== undefined) setActiveStep(state.activeStep);
      if (state.plan) setPlan(state.plan);
      if (state.selectedFolder) setSelectedFolder(state.selectedFolder);
    }
  }, []);

  // Save state whenever it changes
  useEffect(() => {
    const state = {
      activeStep,
      plan,
      selectedFolder,
    };
    localStorage.setItem("organizePageState", JSON.stringify(state));
  }, [activeStep, plan, selectedFolder]);

  useEffect(() => {
    // Load saved folder
    const savedFolder = localStorage.getItem("selectedFolder");
    if (savedFolder) {
      setSelectedFolder(savedFolder);
    }

    // Check if we have scan results
    checkScanResults();
  }, []);

  const checkScanResults = async () => {
    try {
      const scanResults = localStorage.getItem("scanResults");
      if (!scanResults) {
        setError("No scan results found. Please scan a folder first.");
        return;
      }

      // Check if we have a saved plan
      const savedPlan = localStorage.getItem("organizationPlan");
      if (savedPlan) {
        setPlan(JSON.parse(savedPlan));
        setActiveStep(1);
      }
    } catch (error) {
      console.error("Error checking scan results:", error);
    }
  };

  const handleGeneratePlan = async () => {
    if (!selectedFolder) {
      setError("Please select a folder first");
      return;
    }

    setError("");
    try {
      const response = await api.generatePrompt(selectedFolder);
      setCurrentTask({
        task_id: response.task_id,
        status: "pending",
        progress: 0,
        message: "Generating organization plan...",
      });

      pollTaskStatus(response.task_id, "prompt");
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to generate plan");
    }
  };

  const pollTaskStatus = async (
    taskId: string,
    type: "prompt" | "organize"
  ) => {
    const interval = setInterval(async () => {
      try {
        const status = await api.getTaskStatus(taskId);
        setCurrentTask(status);

        if (status.status === "completed") {
          clearInterval(interval);

          if (type === "prompt") {
            // Load the generated plan from file
            try {
              // In a real implementation, you'd get this from the API
              // For now, we'll show a message to copy the plan
              loadPlanFromFile();
              setActiveStep(1);
              //   Alert(
              //     "Please copy the generated prompt from data/gpt_prompt.txt to ChatGPT/Claude and save the response to data/plan.json"
              //   );
            } catch (error) {
              setError("Failed to load generated plan");
            }
          } else {
            // Organization complete
            setActiveStep(2);

            // Update stats
            const stats = JSON.parse(
              localStorage.getItem("organizerStats") || "{}"
            );
            stats.filesOrganized =
              (stats.filesOrganized || 0) + (plan?.moves.length || 0);
            stats.foldersCreated =
              (stats.foldersCreated || 0) + (plan?.folders.length || 0);
            localStorage.setItem("organizerStats", JSON.stringify(stats));
          }
        } else if (status.status === "failed") {
          clearInterval(interval);
          setError(status.error || `${type} failed`);
        }
      } catch (error) {
        clearInterval(interval);
        setError(`Failed to get ${type} status`);
      }
    }, 1000);
  };

  const loadPlanFromFile = async () => {
    try {
      const planData = await api.loadPlan();
      setPlan(planData);
      localStorage.setItem("organizationPlan", JSON.stringify(planData));
      setActiveStep(1);
    } catch (error) {
      setError(
        "Failed to load plan. Please ensure plan.json exists in the backend/data folder."
      );
    }
  };

  const handleExecutePlan = async () => {
    if (!plan || !selectedFolder) return;

    setConfirmDialog(false);
    setError("");

    try {
      const response = await api.executeOrganization(selectedFolder, isDryRun);
      setCurrentTask({
        task_id: response.task_id,
        status: "pending",
        progress: 0,
        message: isDryRun ? "Running simulation..." : "Organizing files...",
      });

      pollTaskStatus(response.task_id, "organize");
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to execute plan");
    }
  };

  const toggleMoveExpanded = (index: number) => {
    const newExpanded = new Set(expandedMoves);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedMoves(newExpanded);
  };

  const downloadPlan = () => {
    if (!plan) return;

    const dataStr = JSON.stringify(plan, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = "organization_plan.json";

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight={600}>
          Organize Files
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review and execute the AI-generated organization plan
        </Typography>
      </Box>

      {!apiConnected && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Backend API is not connected. Please start the Python backend.
        </Alert>
      )}

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Step Content */}
      {activeStep === 0 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Generate Organization Plan
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            AI will analyze your scan results and create an intelligent
            organization plan
          </Typography>

          {selectedFolder ? (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                Folder: {selectedFolder}
              </Alert>
              <Button
                variant="contained"
                size="large"
                startIcon={<AutoAwesome />}
                onClick={handleGeneratePlan}
                disabled={!apiConnected || !!currentTask}
                fullWidth
                sx={{
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                }}
              >
                Generate Plan with AI
              </Button>
            </Box>
          ) : (
            <Alert severity="warning">
              Please scan a folder first before generating an organization plan
            </Alert>
          )}
        </Paper>
      )}

      {activeStep === 1 && plan && (
        <>
          {/* Plan Overview */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    New Folders
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {plan.folders.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    folders will be created
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    File Moves
                  </Typography>
                  <Typography variant="h3" color="secondary">
                    {plan.moves.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    files will be organized
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Folders to Create */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Folders to Create
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={1}>
              {plan.folders.map((folder, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Chip
                    icon={<Folder />}
                    label={folder}
                    sx={{ width: "100%", justifyContent: "flex-start" }}
                  />
                </Grid>
              ))}
            </Grid>
          </Paper>

          {/* File Moves */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Planned File Moves
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <List>
              {plan.moves.slice(0, 10).map((move, index) => (
                <React.Fragment key={index}>
                  <ListItem
                    onClick={() => toggleMoveExpanded(index)}
                    sx={{
                      cursor: "pointer",
                      "&:hover": { bgcolor: "action.hover" },
                    }}
                  >
                    <ListItemIcon>
                      <ArrowForward color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={move.file}
                      secondary={`To: ${move.new_path}`}
                    />
                    <IconButton size="small">
                      {expandedMoves.has(index) ? (
                        <ExpandLess />
                      ) : (
                        <ExpandMore />
                      )}
                    </IconButton>
                  </ListItem>
                  <Collapse in={expandedMoves.has(index)}>
                    <Box sx={{ pl: 9, pr: 3, pb: 2 }}>
                      <Alert severity="info" icon={<Info />}>
                        {move.reason}
                      </Alert>
                    </Box>
                  </Collapse>
                  {index < plan.moves.length - 1 && <Divider variant="inset" />}
                </React.Fragment>
              ))}
            </List>
            {plan.moves.length > 10 && (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                ... and {plan.moves.length - 10} more files
              </Typography>
            )}
          </Paper>

          {/* Action Buttons */}
          <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<Preview />}
              onClick={() => {
                setIsDryRun(true);
                setConfirmDialog(true);
              }}
            >
              Preview (Dry Run)
            </Button>
            <Button
              variant="contained"
              size="large"
              color="success"
              startIcon={<PlayArrow />}
              onClick={() => {
                setIsDryRun(false);
                setConfirmDialog(true);
              }}
            >
              Execute Plan
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<Download />}
              onClick={downloadPlan}
            >
              Download Plan
            </Button>
          </Box>
        </>
      )}

      {activeStep === 2 && !isDryRun && (
        <Paper sx={{ p: 4, textAlign: "center" }}>
          <CheckCircle sx={{ fontSize: 80, color: "success.main", mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Organization Complete!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Your files have been successfully organized according to the
            AI-generated plan.
          </Typography>
          <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<RestartAlt />}
              onClick={() => {
                setActiveStep(0);
                setPlan(null);
                setCurrentTask(null);
                setError("");
              }}
            >
              Organize Another Folder
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => (window.location.href = "/")}
            >
              Back to Home
            </Button>
          </Box>
        </Paper>
      )}

      {/* Loading / Progress Display */}
      {currentTask && currentTask.status === "pending" && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="body1" gutterBottom>
            {currentTask.message}
          </Typography>
          <LinearProgress />
        </Paper>
      )}

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog}
        onClose={() => setConfirmDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirm {isDryRun ? "Dry Run" : "Execution"}</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to{" "}
            {isDryRun
              ? "preview the plan without moving files"
              : "execute the full file reorganization"}
            ?
          </Typography>
          {!isDryRun && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This will move files on your system. Please make sure you're ready
              before proceeding.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>Cancel</Button>
          <Button
            onClick={handleExecutePlan}
            variant="contained"
            color={isDryRun ? "info" : "success"}
          >
            {isDryRun ? "Run Dry Preview" : "Execute"}
          </Button>
        </DialogActions>
      </Dialog>

      {activeStep === 2 && isDryRun && plan && (
        <Paper sx={{ p: 4, mt: 4 }}>
          <Typography variant="h4" gutterBottom>
            Dry Run Preview
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            This is a preview — no files have been moved yet.
          </Alert>
          <FolderTreePreview folders={plan.folders} moves={plan.moves} />
          <Box
            sx={{ mt: 3, display: "flex", gap: 2, justifyContent: "center" }}
          >
            <Button
              variant="contained"
              color="success"
              startIcon={<PlayArrow />}
              onClick={() => {
                setIsDryRun(false);
                setConfirmDialog(true);
              }}
            >
              Execute for Real
            </Button>
            <Button variant="outlined" onClick={() => setActiveStep(1)}>
              Back to Plan
            </Button>
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default OrganizePage;
