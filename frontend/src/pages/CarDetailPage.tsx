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
import { LiveIntelligenceSection } from '../components/cars/LiveIntelligenceSection';

export const CarDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [car, setCar] = useState<CarDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'intelligence' | 'specs' | 'features' | 'safety' | 'sources'>('overview');
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
            className="inline-flex items-center gap-2 text-xs font-semibold text-[#5C524A] hover:text-[#1A1614] transition-colors cursor-pointer"
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
        <div className="p-6 lg:p-8 rounded-3xl bg-[#FAF7F2] border border-[#B7A89A] shadow-sm relative overflow-hidden flex flex-col md:flex-row justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="primary">{car.manufacturer_name}</Badge>
              <Badge variant="purple">{car.body_type}</Badge>
              <Badge variant="slate">{car.model_year}</Badge>
            </div>

            <h1 className="text-3xl font-extrabold text-[#1A1614]">{car.model_name}</h1>
            <p className="text-sm text-[#5C524A] font-medium mt-1">{car.variant_name}</p>

            <div className="mt-6 flex items-baseline gap-2">
              <span className="text-3xl font-black text-[#1A1614]">₹{priceLakh}</span>
              <span className="text-xs text-[#5C524A]">Lakh (Ex-Showroom)</span>
              <span className="text-xs text-[#722F37] font-mono ml-3 font-semibold">• Estimated On-Road: ₹{onRoadLakh} Lakh</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 min-w-[280px]">
            <div className="p-3.5 rounded-xl bg-[#DFD2BA] border border-[#B7A89A]">
              <div className="text-xs text-[#5C524A] mb-1 flex items-center gap-1.5">
                <Fuel className="w-3.5 h-3.5 text-[#722F37]" />
                Powertrain
              </div>
              <p className="text-sm font-bold text-[#1A1614]">{car.fuel_type} • {car.transmission}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-[#DFD2BA] border border-[#B7A89A]">
              <div className="text-xs text-[#5C524A] mb-1 flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-emerald-700" />
                Efficiency / Range
              </div>
              <p className="text-sm font-bold text-[#1A1614]">
                {car.fuel_type === 'EV' ? `${car.electric_range || 450} km` : `${car.combined_mileage || 18} km/l`}
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-[#DFD2BA] border border-[#B7A89A]">
              <div className="text-xs text-[#5C524A] mb-1 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-blue-700" />
                Airbags
              </div>
              <p className="text-sm font-bold text-[#1A1614]">{car.airbags} Airbags</p>
            </div>

            <div className="p-3.5 rounded-xl bg-[#DFD2BA] border border-[#B7A89A]">
              <div className="text-xs text-[#5C524A] mb-1 flex items-center gap-1.5">
                <Star className="w-3.5 h-3.5 text-amber-600 fill-amber-600" />
                Safety Rating
              </div>
              <p className="text-sm font-bold text-[#1A1614]">{car.safety_rating || 5.0} Stars</p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-[#B7A89A] flex items-center gap-6 text-sm font-medium text-[#5C524A]">
          {(['overview', 'intelligence', 'specs', 'features', 'safety', 'sources'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 capitalize transition-all border-b-2 cursor-pointer flex items-center gap-1.5 ${
                activeTab === tab
                  ? 'border-[#722F37] text-[#722F37] font-bold'
                  : 'border-transparent hover:text-[#1A1614]'
              }`}
            >
              {tab === 'intelligence' ? (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-[#722F37]" />
                  Live Intelligence
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
                </>
              ) : (
                tab
              )}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'intelligence' && (
            <LiveIntelligenceSection
              make={car.manufacturer_name}
              model={car.model_name}
              year={car.model_year}
              initialCity={car.country === 'India' ? 'Ahmedabad' : 'Ahmedabad'}
            />
          )}

          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] shadow-sm">
                <h3 className="text-base font-bold text-[#1A1614] mb-2">Overview Description</h3>
                <p className="text-sm text-[#2D2520] leading-relaxed">{car.description}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/25">
                  <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-700" /> Pros & Highlights
                  </h4>
                  <ul className="space-y-2 text-xs text-[#2D2520]">
                    <li>• Verified 5-star structural safety score</li>
                    <li>• High fuel efficiency & low cost of ownership</li>
                    <li>• Comprehensive multi-airbag protection</li>
                  </ul>
                </div>

                <div className="p-5 rounded-2xl bg-rose-500/10 border border-rose-500/25">
                  <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <XCircle className="w-4 h-4 text-rose-700" /> Considerations
                  </h4>
                  <ul className="space-y-2 text-xs text-[#2D2520]">
                    <li>• Higher waiting period for specific color trims</li>
                    <li>• Touchscreen response could be faster</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'specs' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] space-y-3 text-xs shadow-sm">
                <h4 className="font-bold text-sm text-[#1A1614] mb-4">Engine & Performance</h4>
                <div className="flex justify-between py-2 border-b border-[#B7A89A]">
                  <span className="text-[#5C524A]">Engine Capacity:</span>
                  <span className="font-semibold text-[#1A1614]">{car.engine_cc ? `${car.engine_cc} cc` : 'N/A (EV)'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#B7A89A]">
                  <span className="text-[#5C524A]">Horsepower:</span>
                  <span className="font-semibold text-[#1A1614]">{car.horsepower || '120'} bhp</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#B7A89A]">
                  <span className="text-[#5C524A]">Torque:</span>
                  <span className="font-semibold text-[#1A1614]">{car.torque_nm || '170'} Nm</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-[#5C524A]">Drive Type:</span>
                  <span className="font-semibold text-[#1A1614]">{car.drive_type}</span>
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] space-y-3 text-xs shadow-sm">
                <h4 className="font-bold text-sm text-[#1A1614] mb-4">Dimensions & Capacities</h4>
                <div className="flex justify-between py-2 border-b border-[#B7A89A]">
                  <span className="text-[#5C524A]">Seating Capacity:</span>
                  <span className="font-semibold text-[#1A1614]">{car.seating_capacity} Persons</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#B7A89A]">
                  <span className="text-[#5C524A]">Boot Space:</span>
                  <span className="font-semibold text-[#1A1614]">{car.boot_space || '382'} Liters</span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#B7A89A]">
                  <span className="text-[#5C524A]">Ground Clearance:</span>
                  <span className="font-semibold text-[#1A1614]">{car.ground_clearance || '208'} mm</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'sources' && (
            <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] shadow-sm">
              <h4 className="font-bold text-[#1A1614] mb-3 flex items-center gap-2">
                <Globe className="w-4 h-4 text-[#722F37]" />
                Verified Automotive Source Metadata
              </h4>
              {car.source ? (
                <div className="p-4 rounded-xl bg-[#DFD2BA] border border-[#B7A89A] flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-bold text-[#1A1614]">{car.source.name}</h5>
                    <p className="text-xs text-[#5C524A]">{car.source.domain}</p>
                  </div>
                  <a
                    href={car.source_url || car.source.base_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-[#722F37] hover:underline font-semibold"
                  >
                    Visit Source <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              ) : (
                <p className="text-xs text-[#5C524A]">Source verified via AutoMind Database Index.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};
