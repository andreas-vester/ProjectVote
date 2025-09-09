import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  Snackbar,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import { submitApplication, type ApplicationCreate } from '../apiService';

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    applicant_email: '',
    department: '',
    project_title: '',
    project_description: '',
    costs: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  } | null>(null);

  const validate = (name: string, value: string) => {
    let error = '';
    if (!value) {
      error = 'Dieses Feld ist ein Pflichtfeld';
    } else if (name === 'applicant_email' && !/\S+@\S+\.\S+/.test(value)) {
      error = 'Ungültige E-Mail-Adresse';
    } else if (name === 'costs' && parseFloat(value) <= 0) {
      error = 'Die Kosten müssen eine positive Zahl sein';
    }
    return error;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
    const error = validate(name, value);
    setErrors((prevErrors) => ({
      ...prevErrors,
      [name]: error,
    }));
  };

  const handleCloseSnackbar = () => {
    setSnackbar(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);

    const newErrors: Record<string, string> = {};
    Object.entries(formData).forEach(([key, value]) => {
      const error = validate(key, value);
      if (error) {
        newErrors[key] = error;
      }
    });

    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      setIsSubmitting(false);
      return;
    }

    try {
      const applicationData: ApplicationCreate = {
        ...formData,
        costs: parseFloat(formData.costs) || 0,
      };

      const response = await submitApplication(applicationData);

      setSnackbar({
        open: true,
        message: 'Antrag erfolgreich eingereicht!',
        severity: 'success',
      });
      console.log(response);
      // Clear the form
      setFormData({
        first_name: '',
        last_name: '',
        applicant_email: '',
        department: '',
        project_title: '',
        project_description: '',
        costs: '',
      });
    } catch (error) {
      console.error('Fehler beim Einreichen des Antrags:', error);
      setSnackbar({
        open: true,
        message: 'Fehler beim Einreichen des Antrags. Bitte die Konsole prüfen.',
        severity: 'error',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Neuer Förderantrag
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <Grid container spacing={2}>
            <Grid>
              <TextField
                name="first_name"
                required
                fullWidth
                id="first_name"
                label="Vorname"
                autoFocus
                value={formData.first_name}
                onChange={handleChange}
                error={!!errors.first_name}
                helperText={errors.first_name}
              />
            </Grid>
            <Grid>
              <TextField
                required
                fullWidth
                id="last_name"
                label="Nachname"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                error={!!errors.last_name}
                helperText={errors.last_name}
              />
            </Grid>
            <Grid>
              <TextField
                required
                fullWidth
                id="applicant_email"
                label="E-Mail-Adresse"
                name="applicant_email"
                type="email"
                value={formData.applicant_email}
                onChange={handleChange}
                error={!!errors.applicant_email}
                helperText={errors.applicant_email}
              />
            </Grid>
            <Grid>
              <TextField
                required
                fullWidth
                id="department"
                label="Abteilung/Fachschaft"
                name="department"
                value={formData.department}
                onChange={handleChange}
                error={!!errors.department}
                helperText={errors.department}
              />
            </Grid>
            <Grid>
              <TextField
                required
                fullWidth
                id="project_title"
                label="Projekttitel"
                name="project_title"
                value={formData.project_title}
                onChange={handleChange}
                error={!!errors.project_title}
                helperText={errors.project_title}
              />
            </Grid>
            <Grid>
              <TextField
                required
                fullWidth
                name="project_description"
                label="Projektbeschreibung"
                id="project_description"
                multiline
                rows={4}
                value={formData.project_description}
                onChange={handleChange}
                error={!!errors.project_description}
                helperText={errors.project_description}
              />
            </Grid>
            <Grid>
              <TextField
                required
                fullWidth
                name="costs"
                label="Geschätzte Kosten (€)"
                type="number"
                id="costs"
                value={formData.costs}
                onChange={handleChange}
                error={!!errors.costs}
                helperText={errors.costs}
              />
            </Grid>
          </Grid>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Antrag einreichen'}
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

export default ApplicationForm;
