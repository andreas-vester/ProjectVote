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
  FormHelperText,
} from '@mui/material';
import { AttachFile, Close } from '@mui/icons-material';
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

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string>('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  } | null>(null);

  // File validation constants
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_FILE_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX
    'application/msword', // DOC
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // XLSX
    'application/vnd.ms-excel', // XLS
  ];
  const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx'];

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

  const validateFile = (file: File): string => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return 'Die Dateigröße darf 10 MB nicht überschreiten';
    }

    // Check file extension
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
      return 'Nur PDF, DOC, DOCX, XLS und XLSX Dateien sind erlaubt';
    }

    // Check MIME type
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      return 'Ungültiger Dateityp';
    }

    return '';
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const error = validateFile(file);
      if (error) {
        setFileError(error);
        setSelectedFile(null);
        e.target.value = ''; // Reset input
      } else {
        setFileError('');
        setSelectedFile(file);
      }
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setFileError('');
    // Reset file input
    const fileInput = document.getElementById('attachment-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
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

      const response = await submitApplication(applicationData, selectedFile);

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
      handleRemoveFile();
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
            <Grid>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Anhang (optional)
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<AttachFile />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
                >
                  {selectedFile ? 'Datei ändern' : 'Datei auswählen'}
                  <input
                    type="file"
                    id="attachment-input"
                    hidden
                    accept=".pdf,.doc,.docx,.xls,.xlsx"
                    onChange={handleFileChange}
                  />
                </Button>
                {selectedFile && (
                  <Box
                    sx={{
                      mt: 1,
                      p: 1,
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      backgroundColor: '#f5f5f5',
                    }}
                  >
                    <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                      {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </Typography>
                    <Button
                      size="small"
                      onClick={handleRemoveFile}
                      startIcon={<Close />}
                      sx={{ minWidth: 'auto' }}
                    >
                      Entfernen
                    </Button>
                  </Box>
                )}
                {fileError && (
                  <FormHelperText error>{fileError}</FormHelperText>
                )}
                <FormHelperText>
                  Erlaubte Formate: PDF, DOC, DOCX, XLS, XLSX (max. 10 MB)
                </FormHelperText>
              </Box>
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
