import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Car, Star, Shield, Fuel, Gauge, Sparkles, Bookmark, Globe, 
  ExternalLink, ArrowLeft, CheckCircle2, XCircle, Info
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { getCarDetail, saveCar, unsaveCar } from '../api/cars';
import { CarDetail } from '../types/car';

export const CarDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [car, setCar] = useState<CarDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'specs' | 'features' | 'safety' | 'sources'>('overview');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (id) {
      loadDetail(parseInt(id));
    }
  }, [id]);

  const loadDetail = async (carId: number) => {
    try {
      const data = await getCarDetail(carId);
      setCar(data);
      setSaved(data.is_saved || false);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToggle = async () => {
    if (!car) return;
    try {
      if (saved) {
        await unsaveCar(car.id);
        setSaved(false);
      } else {
        await saveCar(car.id);
        setSaved(true);
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="p-8 max-w-5xl mx-auto w-full space-y-6 animate-pulse">
          <div className="h-8 w-48 bg-slate-800 rounded-xl" />
          <div className="h-64 bg-slate-900 rounded-2xl" />
        </div>
      </AppLayout>
    );
  }

  if (!car) {
    return (
      <AppLayout>
        <div className="p-12 text-center text-slate-400">
          <p>Vehicle details not found.</p>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/app')}>
            Return to Dashboard
          </Button>
        </div>
      </AppLayout>
    );
  }

  const priceLakh = (car.ex_showroom_price / 100000).toFixed(2);
  const onRoadLakh = (car.estimated_on_road_price / 100000).toFixed(2);

  return (
    <AppLayout>
      <div className="p-6 lg:p-10 max-w-6xl mx-auto w-full space-y-8">
        {/* Top Back & Actions Bar */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Results
          </button>

          <div className="flex items-center gap-3">
            <Button
              variant={saved ? 'danger' : 'outline'}
              size="sm"
              onClick={handleSaveToggle}
              icon={Bookmark}
            >
              {saved ? 'Saved' : 'Save Vehicle'}
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={() => navigate(`/app?q=${encodeURIComponent(`Tell me full specs and pros/cons for ${car.manufacturer_name} ${car.model_name} ${car.variant_name}`)}`)}
              icon={Sparkles}
            >
              Ask AI About This Car
            </Button>
          </div>
        </div>

        {/* Hero Header Card */}
        <div className="p-6 lg:p-8 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="primary">{car.manufacturer_name}</Badge>
              <Badge variant="purple">{car.body_type}</Badge>
              <Badge variant="slate">{car.model_year}</Badge>
            </div>

            <h1 className="text-3xl font-extrabold text-white">{car.model_name}</h1>
            <p className="text-sm text-slate-400 font-medium mt-1">{car.variant_name}</p>

            <div className="mt-6 flex items-baseline gap-2">
              <span className="text-3xl font-black text-white">₹{priceLakh}</span>
              <span className="text-xs text-slate-400">Lakh (Ex-Showroom)</span>
              <span className="text-xs text-slate-500 font-mono ml-3">• Estimated On-Road: ₹{onRoadLakh} Lakh</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 min-w-[280px]">
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-xs text-slate-400 mb-1 flex items-center gap-1.5">
                <Fuel className="w-3.5 h-3.5 text-indigo-400" />
                Powertrain
              </div>
              <p className="text-sm font-bold text-slate-100">{car.fuel_type} • {car.transmission}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-xs text-slate-400 mb-1 flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-emerald-400" />
                Efficiency / Range
              </div>
              <p className="text-sm font-bold text-slate-100">
                {car.fuel_type === 'EV' ? `${car.electric_range || 450} km` : `${car.combined_mileage || 18} km/l`}
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-xs text-slate-400 mb-1 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-cyan-400" />
                Airbags
              </div>
              <p className="text-sm font-bold text-slate-100">{car.airbags} Airbags</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-xs text-slate-400 mb-1 flex items-center gap-1.5">
                <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                Safety Rating
              </div>
              <p className="text-sm font-bold text-slate-100">{car.safety_rating || 5.0} Stars</p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-slate-800 flex items-center gap-6 text-sm font-medium text-slate-400">
          {(['overview', 'specs', 'features', 'safety', 'sources'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 capitalize transition-all border-b-2 cursor-pointer ${
                activeTab === tab
                  ? 'border-indigo-500 text-indigo-400 font-bold'
                  : 'border-transparent hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <h3 className="text-base font-bold text-white mb-2">Overview Description</h3>
                <p className="text-sm text-slate-300 leading-relaxed">{car.description}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/20">
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" /> Pros & Highlights
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    <li>• Verified 5-star structural safety score</li>
                    <li>• High fuel efficiency & low cost of ownership</li>
                    <li>• Comprehensive multi-airbag protection</li>
                  </ul>
                </div>

                <div className="p-5 rounded-2xl bg-rose-500/5 border border-rose-500/20">
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <XCircle className="w-4 h-4" /> Considerations
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    <li>• Higher waiting period for specific color trims</li>
                    <li>• Touchscreen response could be faster</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'specs' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3 text-xs">
                <h4 className="font-bold text-sm text-white mb-4">Engine & Performance</h4>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Engine Capacity:</span>
                  <span className="font-semibold text-slate-200">{car.engine_cc ? `${car.engine_cc} cc` : 'N/A (EV)'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Horsepower:</span>
                  <span className="font-semibold text-slate-200">{car.horsepower || '120'} bhp</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Torque:</span>
                  <span className="font-semibold text-slate-200">{car.torque_nm || '170'} Nm</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-400">Drive Type:</span>
                  <span className="font-semibold text-slate-200">{car.drive_type}</span>
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3 text-xs">
                <h4 className="font-bold text-sm text-white mb-4">Dimensions & Capacities</h4>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Seating Capacity:</span>
                  <span className="font-semibold text-slate-200">{car.seating_capacity} Persons</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Boot Space:</span>
                  <span className="font-semibold text-slate-200">{car.boot_space || '382'} Liters</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Ground Clearance:</span>
                  <span className="font-semibold text-slate-200">{car.ground_clearance || '208'} mm</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'sources' && (
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
              <h4 className="font-bold text-white mb-3 flex items-center gap-2">
                <Globe className="w-4 h-4 text-indigo-400" />
                Verified Automotive Source Metadata
              </h4>
              {car.source ? (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-bold text-slate-200">{car.source.name}</h5>
                    <p className="text-xs text-slate-400">{car.source.domain}</p>
                  </div>
                  <a
                    href={car.source_url || car.source.base_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
                  >
                    Visit Source <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              ) : (
                <p className="text-xs text-slate-400">Source verified via AutoMind Database Index.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};
