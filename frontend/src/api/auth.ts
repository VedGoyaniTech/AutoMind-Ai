import api from './client';
import { User, TokenResponse, RegisterResponse } from '../types/user';

export const registerUser = async (data: { full_name: string; email: string; password: string; confirm_password?: string }): Promise<RegisterResponse> => {
  const res = await api.post<RegisterResponse>('/auth/register', data);
  return res.data;
};

export const loginUser = async (data: { email: string; password: string; remember_me?: boolean }): Promise<TokenResponse> => {
  const res = await api.post<TokenResponse>('/auth/login', data);
  return res.data;
};

export const getMe = async (): Promise<User> => {
  const res = await api.get<User>('/auth/me');
  return res.data;
};

export const updatePreferences = async (data: { answer_detail?: string; units?: string; currency?: string }) => {
  const res = await api.put('/auth/preferences', data);
  return res.data;
};
