import React, { useState, useEffect } from "react";
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  useTheme,
  alpha,
} from "@mui/material";
import {
  CreditCard,
  Check,
  Warning,
  Refresh,
  Cancel,
  Download,
  Email,
  Key,
  Storage,
  TrendingUp,
} from "@mui/icons-material";

interface LicenseInfo {
  status: "active" | "trial" | "expired" | "none";
  plan: "starter" | "professional" | "enterprise" | "trial";
  expiresAt: string;
  creditsUsed: number;
  creditsTotal: number;
  customerEmail: string;
}

const AccountPage: React.FC = () => {
  const theme = useTheme();
  const [license, setLicense] = useState<LicenseInfo>({
    status: "trial",
    plan: "trial",
    expiresAt: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    creditsUsed: 2,
    creditsTotal: 10,
    customerEmail: "user@example.com",
  });
  const [licenseKey, setLicenseKey] = useState("");
  const [showActivateDialog, setShowActivateDialog] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleActivateLicense = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLicense({
        ...license,
        status: "active",
        plan: "professional",
        creditsTotal: 50,
      });
      setShowActivateDialog(false);
      setLoading(false);
    }, 2000);
  };

  const handleManageSubscription = () => {
    // Open Stripe customer portal
    window.open("https://billing.stripe.com/p/login/test", "_blank");
  };

  const getStatusColor = () => {
    switch (license.status) {
      case "active":
        return "success";
      case "trial":
        return "info";
      case "expired":
        return "error";
      default:
        return "default";
    }
  };

  const creditsPercentage = (license.creditsUsed / license.creditsTotal) * 100;

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight={600}>
          Account & License
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your subscription and track usage
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* License Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
              >
                <Typography variant="h6">License Status</Typography>
                <Chip
                  label={license.status.toUpperCase()}
                  color={getStatusColor()}
                  size="small"
                />
              </Box>

              <List>
                <ListItem>
                  <ListItemText
                    primary="Plan"
                    secondary={
                      license.plan.charAt(0).toUpperCase() +
                      license.plan.slice(1)
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton size="small">
                      <CreditCard />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Email"
                    secondary={license.customerEmail}
                  />
                  <ListItemSecondaryAction>
                    <IconButton size="small">
                      <Email />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Expires"
                    secondary={new Date(license.expiresAt).toLocaleDateString()}
                  />
                </ListItem>
              </List>

              <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
                {license.status === "active" ? (
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={handleManageSubscription}
                  >
                    Manage Subscription
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => setShowActivateDialog(true)}
                    startIcon={<Key />}
                  >
                    Activate License
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Usage Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Credit Usage
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography variant="body2">
                    {license.creditsUsed} / {license.creditsTotal} credits used
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {Math.round(creditsPercentage)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={creditsPercentage}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                  }}
                />
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ mt: 1 }}
                >
                  1 credit = 500 files organized
                </Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Paper
                    sx={{
                      p: 2,
                      textAlign: "center",
                      bgcolor: "background.default",
                    }}
                  >
                    <Storage color="primary" />
                    <Typography variant="h4">
                      {license.creditsUsed * 500}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Files Organized
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6}>
                  <Paper
                    sx={{
                      p: 2,
                      textAlign: "center",
                      bgcolor: "background.default",
                    }}
                  >
                    <TrendingUp color="success" />
                    <Typography variant="h4">
                      {(license.creditsTotal - license.creditsUsed) * 500}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Files Remaining
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Download />}
                  onClick={() => {
                    const invoices = [
                      { date: "2024-01-01", amount: "$29.00" },
                      { date: "2024-02-01", amount: "$29.00" },
                    ];
                    console.log("Download invoices:", invoices);
                  }}
                >
                  Download Invoices
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Refresh />}
                  onClick={() => window.location.reload()}
                >
                  Sync License
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  color="error"
                  startIcon={<Cancel />}
                  onClick={() => {
                    if (
                      window.confirm(
                        "Are you sure you want to cancel your subscription?"
                      )
                    ) {
                      handleManageSubscription();
                    }
                  }}
                >
                  Cancel Subscription
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Upgrade Prompt */}
        {license.status === "trial" && (
          <Grid item xs={12}>
            <Alert
              severity="info"
              action={
                <Button color="inherit" size="small" href="/pricing">
                  Upgrade Now
                </Button>
              }
            >
              You're currently on a trial plan. Upgrade to unlock unlimited file
              organization!
            </Alert>
          </Grid>
        )}
      </Grid>

      {/* Activate License Dialog */}
      <Dialog
        open={showActivateDialog}
        onClose={() => setShowActivateDialog(false)}
      >
        <DialogTitle>Activate License</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Enter your license key to activate your subscription
          </Typography>
          <TextField
            fullWidth
            label="License Key"
            value={licenseKey}
            onChange={(e) => setLicenseKey(e.target.value)}
            placeholder="XXXX-XXXX-XXXX-XXXX"
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowActivateDialog(false)}>Cancel</Button>
          <Button
            onClick={handleActivateLicense}
            variant="contained"
            disabled={!licenseKey || loading}
          >
            {loading ? "Activating..." : "Activate"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AccountPage;
