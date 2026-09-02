export interface IngestionJob {
  id: number;
  source_name: string;
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed' | string;
  total_records: number;
  processed_records: number;
  failed_records: number;
  progress_percentage: number;
  error_log?: string;
  started_at: string;
  completed_at?: string;
}

export interface AdminStats {
  total_cars: number;
  total_models: number;
  total_manufacturers: number;
  total_sources: number;
  total_vector_docs: number;
  vector_store_type: string;
}
