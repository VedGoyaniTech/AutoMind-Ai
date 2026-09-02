import api from './client';
import { CarDetail, CarSearchFilterParams, CarVariantSummary } from '../types/car';

export const searchCars = async (params: CarSearchFilterParams) => {
  const res = await api.get('/cars', { params });
  return res.data;
};

export const getCarDetail = async (id: number): Promise<CarDetail> => {
  const res = await api.get(`/cars/${id}`);
  return res.data;
};

export const compareCars = async (variant_ids: number[]): Promise<CarDetail[]> => {
  const res = await api.post('/cars/compare', { variant_ids });
  return res.data;
};

export const getSavedCars = async (): Promise<CarVariantSummary[]> => {
  const res = await api.get('/saved');
  return res.data;
};

export const saveCar = async (variant_id: number) => {
  const res = await api.post(`/saved/${variant_id}`);
  return res.data;
};

export const unsaveCar = async (variant_id: number) => {
  const res = await api.delete(`/saved/${variant_id}`);
  return res.data;
};
