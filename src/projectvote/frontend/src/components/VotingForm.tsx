import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Link,
} from '@mui/material';
import { AttachFile } from '@mui/icons-material';
import axios from 'axios';
import {
  getVoteDetails,
  castVote,
  getAttachmentUrl,
  type VoteDetails,
  type VoteCreate,
  VoteOption,
} from '../apiService';

const voteOptionLabels: Record<VoteOption, string> = {
  [VoteOption.APPROVE]: 'Zustimmen',
  [VoteOption.REJECT]: 'Ablehnen',
  [VoteOption.ABSTAIN]: 'Enthalten',
};

const VotingForm: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [voteDetails, setVoteDetails] = useState<VoteDetails | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVote, setSelectedVote] = useState<VoteOption>(VoteOption.APPROVE);
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
        const data = await getVoteDetails(token);
        setVoteDetails(data);
        if (data.vote_options.length > 0) {
          setSelectedVote(data.vote_options[0]);
        }
      } catch (err) {
        let errorMessage = 'Fehler beim Abrufen der Abstimmungsdaten.';
        if (axios.isAxiosError(err) && err.response) {
          errorMessage = err.response.data?.detail || errorMessage;
        }
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

    if (!token) {
      setError('Kein Abstimmungs-Token gefunden.');
      return;
    }

    try {
      const voteData: VoteCreate = { decision: selectedVote };
      const response = await castVote(token, voteData);
      setSnackbar({
        open: true,
        message: response.message || 'Stimme erfolgreich abgegeben!',
        severity: 'success',
      });
    } catch (err) {
      let errorMessage = 'Unbekannter Fehler.';
      if (axios.isAxiosError(err) && err.response) {
        errorMessage = err.response.data?.detail || errorMessage;
      }
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
  if (!voteDetails) return <Alert severity="info">Antragsdaten konnten nicht geladen werden.</Alert>;

  const { application, voter_email, vote_options } = voteDetails;

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
          
          {application.attachments && application.attachments.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                <b>Anhänge:</b>
              </Typography>
              <List dense>
                {application.attachments.map((attachment) => (
                  <ListItem key={attachment.id} sx={{ pl: 0 }}>
                    <ListItemIcon>
                      <AttachFile />
                    </ListItemIcon>
                    <ListItemText>
                      <Link
                        href={getAttachmentUrl(token!, attachment.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        underline="hover"
                      >
                        {attachment.filename}
                      </Link>
                    </ListItemText>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>

        <Typography variant="h5" component="h2" gutterBottom>
          Stimme abgeben als {voter_email}
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
              {vote_options.map((option) => (
                <FormControlLabel
                  key={option}
                  value={option}
                  control={<Radio />}
                  label={voteOptionLabels[option]}
                />
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
