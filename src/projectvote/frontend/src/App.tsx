import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link as RouterLink } from 'react-router-dom';
import { Container, Typography, CssBaseline, AppBar, Toolbar, Button, Box } from '@mui/material';
import ApplicationForm from './components/ApplicationForm';
import Archive from './components/Archive';
import VotingForm from './components/VotingForm';
import { getVersion } from './apiService';

function App() {
  const [version, setVersion] = useState<string>('');

  useEffect(() => {
    getVersion().then(setVersion);
  }, []);

  return (
    <Router>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, display: 'flex', alignItems: 'baseline', gap: 1 }}>
              ProjectVote
              {version && (
                <Typography variant="caption" sx={{ opacity: 0.8, fontSize: '0.8rem' }}>
                  v{version}
                </Typography>
              )}
            </Typography>
            <Button color="inherit" component={RouterLink} to="/">Startseite</Button>
            <Button color="inherit" component={RouterLink} to="/new">Neuer Antrag</Button>
            <Button color="inherit" component={RouterLink} to="/archive">Archiv</Button>
          </Toolbar>
        </AppBar>
        <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }} maxWidth="lg">
          <Routes>
            <Route path="/" element={<Typography>Willkommen bei der Antragsverwaltung.</Typography>} />
            <Route path="/new" element={<ApplicationForm />} />
            <Route path="/archive" element={<Archive />} />
            <Route path="/vote/:token" element={<VotingForm />} />
          </Routes>
        </Container>
        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: 'auto',
            backgroundColor: (theme) =>
              theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[800],
            textAlign: 'center',
          }}
        >
          <Container maxWidth="lg">
            <Typography variant="body2" color="text.secondary">
              ProjectVote {version ? `v${version}` : ''} &copy; {new Date().getFullYear()}
            </Typography>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
