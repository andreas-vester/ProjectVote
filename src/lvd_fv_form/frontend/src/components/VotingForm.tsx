import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  Typography,
  Paper,
  Box,
  CircularProgress,
  Alert,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Snackbar,
} from '@mui/material';

// Simplified application interface for the voting form
interface Application {
  id: number;
  project_title: string;
  project_description: string;
  costs: number;
  department: string;
}

type VoteOption = 'approve' | 'reject' | 'abstain';

const voteOptionLabels: Record<VoteOption, string> = {
  approve: 'Zustimmen',
  reject: 'Ablehnen',
  abstain: 'Enthalten',
};

const VotingForm: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [application, setApplication] = useState<Application | null>(null);
  const [voterEmail, setVoterEmail] = useState<string>('');
  const [voteOptions, setVoteOptions] = useState<VoteOption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVote, setSelectedVote] = useState<VoteOption>('approve');
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  } | null>(null);

  useEffect(() => {
    const fetchVoteDetails = async () => {
      if (!token) {
        setError('Kein Abstimmungs-Token gefunden.');
        setLoading(false);
        return;
      }
      try {
        const response = await axios.get(`http://localhost:8001/vote/${token}`);
        setApplication(response.data.application);
        setVoterEmail(response.data.voter_email);
        setVoteOptions(response.data.vote_options);
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'Fehler beim Abrufen der Abstimmungsdaten.';
        setError(errorMessage);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchVoteDetails();
  }, [token]);

  const handleVoteChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedVote(event.target.value as VoteOption);
  };

  const handleCloseSnackbar = () => {
    setSnackbar(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSnackbar(null);

    try {
      const response = await axios.post(`http://localhost:8001/vote/${token}`, {
        decision: selectedVote,
      });
      setSnackbar({
        open: true,
        message: response.data.message || 'Stimme erfolgreich abgegeben!',
        severity: 'success',
      });
    } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'Unbekannter Fehler.';
        setSnackbar({
          open: true,
          message: `Fehler beim Abstimmen: ${errorMessage}`,
          severity: 'error',
        });
        console.error(err);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!application) return <Alert severity="info">Antragsdaten konnten nicht geladen werden.</Alert>;

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Abstimmung für Antrag: {application.project_title}
        </Typography>
        
        <Box sx={{ mb: 3, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
            <Typography variant="h6">Antragsdetails</Typography>
            <Typography><b>Abteilung/Fachschaft:</b> {application.department}</Typography>
            <Typography><b>Kosten:</b> €{application.costs.toFixed(2)}</Typography>
            <Typography><b>Beschreibung:</b> {application.project_description}</Typography>
        </Box>

        <Typography variant="h5" component="h2" gutterBottom>
          Stimme abgeben als {voterEmail}
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <FormControl component="fieldset" required>
                <FormLabel component="legend">Ihre Entscheidung</FormLabel>
                <RadioGroup
                    aria-label="decision"
                    name="decision"
                    value={selectedVote}
                    onChange={handleVoteChange}
                    row
                >
                  {voteOptions.map(option => (
                    <FormControlLabel key={option} value={option} control={<Radio />} label={voteOptionLabels[option]} />
                  ))}
                </RadioGroup>
            </FormControl>

            <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={!!snackbar && snackbar.severity === 'success'}
            >
                Stimme abgeben
            </Button>
        </Box>
      </Paper>
      {snackbar && (
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      )}
    </Container>
  );
};

export default VotingForm;
