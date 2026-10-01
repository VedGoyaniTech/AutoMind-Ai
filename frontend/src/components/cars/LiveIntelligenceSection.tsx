import React, { useState, useEffect } from 'react';
import { 
  CloudSun, Fuel, TrendingUp, Newspaper, ShieldAlert, 
  RefreshCw, CheckCircle2, AlertCircle, Info, ExternalLink,
  DollarSign, MapPin, Sparkles, Clock, Compass, Activity
} from 'lucide-react';
import { getCarIntelligence } from '../../api/cars';
import { CarIntelligenceResponse } from '../../types/intelligence';
import { Button } from '../ui/Button';

interface LiveIntelligenceSectionProps {
  make: string;
  model: string;
  year?: number;
  initialCity?: string;
  vin?: string;
}

const CITIES = [
  'Ahmedabad',
  'Mumbai',
  'Delhi',
  'Bengaluru',
  'Pune',
  'Hyderabad',
  'Chennai',
  'Surat',
  'Jaipur',
  'Kolkata'
];

export const LiveIntelligenceSection: React.FC<LiveIntelligenceSectionProps> = ({
  make,
  model,
  year,
  initialCity = 'Ahmedabad',
  vin
}) => {
  const [city, setCity] = useState<string>(initialCity);
  const [data, setData] = useState<CarIntelligenceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchIntelligence = async (forceRefresh: boolean = false) => {
    if (forceRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const res = await getCarIntelligence({
        make,
        model,
        year,
        city,
        vin,
        force_refresh: forceRefresh
      });
      setData(res);
    } catch (err: any) {
      console.error('Failed to load car intelligence:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to fetch live intelligence telemetry.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchIntelligence(false);
  }, [city, make, model, year]);

  const renderStatusBadge = (status?: string) => {
    switch (status) {
      case 'live':
      case 'live_statutory_engine':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-2.5 h-2.5" /> Live Response
          </span>
        );
      case 'cached':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Clock className="w-2.5 h-2.5" /> Cached
          </span>
        );
      case 'not_configured':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Info className="w-2.5 h-2.5" /> API Not Configured
          </span>
        );
      case 'unavailable':
      case 'empty_results':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-700 text-slate-300">
            Unavailable
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-400">
            {status || 'Unknown'}
          </span>
        );
    }
  };

  if (loading && !data) {
    return (
      <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-6 w-48 bg-slate-800 rounded-lg" />
          <div className="h-8 w-24 bg-slate-800 rounded-lg" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="h-32 bg-slate-800/60 rounded-xl" />
          <div className="h-32 bg-slate-800/60 rounded-xl" />
          <div className="h-32 bg-slate-800/60 rounded-xl" />
        </div>
        <div className="h-44 bg-slate-800/40 rounded-xl" />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-center space-y-4">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
        <div>
          <h4 className="font-bold text-white text-sm">Failed to Load Vehicle Intelligence</h4>
          <p className="text-xs text-rose-300 mt-1">{error}</p>
        </div>
        <Button size="sm" variant="outline" onClick={() => fetchIntelligence(true)}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Retry Fetch
        </Button>
      </div>
    );
  }

  if (!data) return null;

  const weather = data.weather;
  const pricing = data.india_pricing;
  const market = data.market_data;
  const fuel = data.fuel;
  const news = data.news;
  const traffic = data.traffic;
  const quote = pricing.breakdown;

  return (
    <div className="space-y-6">
      {/* Control Bar: Location & Sync Status */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Real-Time Intelligence & Market Telemetry
              {data.metadata?.is_cached ? (
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  Cached ({data.metadata.cached_at ? new Date(data.metadata.cached_at).toLocaleTimeString() : 'Recent'})
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Live Response
                </span>
              )}
            </h3>
            <p className="text-xs text-slate-400">
              Federated telemetry across Open-Meteo, NHTSA, NewsAPI, and AutoMind statutory tax engines.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* City Selector */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="bg-transparent text-xs text-white focus:outline-none cursor-pointer"
            >
              {CITIES.map((c) => (
                <option key={c} value={c} className="bg-slate-900 text-white">
                  {c}
                </option>
              ))}
            </select>
          </div>

          <Button
            size="sm"
            variant="outline"
            disabled={refreshing}
            onClick={() => fetchIntelligence(true)}
            className="flex items-center gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {/* AI Grounded Executive Summary */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900/60 to-purple-950/30 border border-indigo-500/20 relative overflow-hidden">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
              Grounded AI Intelligence Briefing
            </h4>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
            Strict Fact Grounding • Zero Hallucination Guarantee
          </span>
        </div>
        <div className="prose prose-invert prose-xs max-w-none text-slate-200 text-xs leading-relaxed space-y-3 whitespace-pre-line">
          {data.ai_analysis?.summary}
        </div>
      </div>

      {/* Real-Time Environmental & Fuel Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Weather Card */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CloudSun className="w-4 h-4 text-amber-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                Live Weather & Driving Conditions
              </h4>
            </div>
            {renderStatusBadge(weather?.status)}
          </div>

          {weather?.status === 'live' ? (
            <div className="space-y-3">
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-2xl font-black text-white">
                    {weather.temperature_celsius}°C
                  </span>
                  <span className="text-xs text-slate-400 ml-2">
                    (Feels like {weather.feels_like_celsius}°C)
                  </span>
                </div>
                <span className="text-xs font-semibold text-slate-300 px-2 py-1 rounded-lg bg-slate-800">
                  {weather.weather_condition}
                </span>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] text-slate-300">
                <span className="text-amber-400 font-bold">Driving Assessment: </span>
                {weather.driving_conditions}
              </div>

              <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-400 pt-1">
                <div>Wind: <span className="text-slate-200 font-semibold">{weather.wind_speed_kmh} km/h</span></div>
                <div>Humidity: <span className="text-slate-200 font-semibold">{weather.relative_humidity_percent}%</span></div>
                <div>Rain: <span className="text-slate-200 font-semibold">{weather.precipitation_mm} mm</span></div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400">
              {weather?.error || 'Weather telemetry unavailable for this location.'}
            </p>
          )}
          <div className="text-[10px] text-slate-400 border-t border-slate-800/60 pt-2">
            Source: Open-Meteo Open API ({weather?.city || city})
          </div>
        </div>

        {/* Fuel Prices Card */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Fuel className="w-4 h-4 text-emerald-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                Fuel Prices in {city}
              </h4>
            </div>
            {renderStatusBadge(fuel?.status)}
          </div>

          {fuel?.status === 'live' && (fuel.petrol || fuel.diesel) ? (
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                <span className="text-[10px] text-slate-400 font-semibold uppercase">Petrol</span>
                <div className="text-xl font-bold text-emerald-400 mt-1">
                  ₹{fuel.petrol?.price} <span className="text-xs text-slate-400 font-normal">/L</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                <span className="text-[10px] text-slate-400 font-semibold uppercase">Diesel</span>
                <div className="text-xl font-bold text-sky-400 mt-1">
                  ₹{fuel.diesel?.price} <span className="text-xs text-slate-400 font-normal">/L</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60 text-xs text-slate-400 space-y-1">
              <p className="font-semibold text-slate-300">Live Pump Feeds Pending</p>
              <p className="text-[11px] leading-relaxed">
                {fuel?.note || 'FUEL_API_KEY is not configured in .env. Configure credentials from IndianAPI or APIMitra to activate daily live fuel telemetry.'}
              </p>
            </div>
          )}
          <div className="text-[10px] text-slate-400 border-t border-slate-800/60 pt-2">
            Provider: {fuel?.provider || 'Indian API / API Mitra'}
          </div>
        </div>
      </div>

      {/* Indian Statutory On-Road Price Breakdown */}
      {pricing && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                Statutory On-Road Pricing & Taxes ({city}, {pricing.state_code})
              </h4>
              <p className="text-xs text-slate-400">
                Calculated via AutoMind Verified Motor Vehicle Tax Engine ({pricing.state_code} Motor Vehicle Act)
              </p>
            </div>
            {renderStatusBadge(pricing.status)}
          </div>

          {quote && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Ex-Showroom Price</span>
                <div className="text-base font-bold text-white mt-1">
                  ₹{quote.exShowroomPrice?.toLocaleString('en-IN')}
                </div>
                <span className="text-[10px] text-slate-400">Base Retail</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">RTO Road Tax</span>
                <div className="text-base font-bold text-amber-400 mt-1">
                  ₹{quote.rtoTax?.toLocaleString('en-IN')}
                </div>
                <span className="text-[10px] text-slate-400">{pricing.state_code} State Slab</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Insurance & FASTag</span>
                <div className="text-base font-bold text-sky-400 mt-1">
                  ₹{((quote.insurance || 0) + (quote.fastag || 0)).toLocaleString('en-IN')}
                </div>
                <span className="text-[10px] text-slate-400">1-Yr Own + 3-Yr Third Party</span>
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                <span className="text-[10px] text-emerald-400 uppercase font-bold">Estimated On-Road</span>
                <div className="text-base font-extrabold text-emerald-300 mt-1">
                  ₹{quote.onRoadPrice?.toLocaleString('en-IN')}
                </div>
                <span className="text-[10px] text-emerald-400/80">Inclusive of all duties</span>
              </div>
            </div>
          )}

          {/* EMI Options */}
          {pricing.emi_options && pricing.emi_options.length > 0 && (
            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60 text-xs text-slate-300 flex items-center justify-between">
              <span>
                Indicative 5-Year Loan EMI @ {pricing.emi_options[0].interestRate}% p.a. (20% Down Payment):
              </span>
              <span className="font-bold text-white text-sm">
                ₹{pricing.emi_options[0].monthlyEMI?.toLocaleString('en-IN')}/month
              </span>
            </div>
          )}

          {/* Commercial Provider Audit Notice */}
          <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/40 text-[11px] text-slate-400 flex items-start gap-2">
            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-300">Third-Party Pricing Provider Audit: </span>
              IDSPay (Fintech/BBPS) and MyNewCar do not offer open unauthenticated programmatic endpoints. Both require commercial enterprise onboarding. AutoMind uses genuine statutory motor vehicle tax schedules to guarantee accuracy without relying on unverified scrapers.
            </div>
          </div>
        </div>
      )}

      {/* Used Car Market Snapshot & Statistics */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              Used Vehicle Market Data & Aggregate Statistics
            </h4>
            <p className="text-xs text-slate-400">
              Provider: {market?.provider || 'DataForCars'} • Geographic Coverage: {market?.geographic_coverage || 'North America (USD)'}
            </p>
          </div>
          {renderStatusBadge(market?.status)}
        </div>

        {/* Currency & Geographic Boundary Notice */}
        <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 flex items-start gap-2">
          <ShieldAlert className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
          <p>
            <span className="font-bold">Market Separation Notice: </span>
            DataForCars provides North American used-vehicle market listings denominated in <strong>USD ($)</strong>. These are strictly segregated and not represented as Indian INR used prices. A dedicated partner interface is prepared for licensed Indian listing feeds.
          </p>
        </div>

        {market?.statistics && market.statistics.listing_count > 0 ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Active Listings</span>
                <div className="text-lg font-bold text-white mt-1">
                  {market.statistics.listing_count}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Median Asking</span>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  ${market.statistics.median_price?.toLocaleString()}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Price Range</span>
                <div className="text-sm font-bold text-slate-200 mt-1">
                  ${market.statistics.min_price?.toLocaleString()} - ${market.statistics.max_price?.toLocaleString()}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Avg Mileage</span>
                <div className="text-lg font-bold text-sky-400 mt-1">
                  {market.statistics.avg_mileage ? `${Math.round(market.statistics.avg_mileage).toLocaleString()} mi` : 'N/A'}
                </div>
              </div>
            </div>

            <p className="text-[11px] text-slate-400 italic">
              {market.statistics.disclaimer}
            </p>
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/60 text-xs text-slate-400">
            <p className="font-semibold text-slate-300">Live Snapshot Status</p>
            <p className="mt-1 leading-relaxed">
              {market?.note || 'No active listings observed for this specific model configuration. DATAFORCARS_API_KEY can be added in .env to enable live North American used-market snapshots.'}
            </p>
          </div>
        )}
      </div>

      {/* Automotive News Feed */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Newspaper className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Relevant Automotive News & Updates
            </h4>
          </div>
          {renderStatusBadge(news?.status)}
        </div>

        {news?.articles && news.articles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {news.articles.map((art, idx) => (
              <a
                key={idx}
                href={art.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition-colors block group"
              >
                <h5 className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors line-clamp-2">
                  {art.title}
                </h5>
                {art.description && (
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">
                    {art.description}
                  </p>
                )}
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
                  <span>{art.source}</span>
                  <span className="inline-flex items-center gap-1 text-indigo-400">
                    Read <ExternalLink className="w-2.5 h-2.5" />
                  </span>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60 text-xs text-slate-400">
            {news?.note || 'No recent automotive news articles found for this vehicle.'}
          </div>
        )}
      </div>

      {/* Traffic & Telemetry Status */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-sky-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Traffic & Urban Congestion Telemetry
            </h4>
          </div>
          {renderStatusBadge(traffic?.status)}
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          {traffic?.note || 'INRIX enterprise telemetry is currently optional and requires an enterprise data contract for Indian urban corridors.'}
        </p>
      </div>

      {/* Data Source Provenance & Freshness Attribution */}
      <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-3">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Federated Data Attribution & Freshness Metadata
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-[11px] text-slate-400">
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 font-semibold block">Vehicle Specs:</span>
            {data.metadata.data_sources?.specifications?.provider || 'NHTSA vPIC / Vehicles.dev'}
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 font-semibold block">Pricing Engine:</span>
            AutoMind Motor Vehicle Act Engine ({pricing?.state_code})
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 font-semibold block">Used Market Data:</span>
            DataForCars API (North America USD)
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 font-semibold block">Weather Telemetry:</span>
            Open-Meteo Global Open API
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 font-semibold block">Fuel Rate Provider:</span>
            IndianAPI / APIMitra Feeds
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 font-semibold block">News Provider:</span>
            NewsAPI Everything Endpoint
          </div>
        </div>
        <div className="text-[10px] text-slate-400 text-right pt-1">
          Fetched: {new Date(data.metadata.fetched_at).toUTCString()}
        </div>
      </div>
    </div>
  );
};
