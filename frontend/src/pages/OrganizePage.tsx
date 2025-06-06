import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef,
} from "react";
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
import { api } from "../services/api";
import FolderTreePreview from "../components/FolderTreePreview";
import { useAppState } from "../contexts/AppStateContext";

// Type definitions
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

// Constants
const STEPS = ["Generate Plan", "Review Plan", "Execute Organization"];
const POLL_INTERVAL = 1000;
const TASK_CLEAR_DELAY = 2000;
const MAX_VISIBLE_MOVES = 10;

const OrganizePage: React.FC<OrganizePageProps> = ({ apiConnected }) => {
  const theme = useTheme();
  const { state, updateState } = useAppState();

  // State with proper defaults
  const {
    selectedFolder = "",
    activeStep = 0,
    organizationPlan: plan = null,
    currentTask = null,
    organizeError: error = "",
    isDryRun = true,
    scanResults = null,
    isOrganizationComplete = false,
  } = state;

  const [expandedMoves, setExpandedMoves] = useState<Set<number>>(new Set());
  const [confirmDialog, setConfirmDialog] = useState(false);

  // Use refs to avoid stale closures
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Memoized values
  const hasValidScanResults = useMemo(() => {
    return !!(scanResults || localStorage.getItem("scanResults"));
  }, [scanResults]);

  // Check for stuck tasks on mount
  useEffect(() => {
    // If there's a currentTask but it's not for organization, clear it
    if (currentTask && !currentTask.task_id.includes("organize")) {
      console.log("Clearing stuck task from previous operation:", currentTask);
      updateState({ currentTask: null });
    }
  }, []);
  const canGeneratePlan = useMemo(() => {
    // Only block if there's an active organization task
    const hasActiveOrganizeTask =
      currentTask &&
      (currentTask.status === "pending" || currentTask.status === "running");

    const canGenerate =
      apiConnected &&
      !hasActiveOrganizeTask &&
      selectedFolder &&
      hasValidScanResults;

    console.log("canGeneratePlan check:", {
      apiConnected,
      currentTask,
      hasActiveOrganizeTask,
      selectedFolder,
      hasValidScanResults,
      canGenerate,
    });

    return canGenerate;
  }, [apiConnected, currentTask, selectedFolder, hasValidScanResults]);
  const canExecutePlan = useMemo(() => {
    return apiConnected && !currentTask && plan?.moves?.length > 0;
  }, [apiConnected, currentTask, plan]);

  // Initialize component
  useEffect(() => {
    const initializeComponent = async () => {
      // Check if this is a fresh page load
      const isFreshLoad = sessionStorage.getItem("freshLoad") !== "false";

      if (isFreshLoad) {
        // Reset to initial state for fresh load
        updateState({
          activeStep: 0,
          organizationPlan: null,
          currentTask: null,
          organizeError: "",
          isDryRun: true,
          isOrganizationComplete: false,
        });
        sessionStorage.setItem("freshLoad", "false");
      } else {
        // Restore state from storage
        await restoreStateFromStorage();
      }

      // Validate scan results
      await validateScanResults();
    };

    initializeComponent();

    // Cleanup interval on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Restore state from localStorage
  const restoreStateFromStorage = useCallback(async () => {
    try {
      // Restore selected folder
      if (!selectedFolder) {
        const savedFolder = localStorage.getItem("selectedFolder");
        if (savedFolder) {
          updateState({ selectedFolder: savedFolder });
        }
      }

      // Restore organization plan
      if (!plan) {
        const savedPlan = localStorage.getItem("organizationPlan");
        if (savedPlan) {
          const parsedPlan = JSON.parse(savedPlan);
          updateState({
            organizationPlan: parsedPlan,
            activeStep: parsedPlan?.moves?.length > 0 ? 1 : 0,
          });
        }
      }

      // Restore scan results
      if (!scanResults) {
        const savedScanResults = localStorage.getItem("scanResults");
        if (savedScanResults) {
          const parsedResults = JSON.parse(savedScanResults);
          updateState({ scanResults: parsedResults });
        }
      }
    } catch (error) {
      console.error("Error restoring state from storage:", error);
    }
  }, [selectedFolder, plan, scanResults, updateState]);

  // Validate scan results
  const validateScanResults = useCallback(async () => {
    try {
      const currentScanResults =
        scanResults ||
        JSON.parse(localStorage.getItem("scanResults") || "null");

      if (!currentScanResults) {
        updateState({
          organizeError: "No scan results found. Please scan a folder first.",
        });
        return false;
      }

      // Clear any previous error if we have valid scan results
      if (error) {
        updateState({ organizeError: "" });
      }

      return true;
    } catch (error) {
      console.error("Error validating scan results:", error);
      updateState({
        organizeError:
          "Error checking scan results. Please try scanning again.",
      });
      return false;
    }
  }, [scanResults, error, updateState]);

  // Load plan from file
  const loadPlanFromFile = useCallback(async () => {
    try {
      const planData = await api.loadPlan();
      updateState({
        organizationPlan: planData,
        activeStep: 1,
      });
      localStorage.setItem("organizationPlan", JSON.stringify(planData));
    } catch (error) {
      console.error("Error loading plan:", error);
      updateState({
        organizeError: "Failed to load plan. Please ensure plan.json exists.",
      });
    }
  }, [updateState]);

  // Update organization statistics
  const updateOrganizationStats = useCallback(() => {
    const stats = JSON.parse(localStorage.getItem("organizerStats") || "{}");
    stats.filesOrganized =
      (stats.filesOrganized || 0) + (plan?.moves?.length || 0);
    stats.foldersCreated =
      (stats.foldersCreated || 0) + (plan?.folders?.length || 0);
    localStorage.setItem("organizerStats", JSON.stringify(stats));
  }, [plan]);

  // Handle organization completion
  const handleOrganizationComplete = useCallback(() => {
    if (isDryRun) {
      updateState({
        activeStep: 2,
        isOrganizationComplete: false,
      });
    } else {
      updateState({
        activeStep: 2,
        isOrganizationComplete: true,
      });
      updateOrganizationStats();
    }
  }, [isDryRun, updateState, updateOrganizationStats]);

  // Poll task status
  const pollTaskStatus = useCallback(
    async (taskId: string, type: "prompt" | "organize") => {
      // Clear any existing interval
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      intervalRef.current = setInterval(async () => {
        try {
          const status = await api.getTaskStatus(taskId);
          updateState({ currentTask: status });

          if (status.status === "completed") {
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }

            // Clear task after delay
            setTimeout(() => {
              updateState({ currentTask: null });
            }, TASK_CLEAR_DELAY);

            if (type === "prompt") {
              await loadPlanFromFile();
            } else {
              handleOrganizationComplete();
            }
          } else if (status.status === "failed") {
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }
            updateState({
              organizeError: status.error || `${type} failed`,
              currentTask: null,
            });
          }
        } catch (error) {
          console.error("Error polling task status:", error);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          updateState({
            organizeError: `Failed to get ${type} status`,
            currentTask: null,
          });
        }
      }, POLL_INTERVAL);
    },
    [updateState, loadPlanFromFile, handleOrganizationComplete]
  );

  // Handle plan generation
  const handleGeneratePlan = useCallback(async () => {
    console.log("handleGeneratePlan called", {
      canGeneratePlan,
      selectedFolder,
    });

    if (!canGeneratePlan) {
      console.log("Cannot generate plan - conditions not met");
      return;
    }

    updateState({
      organizeError: "",
      isOrganizationComplete: false,
    });

    try {
      console.log("Calling API to generate prompt for folder:", selectedFolder);
      const response = await api.generatePrompt(selectedFolder);
      console.log("API response:", response);

      updateState({
        currentTask: {
          task_id: response.task_id,
          status: "pending",
          progress: 0,
          message: "Generating organization plan...",
        },
      });

      pollTaskStatus(response.task_id, "prompt");
    } catch (error: any) {
      console.error("Error generating plan:", error);
      updateState({
        organizeError:
          error.response?.data?.detail || "Failed to generate plan",
        currentTask: null,
      });
    }
  }, [canGeneratePlan, selectedFolder, updateState, pollTaskStatus]);

  // Handle plan execution
  const handleExecutePlan = useCallback(async () => {
    if (!canExecutePlan) return;

    setConfirmDialog(false);
    updateState({
      organizeError: "",
      isOrganizationComplete: false,
    });

    try {
      const response = await api.executeOrganization(selectedFolder, isDryRun);
      updateState({
        currentTask: {
          task_id: response.task_id,
          status: "pending",
          progress: 0,
          message: isDryRun ? "Running simulation..." : "Organizing files...",
        },
      });

      pollTaskStatus(response.task_id, "organize");
    } catch (error: any) {
      updateState({
        organizeError: error.response?.data?.detail || "Failed to execute plan",
        currentTask: null,
      });
    }
  }, [canExecutePlan, selectedFolder, isDryRun, updateState, pollTaskStatus]);

  // Toggle move expansion
  const toggleMoveExpanded = useCallback((index: number) => {
    setExpandedMoves((prev) => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(index)) {
        newExpanded.delete(index);
      } else {
        newExpanded.add(index);
      }
      return newExpanded;
    });
  }, []);

  // Download plan
  const downloadPlan = useCallback(() => {
    if (!plan) return;

    const dataStr = JSON.stringify(plan, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", "organization_plan.json");
    linkElement.click();
  }, [plan]);

  // Reset organization
  const resetOrganization = useCallback(() => {
    updateState({
      activeStep: 0,
      organizationPlan: null,
      currentTask: null,
      organizeError: "",
      isDryRun: true,
      isOrganizationComplete: false,
    });
    localStorage.removeItem("organizationPlan");
    sessionStorage.setItem("freshLoad", "true");
  }, [updateState]);

  // Render step content
  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderGeneratePlanStep();
      case 1:
        return plan ? renderReviewPlanStep() : null;
      case 2:
        return renderExecutionResultStep();
      default:
        return null;
    }
  };

  // Render generate plan step
  const renderGeneratePlanStep = () => (
    <Paper sx={{ p: 4 }}>
      {/* <Button
        variant="outlined"
        color="warning"
        onClick={() => {
          localStorage.clear();
          sessionStorage.clear();
          updateState({
            currentTask: null,
            scanResults: null,
            selectedFolder: null,
            activeStep: 0,
            organizationPlan: null,
            isOrganizationComplete: false,
            isDryRun: true,
            organizeError: "",
          });
          window.location.reload();
        }}
      >
        Reset Everything
      </Button> */}
      {/* <Alert severity="info" sx={{ mb: 2 }}>
        Debug: API: {apiConnected ? "✓" : "✗"} | Folder:{" "}
        {selectedFolder ? "✓" : "✗"} | Scan: {hasValidScanResults ? "✓" : "✗"} |
        Task: {currentTask ? "Running" : "None"}
      </Alert> */}
      <Typography variant="h5" gutterBottom>
        Generate Organization Plan
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        AI will analyze your scan results and create an intelligent organization
        plan
      </Typography>

      {selectedFolder && hasValidScanResults ? (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            Folder: {selectedFolder}
          </Alert>
          <Alert severity="success" sx={{ mb: 3 }}>
            ✓ Scan results found - ready to generate organization plan
          </Alert>
          <Button
            variant="contained"
            size="large"
            startIcon={<AutoAwesome />}
            onClick={handleGeneratePlan}
            disabled={!canGeneratePlan}
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
          {!selectedFolder
            ? "Please scan a folder first before generating an organization plan"
            : "No scan results found. Please run a scan first."}
        </Alert>
      )}
    </Paper>
  );

  // Render review plan step
  const renderReviewPlanStep = () => (
    <>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                New Folders
              </Typography>
              <Typography variant="h3" color="primary">
                {plan?.folders?.length || 0}
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
                {plan?.moves?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                files will be organized
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {plan?.folders?.length > 0 && (
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
      )}

      {plan?.moves?.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Planned File Moves
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <List>
            {plan.moves.slice(0, MAX_VISIBLE_MOVES).map((move, index) => (
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
                    {expandedMoves.has(index) ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </ListItem>
                <Collapse in={expandedMoves.has(index)}>
                  <Box sx={{ pl: 9, pr: 3, pb: 2 }}>
                    <Alert severity="info" icon={<Info />}>
                      {move.reason}
                    </Alert>
                  </Box>
                </Collapse>
                {index <
                  Math.min(plan.moves.length - 1, MAX_VISIBLE_MOVES - 1) && (
                  <Divider variant="inset" />
                )}
              </React.Fragment>
            ))}
          </List>
          {plan.moves.length > MAX_VISIBLE_MOVES && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ p: 2, textAlign: "center" }}
            >
              ... and {plan.moves.length - MAX_VISIBLE_MOVES} more files
            </Typography>
          )}
        </Paper>
      )}

      <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Preview />}
          onClick={() => {
            updateState({ isDryRun: true });
            setConfirmDialog(true);
          }}
          disabled={!canExecutePlan}
        >
          Preview (Dry Run)
        </Button>
        <Button
          variant="contained"
          size="large"
          color="success"
          startIcon={<PlayArrow />}
          onClick={() => {
            updateState({ isDryRun: false });
            setConfirmDialog(true);
          }}
          disabled={!canExecutePlan}
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
  );

  // Render execution result step
  const renderExecutionResultStep = () => {
    if (!isDryRun && isOrganizationComplete) {
      return (
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
              onClick={resetOrganization}
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
      );
    }

    if (isDryRun && plan) {
      return (
        <Paper sx={{ p: 4 }}>
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
                updateState({ isDryRun: false });
                setConfirmDialog(true);
              }}
              disabled={!canExecutePlan}
            >
              Execute for Real
            </Button>
            <Button
              variant="outlined"
              onClick={() => updateState({ activeStep: 1 })}
            >
              Back to Plan
            </Button>
          </Box>
        </Paper>
      );
    }

    return null;
  };

  // Debug output
  console.log("OrganizePage render state:", {
    selectedFolder,
    hasValidScanResults,
    apiConnected,
    currentTask,
    canGeneratePlan,
    activeStep,
    plan: !!plan,
  });

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

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 3 }}
          onClose={() => updateState({ organizeError: "" })}
        >
          {error}
        </Alert>
      )}

      {renderStepContent()}

      {currentTask?.status === "pending" && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="body1" gutterBottom>
            {currentTask.message}
          </Typography>
          <LinearProgress />
        </Paper>
      )}

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
              This will move files on your system. Make sure you're ready before
              proceeding.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>Cancel</Button>
          <Button
            onClick={handleExecutePlan}
            variant="contained"
            color={isDryRun ? "primary" : "success"}
            disabled={!canExecutePlan}
          >
            {isDryRun ? "Run Preview" : "Execute"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default OrganizePage;
