import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, Upload, FileText, CheckCircle2, AlertCircle, Loader2, Cpu, BarChart3 } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { getAdminStats, getIngestionJobs, uploadDataset } from '../api/admin';
import { AdminStats, IngestionJob } from '../types/ingestion';

export const AdminIngestionPage: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [loading, setLoading] = useState(true);

  const [sourceName, setSourceName] = useState('Kaggle Auto Dataset 2026');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      const [sData, jData] = await Promise.all([getAdminStats(), getIngestionJobs()]);
      setStats(sData);
      setJobs(jData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a dataset file (.csv, .json, .jsonl).');
      return;
    }

    setUploading(true);
    setError('');

    try {
      await uploadDataset(sourceName, file);
      setFile(null);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload and ingest dataset.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-6 lg:p-10 max-w-7xl mx-auto w-full space-y-8">
        <div className="border-b border-slate-800 pb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2.5">
              <Database className="w-7 h-7 text-amber-400" />
              Automotive Dataset Ingestion & Scalability Dashboard
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Batch process, validate, normalize, and generate vector embeddings for millions of car records.
            </p>
          </div>
        </div>

        {/* System Ingestion Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Total Vehicle Variants</div>
            <div className="text-2xl font-black text-white">{stats?.total_cars || 0}</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Total Models</div>
            <div className="text-2xl font-black text-indigo-400">{stats?.total_models || 0}</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Verified Sources</div>
            <div className="text-2xl font-black text-emerald-400">{stats?.total_sources || 0}</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Indexed Vector Documents</div>
            <div className="text-2xl font-black text-amber-400">{stats?.total_vector_docs || 0}</div>
          </div>
        </div>

        {/* Upload Form Card */}
        <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-indigo-400" />
            Upload New Automotive Dataset
          </h3>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
              {error}
            </div>
          )}

          <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <Input
              label="Source Name Metadata"
              value={sourceName}
              onChange={(e) => setSourceName(e.target.value)}
              required
            />

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Dataset File (CSV, JSON, JSONL)
              </label>
              <input
                type="file"
                accept=".csv,.json,.jsonl"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
                required
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={uploading}
              icon={Upload}
            >
              Start Ingestion Pipeline
            </Button>
          </form>
        </div>

        {/* Ingestion Jobs History Table */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Recent Batch Ingestion Jobs</h3>
          <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/80 shadow-xl">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400">
                  <th className="p-4">Source Name</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Processed Records</th>
                  <th className="p-4">Progress</th>
                  <th className="p-4">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-slate-500">
                      No ingestion jobs executed yet.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.id}>
                      <td className="p-4 font-bold text-slate-200">{job.source_name}</td>
                      <td className="p-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          job.status.includes('Completed') ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="p-4 text-slate-300 font-mono">
                        {job.processed_records} / {job.total_records}
                      </td>
                      <td className="p-4">
                        <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-500" style={{ width: `${job.progress_percentage}%` }} />
                        </div>
                      </td>
                      <td className="p-4 text-slate-400 font-mono text-[11px]">
                        {new Date(job.started_at).toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
