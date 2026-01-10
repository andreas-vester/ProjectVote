import React, { useEffect, useState } from 'react';
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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Link,
} from '@mui/material';
import { AttachFile } from '@mui/icons-material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { getApplicationsArchive, getPublicAttachmentUrl, type ApplicationOut, ApplicationStatus, VoteOption } from '../apiService';

// Helper function to format timestamps
const formatTimestamp = (timestamp: string | Date | undefined): string => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleString('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const applicationStatusTranslations: Record<ApplicationStatus, string> = {
  [ApplicationStatus.PENDING]: 'Ausstehend',
  [ApplicationStatus.APPROVED]: 'Genehmigt',
  [ApplicationStatus.REJECTED]: 'Abgelehnt',
};

const voteOptionTranslations: Record<VoteOption, string> = {
  [VoteOption.APPROVE]: 'Zustimmung',
  [VoteOption.REJECT]: 'Ablehnung',
  [VoteOption.ABSTAIN]: 'Enthaltung',
};

const Row: React.FC<{ application: ApplicationOut }> = ({ application }) => {
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
        <TableCell>{applicationStatusTranslations[application.status] || application.status}</TableCell>
        <TableCell>{formatTimestamp(application.created_at)}</TableCell>
        <TableCell>{application.concluded_at ? formatTimestamp(application.concluded_at) : 'N/A'}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Details
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }} gutterBottom>
                <strong>Projektbeschreibung:</strong>
                <br />
                {application.project_description}
              </Typography>

              <Typography variant="h6" gutterBottom component="div" sx={{ mt: 2 }}>
                Abstimmungsdetails
              </Typography>
              <Table size="small" aria-label="purchases">
                <TableHead>
                  <TableRow>
                    <TableCell>Abstimmende Person</TableCell>
                    <TableCell>Entscheidung</TableCell>
                    <TableCell>Abgestimmt am</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {application.votes.map((vote, index) => (
                    <TableRow key={index}>
                      <TableCell>{vote.voter_email}</TableCell>
                      <TableCell>{vote.decision ? voteOptionTranslations[vote.decision] : 'N/A'}</TableCell>
                      <TableCell>{vote.voted_at ? formatTimestamp(vote.voted_at) : 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {application.attachments && application.attachments.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom component="div">
                    Anhänge
                  </Typography>
                  <List dense>
                    {application.attachments.map((attachment) => (
                      <ListItem key={attachment.id} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <AttachFile />
                        </ListItemIcon>
                        <ListItemText>
                          <Link
                            href={getPublicAttachmentUrl(attachment.id)}
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
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
};

const Archive: React.FC = () => {
  const [applications, setApplications] = useState<ApplicationOut[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filterText, setFilterText] = useState('');
  const [orderBy, setOrderBy] = useState<keyof ApplicationOut>('id');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const data = await getApplicationsArchive();
        setApplications(data);
      } catch (err) {
        setError('Fehler beim Abrufen der Anträge.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const handleRequestSort = (property: keyof ApplicationOut) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedAndFilteredApplications = applications
    .filter((app) =>
      app.project_title.toLowerCase().includes(filterText.toLowerCase())
    )
    .sort((a, b) => {
      const aValue = a[orderBy];
      const bValue = b[orderBy];

      // Handle null or undefined values to avoid runtime errors
      if (aValue == null) return 1;
      if (bValue == null) return -1;

      if (aValue < bValue) {
        return order === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
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
                <TableCell sx={{ width: '15%' }}>Antragsteller</TableCell>
                <TableCell sx={{ width: '20%' }} sortDirection={orderBy === 'project_title' ? order : false}>
                  <TableSortLabel
                    active={orderBy === 'project_title'}
                    direction={orderBy === 'project_title' ? order : 'asc'}
                    onClick={() => handleRequestSort('project_title')}
                  >
                    Projekttitel
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ width: '15%' }}>Abteilung/Fachschaft</TableCell>
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
                <TableCell sx={{ width: '10%' }}>Erstellt am</TableCell>
                <TableCell sx={{ width: '10%' }}>Abgeschlossen am</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedAndFilteredApplications.length > 0 ? (
                sortedAndFilteredApplications.map((app) => (
                  <Row key={app.id} application={app} />
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} align="center">
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
