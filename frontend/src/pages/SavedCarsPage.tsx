import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Sparkles, Car } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { CarCardComponent } from '../components/ai/CarCard';
import { getSavedCars } from '../api/cars';
import { CarVariantSummary } from '../types/car';

export const SavedCarsPage: React.FC = () => {
  const navigate = useNavigate();
  const [savedCars, setSavedCars] = useState<CarVariantSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSaved = async () => {
    try {
      const data = await getSavedCars();
      setSavedCars(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSaved();
  }, []);

  const handleSaveToggle = (variantId: number, isSaved: boolean) => {
    if (!isSaved) {
      setSavedCars((prev) => prev.filter((c) => c.id !== variantId));
    }
  };

  return (
    <AppLayout>
      <div className="p-6 lg:p-10 max-w-7xl mx-auto w-full space-y-8">
        <div className="border-b border-slate-800 pb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2.5">
            <Bookmark className="w-7 h-7 text-indigo-400" />
            Bookmarked Vehicles
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Access your saved vehicles for quick comparison or AI research sessions.
          </p>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading saved vehicles...</div>
        ) : savedCars.length === 0 ? (
          <div className="p-12 text-center text-slate-400 border border-slate-800 rounded-2xl bg-slate-900/40">
            <Car className="w-10 h-10 mx-auto text-slate-600 mb-3" />
            <p className="text-base font-semibold text-slate-300">No saved cars yet</p>
            <p className="text-xs text-slate-500 mt-1">Bookmark vehicles from research sessions to view them here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedCars.map((car) => (
              <CarCardComponent
                key={car.id}
                car={car}
                onAskAI={(carName) => navigate(`/app?q=${encodeURIComponent(`Tell me full specs for ${carName}`)}`)}
                onSaveToggle={handleSaveToggle}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
};
