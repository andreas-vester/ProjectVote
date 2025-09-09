import axios from 'axios';

// Create an axios instance with a base URL
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
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
}

export interface VoteDetails {
    voter_email: string;
    application: {
        id: number;
        project_title: string;
        project_description: string;
        costs: number;
        department: string;
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
 * @returns The response from the server.
 */
export const submitApplication = async (applicationData: ApplicationCreate) => {
  try {
    const response = await apiClient.post('/applications', applicationData);
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
