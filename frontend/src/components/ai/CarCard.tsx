import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Shield, Fuel, Gauge, Sparkles, Bookmark, ArrowRight } from 'lucide-react';
import { CarVariantSummary } from '../../types/car';
import { saveCar, unsaveCar } from '../../api/cars';

interface CarCardProps {
  car: CarVariantSummary;
  onAskAI?: (carName: string) => void;
  onSaveToggle?: (carId: number, isSaved: boolean) => void;
}

export const CarCardComponent: React.FC<CarCardProps> = ({ car, onAskAI, onSaveToggle }) => {
  const navigate = useNavigate();
  const [saved, setSaved] = React.useState(car.is_saved || false);
  const [saving, setSaving] = React.useState(false);

  const priceLakh = (car.ex_showroom_price / 100000).toFixed(2);

  const handleBookmark = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setSaving(true);
    try {
      if (saved) {
        await unsaveCar(car.id);
        setSaved(false);
        if (onSaveToggle) onSaveToggle(car.id, false);
      } else {
        await saveCar(car.id);
        setSaved(true);
        if (onSaveToggle) onSaveToggle(car.id, true);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="group rounded-xl transition-all duration-200 overflow-hidden flex flex-col justify-between shadow-sm hover:shadow-md"
      style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
    >
      {/* Header & Badges */}
      <div className="p-4 relative" style={{ borderBottom: '1px solid #E2DDD6' }}>
        <button
          onClick={handleBookmark}
          disabled={saving}
          className="absolute top-3.5 right-3.5 p-1.5 rounded-lg transition-all"
          style={{
            background: saved ? '#FEF2F2' : '#F7F4ED',
            color: saved ? '#EF4444' : '#6B6560',
            border: '1px solid #E2DDD6'
          }}
          title={saved ? 'Remove from Saved' : 'Save Car'}
        >
          <Bookmark className={`w-3.5 h-3.5 ${saved ? 'fill-red-500' : ''}`} />
        </button>

        <div className="flex items-center gap-2 mb-1">
          <span className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#C96A2B' }}>
            {car.manufacturer_name}
          </span>
          <span className="text-xs" style={{ color: '#9C9590' }}>•</span>
          <span className="text-xs font-medium" style={{ color: '#6B6560' }}>{car.body_type}</span>
        </div>

        <h4 className="text-sm font-bold line-clamp-1 pr-8" style={{ color: '#0D0D0D' }}>
          {car.model_name}
        </h4>
        <p className="text-xs line-clamp-1 mt-0.5" style={{ color: '#6B6560' }}>{car.variant_name}</p>
      </div>

      {/* Pricing & Key Specifications Grid */}
      <div className="p-4 space-y-3">
        <div className="flex items-baseline gap-1.5">
          <span className="text-lg font-bold" style={{ color: '#0D0D0D' }}>₹{priceLakh}</span>
          <span className="text-xs" style={{ color: '#6B6560' }}>Lakh (Ex-Showroom)</span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-1.5 p-2 rounded-lg" style={{ background: '#F7F4ED', border: '1px solid #E2DDD6', color: '#0D0D0D' }}>
            <Fuel className="w-3.5 h-3.5" style={{ color: '#C96A2B' }} />
            <span className="truncate">{car.fuel_type} • {car.transmission}</span>
          </div>

          <div className="flex items-center gap-1.5 p-2 rounded-lg" style={{ background: '#F7F4ED', border: '1px solid #E2DDD6', color: '#0D0D0D' }}>
            <Gauge className="w-3.5 h-3.5 text-emerald-600" />
            <span className="truncate">
              {car.fuel_type === 'EV' ? `${car.electric_range || 400} km range` : `${car.combined_mileage || 18} km/l`}
            </span>
          </div>

          <div className="flex items-center gap-1.5 p-2 rounded-lg" style={{ background: '#F7F4ED', border: '1px solid #E2DDD6', color: '#0D0D0D' }}>
            <Shield className="w-3.5 h-3.5 text-blue-600" />
            <span>{car.airbags} Airbags</span>
          </div>

          <div className="flex items-center gap-1.5 p-2 rounded-lg" style={{ background: '#F7F4ED', border: '1px solid #E2DDD6', color: '#0D0D0D' }}>
            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
            <span>{car.safety_rating || 5.0} Star Safety</span>
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-3 flex items-center justify-between gap-2" style={{ background: '#F7F4ED', borderTop: '1px solid #E2DDD6' }}>
        <button
          onClick={() => navigate(`/cars/${car.id}`)}
          className="text-xs font-medium flex items-center gap-1 hover:underline"
          style={{ color: '#6B6560' }}
        >
          View Specs
          <ArrowRight className="w-3 h-3" />
        </button>

        {onAskAI && (
          <button
            onClick={() => onAskAI(`${car.manufacturer_name} ${car.model_name} ${car.variant_name}`)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-colors"
            style={{ background: '#C96A2B', color: '#FFFFFF' }}
          >
            <Sparkles className="w-3 h-3" />
            Ask AI
          </button>
        )}
      </div>
    </div>
  );
};
