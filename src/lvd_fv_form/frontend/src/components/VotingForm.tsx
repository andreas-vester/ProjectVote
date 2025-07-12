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

const VotingForm: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [application, setApplication] = useState<Application | null>(null);
  const [voterEmail, setVoterEmail] = useState<string>('');
  const [voteOptions, setVoteOptions] = useState<VoteOption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVote, setSelectedVote] = useState<VoteOption>('approve');
  const [feedback, setFeedback] = useState<{type: 'success' | 'error', message: string} | null>(null);

  useEffect(() => {
    const fetchVoteDetails = async () => {
      if (!token) {
        setError('No voting token provided.');
        setLoading(false);
        return;
      }
      try {
        const response = await axios.get(`http://localhost:8001/vote/${token}`);
        setApplication(response.data.application);
        setVoterEmail(response.data.voter_email);
        setVoteOptions(response.data.vote_options);
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'Failed to fetch voting data.';
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

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFeedback(null);

    try {
      const response = await axios.post(`http://localhost:8001/vote/${token}`, {
        decision: selectedVote,
      });
      setFeedback({type: 'success', message: response.data.message || 'Vote cast successfully!'});
    } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'An unknown error occurred.';
        setFeedback({type: 'error', message: `Failed to cast vote: ${errorMessage}`});
        console.error(err);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!application) return <Alert severity="info">Application data could not be loaded.</Alert>;

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Vote on Application: {application.project_title}
        </Typography>
        
        <Box sx={{ mb: 3, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
            <Typography variant="h6">Application Details</Typography>
            <Typography><b>Department:</b> {application.department}</Typography>
            <Typography><b>Costs:</b> €{application.costs.toFixed(2)}</Typography>
            <Typography><b>Description:</b> {application.project_description}</Typography>
        </Box>

        <Typography variant="h5" component="h2" gutterBottom>
          Cast Your Vote as {voterEmail}
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <FormControl component="fieldset" required>
                <FormLabel component="legend">Your Decision</FormLabel>
                <RadioGroup
                    aria-label="decision"
                    name="decision"
                    value={selectedVote}
                    onChange={handleVoteChange}
                    row
                >
                  {voteOptions.map(option => (
                    <FormControlLabel key={option} value={option} control={<Radio />} label={option.charAt(0).toUpperCase() + option.slice(1)} />
                  ))}
                </RadioGroup>
            </FormControl>

            <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={!!feedback && feedback.type === 'success'}
            >
                Submit Your Vote
            </Button>

            {feedback && (
                <Alert severity={feedback.type} sx={{ mt: 2 }}>
                    {feedback.message}
                </Alert>
            )}
        </Box>
      </Paper>
    </Container>
  );
};

export default VotingForm;
