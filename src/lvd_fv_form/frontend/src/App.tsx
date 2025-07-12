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
            Förderverein Application Management
          </Typography>
          <Button color="inherit" component={RouterLink} to="/">Home</Button>
          <Button color="inherit" component={RouterLink} to="/new">New Application</Button>
          <Button color="inherit" component={RouterLink} to="/archive">Archive</Button>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Typography>Welcome to the application management system.</Typography>} />
          <Route path="/new" element={<ApplicationForm />} />
          <Route path="/archive" element={<Archive />} />
          <Route path="/vote/:token" element={<VotingForm />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
