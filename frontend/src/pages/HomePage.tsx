import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Paper,
  Chip,
  LinearProgress,
  IconButton,
  alpha,
  useTheme,
} from "@mui/material";
import {
  FolderOpen,
  Scanner,
  AutoAwesome,
  TrendingUp,
  AccessTime,
  CheckCircle,
  Warning,
  ArrowForward,
} from "@mui/icons-material";

interface HomePageProps {
  apiConnected: boolean;
}

const HomePage: React.FC<HomePageProps> = ({ apiConnected }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [stats, setStats] = useState({
    filesOrganized: 0,
    foldersCreated: 0,
    lastScan: null as string | null,
  });

  useEffect(() => {
    // Load stats from localStorage
    const savedStats = localStorage.getItem("organizerStats");
    if (savedStats) {
      setStats(JSON.parse(savedStats));
    }
  }, []);

  const features = [
    {
      icon: <Scanner fontSize="large" />,
      title: "Smart Scanning",
      description: "AI-powered analysis of your file structure",
      color: theme.palette.primary.main,
      path: "/scan",
    },
    {
      icon: <AutoAwesome fontSize="large" />,
      title: "Auto Organization",
      description: "Intelligent categorization using KonMari principles",
      color: theme.palette.secondary.main,
      path: "/organize",
    },
    {
      icon: <TrendingUp fontSize="large" />,
      title: "Progress Tracking",
      description: "Real-time updates and detailed analytics",
      color: theme.palette.success.main,
      path: "/scan",
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box sx={{ mb: 6, mt: 4 }}>
        <Typography
          variant="h2"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 700,
            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          File Organizer
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          Transform your digital chaos into organized bliss
        </Typography>

        {/* Status Alert */}
        <Paper
          sx={{
            p: 2,
            mb: 4,
            backgroundColor: apiConnected
              ? alpha(theme.palette.success.main, 0.1)
              : alpha(theme.palette.error.main, 0.1),
            border: `1px solid ${
              apiConnected
                ? theme.palette.success.main
                : theme.palette.error.main
            }`,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {apiConnected ? (
              <CheckCircle color="success" />
            ) : (
              <Warning color="error" />
            )}
            <Typography variant="body1">
              {apiConnected
                ? "Backend API is connected and ready"
                : "Backend API is not running. Please start it with: python backend/api/main.py"}
            </Typography>
          </Box>
        </Paper>

        {/* Quick Start */}
        <Card
          sx={{
            background: `linear-gradient(135deg, ${alpha(
              theme.palette.primary.main,
              0.1
            )} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 100%)`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
            mb: 4,
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight={600}>
              Quick Start
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Select a folder and let AI organize your files automatically
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<FolderOpen />}
              endIcon={<ArrowForward />}
              onClick={() => navigate("/scan")}
              disabled={!apiConnected}
              sx={{
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                "&:hover": {
                  background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
                },
              }}
            >
              Choose Folder to Organize
            </Button>
          </CardContent>
        </Card>

        {/* Stats */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: "center" }}>
              <Typography variant="h3" color="primary" fontWeight={600}>
                {stats.filesOrganized}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Files Organized
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: "center" }}>
              <Typography variant="h3" color="secondary" fontWeight={600}>
                {stats.foldersCreated}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Folders Created
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: "center" }}>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 1,
                }}
              >
                <AccessTime color="action" />
                <Typography variant="body2" color="text.secondary">
                  {stats.lastScan || "No scans yet"}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Features */}
        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: "100%",
                  cursor: "pointer",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    transform: "translateY(-8px)",
                    boxShadow: `0 12px 40px ${alpha(feature.color, 0.3)}`,
                  },
                }}
                onClick={() => navigate(feature.path)}
              >
                <CardContent sx={{ textAlign: "center", p: 4 }}>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      borderRadius: 3,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      mx: "auto",
                      mb: 3,
                      backgroundColor: alpha(feature.color, 0.1),
                      color: feature.color,
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" gutterBottom fontWeight={600}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage;
