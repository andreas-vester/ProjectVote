import React, { useState } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
} from '@mui/material';
import Grid from '@mui/material/Grid';

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8001/applications', {
        ...formData,
        costs: parseFloat(formData.costs) || 0,
      });
      alert('Application submitted successfully!');
      console.log(response.data);
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
      console.error('Error submitting application:', error);
      alert('Failed to submit application. Please check the console for details.');
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          New Funding Application
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <Grid container spacing={2}>
            <Grid xs={12} sm={6}>
              <TextField
                name="first_name"
                required
                fullWidth
                id="first_name"
                label="First Name"
                autoFocus
                value={formData.first_name}
                onChange={handleChange}
              />
            </Grid>
            <Grid xs={12} sm={6}>
              <TextField
                required
                fullWidth
                id="last_name"
                label="Last Name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                id="applicant_email"
                label="Email Address"
                name="applicant_email"
                type="email"
                value={formData.applicant_email}
                onChange={handleChange}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                id="department"
                label="Department"
                name="department"
                value={formData.department}
                onChange={handleChange}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                id="project_title"
                label="Project Title"
                name="project_title"
                value={formData.project_title}
                onChange={handleChange}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                name="project_description"
                label="Project Description"
                id="project_description"
                multiline
                rows={4}
                value={formData.project_description}
                onChange={handleChange}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                name="costs"
                label="Estimated Costs (€)"
                type="number"
                id="costs"
                value={formData.costs}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Submit Application
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default ApplicationForm;