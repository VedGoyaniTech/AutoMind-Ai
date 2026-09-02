export interface UserPreference {
  id: number;
  answer_detail: 'Concise' | 'Balanced' | 'Detailed';
  units: 'Metric' | 'Imperial';
  currency: string;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  is_admin: boolean;
  preference?: UserPreference;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  access_token: string;
  token_type: string;
  user: User;
}
