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
        <div className="border-b border-[#B7A89A] pb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1A1614] flex items-center gap-2.5">
            <Bookmark className="w-7 h-7 text-[#722F37]" />
            Bookmarked Vehicles
          </h1>
          <p className="text-xs sm:text-sm text-[#5C524A] mt-1">
            Access your saved vehicles for quick comparison or AI research sessions.
          </p>
        </div>

        {loading ? (
          <div className="p-12 text-center text-[#5C524A]">Loading saved vehicles...</div>
        ) : savedCars.length === 0 ? (
          <div className="p-12 text-center text-[#5C524A] border border-[#B7A89A] rounded-2xl bg-[#FAF7F2]">
            <Car className="w-10 h-10 mx-auto text-[#857A70] mb-3" />
            <p className="text-base font-semibold text-[#1A1614]">No saved cars yet</p>
            <p className="text-xs text-[#5C524A] mt-1">Bookmark vehicles from research sessions to view them here.</p>
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
