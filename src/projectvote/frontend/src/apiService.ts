import axios from 'axios';

// Create an axios instance with a base URL
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- TypeScript Interfaces ---

export enum VoteOption {
  APPROVE = 'approve',
  REJECT = 'reject',
  ABSTAIN = 'abstain',
}

export enum ApplicationStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export interface ApplicationCreate {
  first_name: string;
  last_name: string;
  applicant_email: string;
  department: string;
  project_title: string;
  project_description: string;
  costs: number;
}

export interface VoteCreate {
  decision: VoteOption;
}

export interface VoteOut {
  voter_email: string;
  decision: VoteOption | null;
}

export interface AttachmentOut {
  id: number;
  filename: string;
}

export interface ApplicationOut {
  id: number;
  first_name: string;
  last_name: string;
  applicant_email: string;
  department: string;
  project_title: string;
  project_description: string;
  costs: number;
  status: ApplicationStatus;
  votes: VoteOut[];
  attachments: AttachmentOut[];
}

export interface VoteDetails {
    voter_email: string;
    application: {
        id: number;
        project_title: string;
        project_description: string;
        costs: number;
        department: string;
        attachments: AttachmentOut[];
    };
    vote_options: VoteOption[];
}


// --- API Service Functions ---

/**
 * Fetches the archive of all applications.
 * @returns A list of all applications.
 */
export const getApplicationsArchive = async (): Promise<ApplicationOut[]> => {
  try {
    const response = await apiClient.get('/applications/archive');
    return response.data;
  } catch (error) {
    console.error('Error fetching applications archive:', error);
    throw error;
  }
};


/**
 * Submits a new application to the backend.
 * @param applicationData - The data for the new application.
 * @param file - Optional file attachment.
 * @returns The response from the server.
 */
export const submitApplication = async (
  applicationData: ApplicationCreate,
  file: File | null = null
) => {
  try {
    // Create FormData to support file uploads
    const formData = new FormData();
    
    // Append all application fields to FormData
    formData.append('first_name', applicationData.first_name);
    formData.append('last_name', applicationData.last_name);
    formData.append('applicant_email', applicationData.applicant_email);
    formData.append('department', applicationData.department);
    formData.append('project_title', applicationData.project_title);
    formData.append('project_description', applicationData.project_description);
    formData.append('costs', applicationData.costs.toString());
    
    // Append file if provided
    if (file) {
      formData.append('attachment', file);
    }
    
    const response = await apiClient.post('/applications', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting application:', error);
    throw error;
  }
};

/**
 * Fetches the details for a specific vote using a token.
 * @param token - The unique token for the vote.
 * @returns The vote details.
 */
export const getVoteDetails = async (token: string): Promise<VoteDetails> => {
  try {
    const response = await apiClient.get(`/vote/${token}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching vote details:', error);
    throw error;
  }
};

/**
 * Casts a vote for an application.
 * @param token - The unique token for the vote.
 * @param voteData - The decision of the vote.
 * @returns The response from the server.
 */
export const castVote = async (token: string, voteData: VoteCreate) => {
  try {
    const response = await apiClient.post(`/vote/${token}`, voteData);
    return response.data;
  } catch (error) {
    console.error('Error casting vote:', error);
    throw error;
  }
};

/**
 * Gets the download URL for an attachment.
 * @param token - The vote token.
 * @param attachmentId - The attachment ID.
 * @returns The download URL.
 */
export const getAttachmentUrl = (token: string, attachmentId: number): string => {
  return `/api/vote/${token}/attachments/${attachmentId}`;
};

/**
 * Gets the download URL for an attachment (public archive access).
 * @param attachmentId - The attachment ID.
 * @returns The download URL.
 */
export const getPublicAttachmentUrl = (attachmentId: number): string => {
  return `/api/attachments/${attachmentId}`;
};
