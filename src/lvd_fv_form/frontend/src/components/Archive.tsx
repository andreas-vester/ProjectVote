import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Collapse,
  Box,
  IconButton,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

interface Vote {
  voter_email: string;
  decision: 'approve' | 'reject' | 'abstain' | null;
}

interface Application {
  id: number;
  first_name: string;
  last_name: string;
  applicant_email: string;
  department: string;
  project_title: string;
  project_description: string;
  costs: number;
  status: 'pending' | 'approved' | 'rejected';
  votes: Vote[]; // Add votes array
}

const Row: React.FC<{ application: Application }> = ({ application }) => {
  const [open, setOpen] = useState(false);

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          {application.id}
        </TableCell>
        <TableCell>{`${application.first_name} ${application.last_name}`}</TableCell>
        <TableCell>{application.project_title}</TableCell>
        <TableCell>{application.department}</TableCell>
        <TableCell>{`€${application.costs.toFixed(2)}`}</TableCell>
        <TableCell>{application.status}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Voting Details
              </Typography>
              <Table size="small" aria-label="purchases">
                <TableHead>
                  <TableRow>
                    <TableCell>Voter Email</TableCell>
                    <TableCell>Decision</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {application.votes.map((vote, index) => (
                    <TableRow key={index}>
                      <TableCell>{vote.voter_email}</TableCell>
                      <TableCell>{vote.decision || 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
};

const Archive: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const response = await axios.get<Application[]>('http://localhost:8001/applications');
        setApplications(response.data);
      } catch (err) {
        setError('Failed to fetch applications.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ p: 2 }}>
        Antragsarchiv
      </Typography>
      <TableContainer>
        <Table stickyHeader aria-label="sticky table">
          <TableHead>
            <TableRow>
              <TableCell /> {/* For expand button */}
              <TableCell>ID</TableCell>
              <TableCell>Antragsteller</TableCell>
              <TableCell>Projekttitel</TableCell>
              <TableCell>Fachschaft</TableCell>
              <TableCell>Kosten</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {applications.map((app) => (
              <Row key={app.id} application={app} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default Archive;
