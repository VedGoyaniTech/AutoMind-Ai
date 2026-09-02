import api from './client';
import { AdminStats, IngestionJob } from '../types/ingestion';

export const getAdminStats = async (): Promise<AdminStats> => {
  const res = await api.get('/admin/stats');
  return res.data;
};

export const getIngestionJobs = async (): Promise<IngestionJob[]> => {
  const res = await api.get('/admin/ingestion');
  return res.data;
};

export const uploadDataset = async (source_name: string, file: File): Promise<IngestionJob> => {
  const formData = new FormData();
  formData.append('source_name', source_name);
  formData.append('file', file);

  const res = await api.post('/admin/ingestion/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};
