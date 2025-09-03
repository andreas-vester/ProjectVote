import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link as RouterLink } from 'react-router-dom';
import { Container, Typography, CssBaseline, AppBar, Toolbar, Button } from '@mui/material';
import ApplicationForm from './components/ApplicationForm';
import Archive from './components/Archive';
import VotingForm from './components/VotingForm';

function App() {
  return (
    <Router>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            ProjectVote
          </Typography>
          <Button color="inherit" component={RouterLink} to="/">Startseite</Button>
          <Button color="inherit" component={RouterLink} to="/new">Neuer Antrag</Button>
          <Button color="inherit" component={RouterLink} to="/archive">Archiv</Button>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ mt: 4, mb: 4 }} maxWidth="lg">
        <Routes>
          <Route path="/" element={<Typography>Willkommen bei der Antragsverwaltung.</Typography>} />
          <Route path="/new" element={<ApplicationForm />} />
          <Route path="/archive" element={<Archive />} />
          <Route path="/vote/:token" element={<VotingForm />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
