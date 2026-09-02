import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scale, Sparkles, Plus, Trash2, CheckCircle2, Shield, Fuel, Gauge, Star } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { Button } from '../components/ui/Button';
import { compareCars, searchCars } from '../api/cars';
import { CarDetail, CarVariantSummary } from '../types/car';

export const ComparePage: React.FC = () => {
  const navigate = useNavigate();

  const [selectedIds, setSelectedIds] = useState<number[]>([1, 3]); // Initial demo IDs (Tata Nexon & Creta)
  const [comparedCars, setComparedCars] = useState<CarDetail[]>([]);
  const [availableCars, setAvailableCars] = useState<CarVariantSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    loadComparison();
    loadAvailableCars();
  }, [selectedIds]);

  const loadComparison = async () => {
    if (selectedIds.length === 0) {
      setComparedCars([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await compareCars(selectedIds);
      setComparedCars(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableCars = async () => {
    try {
      const res = await searchCars({ page_size: 20 });
      setAvailableCars(res.items);
    } catch (e) {
      console.error(e);
    }
  };

  const removeCar = (id: number) => {
    setSelectedIds((prev) => prev.filter((i) => i !== id));
  };

  const addCar = (id: number) => {
    if (selectedIds.length >= 4 || selectedIds.includes(id)) return;
    setSelectedIds((prev) => [...prev, id]);
    setAdding(false);
  };

  const handleAskAIWhichToBuy = () => {
    const carNames = comparedCars.map((c) => `${c.manufacturer_name} ${c.model_name}`).join(' vs ');
    navigate(`/app?q=${encodeURIComponent(`Which one should I buy between ${carNames}? Explain pros and cons.`)}`);
  };

  return (
    <AppLayout>
      <div className="p-6 lg:p-10 max-w-7xl mx-auto w-full space-y-8">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2">
              <Scale className="w-7 h-7 text-indigo-400" />
              Multi-Vehicle Comparison Matrix
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Compare up to 4 vehicles side-by-side across pricing, powertrain specs, mileage, and safety features.
            </p>
          </div>

          {comparedCars.length > 0 && (
            <Button
              variant="primary"
              size="md"
              onClick={handleAskAIWhichToBuy}
              icon={Sparkles}
            >
              Ask AI Which One Should I Buy?
            </Button>
          )}
        </div>

        {/* Add Car Dropdown / Controls */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400 font-medium">Comparing {comparedCars.length} of 4 models</span>

          {selectedIds.length < 4 && (
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAdding(!adding)}
                icon={Plus}
              >
                Add Vehicle to Compare
              </Button>

              {adding && (
                <div className="absolute right-0 top-10 w-72 max-h-64 overflow-y-auto bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2 z-50">
                  <div className="text-[10px] font-bold text-slate-500 uppercase px-2 mb-1">Select Model:</div>
                  {availableCars.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => addCar(c.id)}
                      disabled={selectedIds.includes(c.id)}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs hover:bg-indigo-600/20 text-slate-200 disabled:opacity-40 flex items-center justify-between"
                    >
                      <span>{c.manufacturer_name} {c.model_name}</span>
                      <span className="text-[10px] text-slate-400">₹{(c.ex_showroom_price / 100000).toFixed(1)}L</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Responsive Matrix Table */}
        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading comparison metrics...</div>
        ) : comparedCars.length === 0 ? (
          <div className="p-12 text-center text-slate-400 border border-slate-800 rounded-2xl bg-slate-900/40">
            <p>No vehicles selected for comparison.</p>
            <Button variant="primary" size="sm" className="mt-4" onClick={() => setSelectedIds([1, 2])}>
              Compare Nexon vs Creta Demo
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/80 shadow-2xl">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/80">
                  <th className="p-4 w-48 text-slate-400 font-bold uppercase tracking-wider">Specifications</th>
                  {comparedCars.map((car) => (
                    <th key={car.id} className="p-4 min-w-[220px] text-slate-100 font-bold border-l border-slate-800/80 relative">
                      <button
                        onClick={() => removeCar(car.id)}
                        className="absolute top-3 right-3 text-slate-500 hover:text-rose-400 p-1"
                        title="Remove"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                      <div className="text-indigo-400 uppercase text-[10px] font-semibold">{car.manufacturer_name}</div>
                      <div className="text-base font-extrabold text-white">{car.model_name}</div>
                      <div className="text-[11px] text-slate-400 font-normal truncate">{car.variant_name}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {/* Price Row */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Price (Ex-Showroom)</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-black text-indigo-300 text-sm">
                      ₹{(car.ex_showroom_price / 100000).toFixed(2)} Lakh
                    </td>
                  ))}
                </tr>

                {/* Fuel & Transmission */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Fuel & Transmission</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-medium text-slate-200">
                      {car.fuel_type} • {car.transmission}
                    </td>
                  ))}
                </tr>

                {/* Engine Power */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Horsepower</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-medium text-slate-200">
                      {car.horsepower || '120'} bhp
                    </td>
                  ))}
                </tr>

                {/* Mileage / EV Range */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Mileage / Range</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-bold text-emerald-400">
                      {car.fuel_type === 'EV' ? `${car.electric_range || 450} km Range` : `${car.combined_mileage || 18} km/l`}
                    </td>
                  ))}
                </tr>

                {/* Airbags */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Airbags</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-medium text-slate-200">
                      {car.airbags} Airbags
                    </td>
                  ))}
                </tr>

                {/* Safety Rating */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">GNCAP Safety Rating</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-bold text-amber-400">
                      {car.safety_rating || 5.0} Stars
                    </td>
                  ))}
                </tr>

                {/* Seating Capacity */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Seating Capacity</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-medium text-slate-200">
                      {car.seating_capacity} Seats
                    </td>
                  ))}
                </tr>

                {/* Boot Space */}
                <tr>
                  <td className="p-4 font-bold text-slate-300 bg-slate-950/40">Boot Capacity</td>
                  {comparedCars.map((car) => (
                    <td key={car.id} className="p-4 border-l border-slate-800/80 font-medium text-slate-200">
                      {car.boot_space || 382} Liters
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
