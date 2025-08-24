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
  TableSortLabel,
  TextField,
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
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Abstimmungsdetails
              </Typography>
              <Table size="small" aria-label="purchases">
                <TableHead>
                  <TableRow>
                    <TableCell>Abstimmende Person</TableCell>
                    <TableCell>Entscheidung</TableCell>
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
  const [filterText, setFilterText] = useState('');
  const [orderBy, setOrderBy] = useState<keyof Application>('id');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const response = await axios.get<Application[]>('http://localhost:8001/applications/archive');
        setApplications(response.data);
      } catch (err) {
        setError('Fehler beim Abrufen der Anträge.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const handleRequestSort = (property: keyof Application) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedAndFilteredApplications = applications
    .filter((app) =>
      app.project_title.toLowerCase().includes(filterText.toLowerCase())
    )
    .sort((a, b) => {
      if (a[orderBy] < b[orderBy]) {
        return order === 'asc' ? -1 : 1;
      }
      if (a[orderBy] > b[orderBy]) {
        return order === 'asc' ? 1 : -1;
      }
      return 0;
    });

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden', minHeight: 600 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ p: 2 }}>
        Antragsarchiv
      </Typography>
      <Box sx={{ p: 2 }}>
        <TextField
          label="Filter by Project Title"
          variant="outlined"
          fullWidth
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
        />
      </Box>
      <TableContainer sx={{ height: 440, overflowY: 'scroll' }}>
          <Table stickyHeader aria-label="sticky table" sx={{ tableLayout: 'fixed' }}>
            <TableHead>
              <TableRow>
                <TableCell sx={{ width: '5%' }} /> {/* For expand button */}
                <TableCell sx={{ width: '5%' }} sortDirection={orderBy === 'id' ? order : false}>
                  <TableSortLabel
                    active={orderBy === 'id'}
                    direction={orderBy === 'id' ? order : 'asc'}
                    onClick={() => handleRequestSort('id')}
                  >
                    ID
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ width: '20%' }}>Antragsteller</TableCell>
                <TableCell sx={{ width: '30%' }} sortDirection={orderBy === 'project_title' ? order : false}>
                  <TableSortLabel
                    active={orderBy === 'project_title'}
                    direction={orderBy === 'project_title' ? order : 'asc'}
                    onClick={() => handleRequestSort('project_title')}
                  >
                    Projekttitel
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ width: '20%' }}>Abteilung/Fachschaft</TableCell>
                <TableCell sx={{ width: '10%' }} sortDirection={orderBy === 'costs' ? order : false}>
                  <TableSortLabel
                    active={orderBy === 'costs'}
                    direction={orderBy === 'costs' ? order : 'asc'}
                    onClick={() => handleRequestSort('costs')}
                  >
                    Kosten
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ width: '10%' }} sortDirection={orderBy === 'status' ? order : false}>
                  <TableSortLabel
                    active={orderBy === 'status'}
                    direction={orderBy === 'status' ? order : 'asc'}
                    onClick={() => handleRequestSort('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedAndFilteredApplications.length > 0 ? (
                sortedAndFilteredApplications.map((app) => (
                  <Row key={app.id} application={app} />
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No applications found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
    </Paper>
  );
};

export default Archive;
