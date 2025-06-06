import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge,
  Tooltip,
  alpha,
} from "@mui/material";
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Scanner as ScannerIcon,
  AutoAwesome as OrganizeIcon,
  Settings as SettingsIcon,
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon,
  CheckCircle as ConnectedIcon,
  Error as DisconnectedIcon,
  AccountCircleOutlined,
} from "@mui/icons-material";

// Import pages
import HomePage from "./pages/HomePage";
import ScanPage from "./pages/ScanPage";
import OrganizePage from "./pages/OrganizePage";
import SettingsPage from "./pages/SettingsPage";
//import neatlyLogo from "../assets/neatly_logo.png";
import neatlyLogo from "../assets/neatly_icon.png";
import AccountPage from "./pages/AccountPage";
import { AppStateProvider } from "./contexts/AppStateContext";
// Import API service
import { api } from "./services/api";

const drawerWidth = 240;

function AppContent() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const checkApi = async () => {
      const connected = await api.checkHealth();
      setApiConnected(connected);
    };

    checkApi();
    const interval = setInterval(checkApi, 5000);
    return () => clearInterval(interval);
  }, []);

  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: {
        main: darkMode ? "#90caf9" : "#1976d2",
      },
      secondary: {
        main: darkMode ? "#f48fb1" : "#dc004e",
      },
      background: {
        default: darkMode ? "#0a0a0a" : "#f5f5f5",
        paper: darkMode ? "#1a1a1a" : "#ffffff",
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 700,
      },
      h2: {
        fontWeight: 600,
      },
      h3: {
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: 16,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 600,
            borderRadius: 12,
            padding: "10px 24px",
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            boxShadow: darkMode
              ? "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
              : "0 8px 32px 0 rgba(31, 38, 135, 0.15)",
          },
        },
      },
    },
  });

  const menuItems = [
    { text: "Home", icon: <HomeIcon />, path: "/" },
    { text: "Scan", icon: <ScannerIcon />, path: "/scan" },
    { text: "Organize", icon: <OrganizeIcon />, path: "/organize" },
    { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
    { text: "Account", icon: <AccountCircleOutlined />, path: "/account" },
  ];

  const drawer = (
    <Box>
      <Toolbar
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
          color: "white",
        }}
      >
        <Box
          component="img"
          src={neatlyLogo}
          alt="Neatly Logo"
          sx={{
            height: 40,
            width: "auto",
            // If in light mode, invert the white logo to black
            filter: darkMode ? "invert(1)" : "invert(1)",
          }}
        />
        <Typography variant="h6" noWrap component="div">
          Neatly
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            component={Link}
            to={item.path}
            onClick={() => setMobileOpen(false)}
            sx={{
              borderRadius: 2,
              mx: 1,
              my: 0.5,
              backgroundColor:
                location.pathname === item.path
                  ? alpha(theme.palette.primary.main, 0.15)
                  : "transparent",
              "&:hover": {
                backgroundColor: alpha(theme.palette.primary.main, 0.08),
              },
            }}
          >
            <ListItemIcon
              sx={{
                color:
                  location.pathname === item.path
                    ? theme.palette.primary.main
                    : theme.palette.text.secondary,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.text}
              sx={{
                color:
                  location.pathname === item.path
                    ? theme.palette.primary.main
                    : theme.palette.text.primary,
              }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <AppStateProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: "flex" }}>
          <AppBar
            position="fixed"
            sx={{
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
              backgroundColor: theme.palette.background.paper,
              color: theme.palette.text.primary,
              boxShadow: "none",
              borderBottom: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={() => setMobileOpen(!mobileOpen)}
                sx={{ mr: 2, display: { sm: "none" } }}
              >
                <MenuIcon />
              </IconButton>

              <Box sx={{ flexGrow: 1 }} />

              <Tooltip
                title={apiConnected ? "API Connected" : "API Disconnected"}
              >
                <IconButton>
                  <Badge
                    variant="dot"
                    color={apiConnected ? "success" : "error"}
                    sx={{
                      "& .MuiBadge-badge": {
                        boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
                      },
                    }}
                  >
                    {apiConnected ? <ConnectedIcon /> : <DisconnectedIcon />}
                  </Badge>
                </IconButton>
              </Tooltip>

              <IconButton
                onClick={() => setDarkMode(!darkMode)}
                color="inherit"
              >
                {darkMode ? <LightIcon /> : <DarkIcon />}
              </IconButton>
            </Toolbar>
          </AppBar>

          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          >
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={() => setMobileOpen(false)}
              ModalProps={{
                keepMounted: true,
              }}
              sx={{
                display: { xs: "block", sm: "none" },
                "& .MuiDrawer-paper": {
                  boxSizing: "border-box",
                  width: drawerWidth,
                  backgroundColor: theme.palette.background.paper,
                },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: "none", sm: "block" },
                "& .MuiDrawer-paper": {
                  boxSizing: "border-box",
                  width: drawerWidth,
                  backgroundColor: theme.palette.background.paper,
                  borderRight: `1px solid ${theme.palette.divider}`,
                },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>

          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              backgroundColor: theme.palette.background.default,
              minHeight: "100vh",
            }}
          >
            <Toolbar />
            <Routes>
              <Route
                path="/"
                element={<HomePage apiConnected={apiConnected} />}
              />
              <Route
                path="/scan"
                element={<ScanPage apiConnected={apiConnected} />}
              />
              <Route
                path="/organize"
                element={<OrganizePage apiConnected={apiConnected} />}
              />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/account" element={<AccountPage />} />
            </Routes>
          </Box>
        </Box>
      </ThemeProvider>
    </AppStateProvider>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
