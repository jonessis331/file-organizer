import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Divider,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import {
  Save,
  RestoreFromTrash,
  Delete,
  Add,
  Remove,
  Info,
} from "@mui/icons-material";
import { api } from "../services/api";

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    maxFilesToScan: 1000,
    skipHiddenFiles: true,
    preserveProjectFolders: true,
    createBackups: true,
    openAIApiKey: "",
    skipFolders: [] as string[],
    fileCategories: {} as Record<string, string[]>,
  });

  const [saved, setSaved] = useState(false);
  const [newSkipFolder, setNewSkipFolder] = useState("");
  const [backups, setBackups] = useState<any[]>([]);
  const [showBackups, setShowBackups] = useState(false);

  useEffect(() => {
    loadSettings();
    loadBackups();
  }, []);

  const loadSettings = async () => {
    try {
      // Load from localStorage
      const savedSettings = localStorage.getItem("organizerSettings");
      if (savedSettings) {
        setSettings(JSON.parse(savedSettings));
      }

      // Also load config from API
      const config = await api.getConfig();
      setSettings((prev) => ({
        ...prev,
        maxFilesToScan: config.max_files_to_scan || 1000,
        skipFolders: config.skip_folders || [],
        fileCategories: config.file_categories || {},
      }));
    } catch (error) {
      console.error("Failed to load settings:", error);
    }
  };

  const loadBackups = async () => {
    try {
      const response = await api.listBackups();
      setBackups(response.backups || []);
    } catch (error) {
      console.error("Failed to load backups:", error);
    }
  };

  const handleSaveSettings = () => {
    localStorage.setItem("organizerSettings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleAddSkipFolder = () => {
    if (newSkipFolder && !settings.skipFolders.includes(newSkipFolder)) {
      setSettings((prev) => ({
        ...prev,
        skipFolders: [...prev.skipFolders, newSkipFolder],
      }));
      setNewSkipFolder("");
    }
  };
  const handleClearData = () => {
    if (
      window.confirm(
        "Are you sure you want to clear all data? This cannot be undone."
      )
    ) {
      localStorage.clear();
      window.location.reload();
    }
  };

  const handleRemoveSkipFolder = (folder: string) => {
    setSettings((prev) => ({
      ...prev,
      skipFolders: prev.skipFolders.filter((f) => f !== folder),
    }));
  };

  const handleRestoreBackup = async (backupFile: string) => {
    if (
      window.confirm(
        "Are you sure you want to restore from this backup? Current file organization will be reverted."
      )
    ) {
      try {
        const response = await api.restoreBackup(backupFile);
        if (response.success) {
          Alert.success("Backup restored successfully!");
          loadBackups(); // Refresh the list
        } else {
          Alert.error("Failed to restore backup");
        }
      } catch (error) {
        console.error("Failed to restore backup:", error);
        Alert.error("Failed to restore backup");
      }
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight={600}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure organization rules and preferences
        </Typography>
      </Box>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      {/* General Settings */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          General Settings
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Max Files to Scan"
              type="number"
              value={settings.maxFilesToScan}
              onChange={(e) =>
                setSettings((prev) => ({
                  ...prev,
                  maxFilesToScan: parseInt(e.target.value) || 1000,
                }))
              }
              helperText="Maximum number of files to scan at once"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.skipHiddenFiles}
                  onChange={(e) =>
                    setSettings((prev) => ({
                      ...prev,
                      skipHiddenFiles: e.target.checked,
                    }))
                  }
                />
              }
              label="Skip hidden files and folders"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.preserveProjectFolders}
                  onChange={(e) =>
                    setSettings((prev) => ({
                      ...prev,
                      preserveProjectFolders: e.target.checked,
                    }))
                  }
                />
              }
              label="Preserve organized project folders (Git repos, etc.)"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.createBackups}
                  onChange={(e) =>
                    setSettings((prev) => ({
                      ...prev,
                      createBackups: e.target.checked,
                    }))
                  }
                />
              }
              label="Create backups before organizing"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Skip Folders */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Folders to Skip
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Add folder to skip (e.g., node_modules)"
            value={newSkipFolder}
            onChange={(e) => setNewSkipFolder(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleAddSkipFolder()}
          />
          <Button
            variant="contained"
            onClick={handleAddSkipFolder}
            startIcon={<Add />}
          >
            Add
          </Button>
        </Box>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {settings.skipFolders.map((folder) => (
            <Chip
              key={folder}
              label={folder}
              onDelete={() => handleRemoveSkipFolder(folder)}
              deleteIcon={<Remove />}
            />
          ))}
        </Box>
      </Paper>

      {/* File Categories */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          File Categories
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={2}>
          {Object.entries(settings.fileCategories).map(
            ([category, extensions]) => (
              <Grid item xs={12} md={6} key={category}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {category}
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                      {(extensions as string[]).slice(0, 5).map((ext) => (
                        <Chip key={ext} label={ext} size="small" />
                      ))}
                      {(extensions as string[]).length > 5 && (
                        <Chip
                          label={`+${(extensions as string[]).length - 5} more`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )
          )}
        </Grid>
      </Paper>

      {/* Backups */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            mb: 2,
          }}
        >
          <Typography variant="h6">Backups</Typography>
          <Button
            variant="outlined"
            onClick={() => setShowBackups(!showBackups)}
            startIcon={<RestoreFromTrash />}
          >
            View Backups ({backups.length})
          </Button>
        </Box>

        {showBackups && (
          <>
            <Divider sx={{ mb: 2 }} />
            <List>
              {backups.map((backup, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={backup.type}
                    secondary={`${backup.timestamp} - ${backup.files} files`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="restore"
                      onClick={() => handleRestoreBackup(backup.file)}
                    >
                      <RestoreFromTrash />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </>
        )}
      </Paper>

      {/* Actions */}
      <Box sx={{ display: "flex", gap: 2, justifyContent: "space-between" }}>
        <Button
          variant="outlined"
          color="error"
          startIcon={<Delete />}
          onClick={handleClearData}
        >
          Clear All Data
        </Button>

        <Button
          variant="contained"
          startIcon={<Save />}
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>
      </Box>
    </Container>
  );
};

export default SettingsPage;
