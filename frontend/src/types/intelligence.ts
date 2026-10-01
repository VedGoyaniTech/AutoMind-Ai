export interface CarIntelligenceQuery {
  make: string;
  model: string;
  year?: number | null;
  city: string;
  vin?: string | null;
}

export interface ProviderStatus {
  provider: string;
  status: 'live' | 'cached' | 'historical' | 'not_configured' | 'unavailable' | 'error' | string;
  last_updated?: string;
  currency?: string;
  note?: string;
  provenance?: string;
}

export interface VehicleSpecsData {
  status: string;
  provider: string;
  specs?: Record<string, any>;
  data?: Record<string, any>;
  vin_details?: Record<string, any>;
  provenance?: string;
  error?: string;
}

export interface PriceBreakdown {
  exShowroomPrice: number;
  rtoTax: number;
  roadSafetyCess?: number;
  insurance: number;
  fastag: number;
  onRoadPrice: number;
}

export interface EmiOption {
  tenureYears: number;
  monthlyEMI: number;
  totalInterest: number;
  totalRepayment: number;
  interestRate: number;
}

export interface IndiaPricingData {
  status: string;
  city: string;
  state_code: string;
  currency: string;
  price_types?: {
    ex_showroom?: { amount: number; type: string; description: string };
    estimated_on_road?: { amount: number; type: string; description: string };
    dealer_quotes?: { note: string };
  };
  breakdown?: PriceBreakdown;
  emi_options?: EmiOption[];
  commercial_provider_audit?: {
    idspay?: { status: string; provider_url: string; note: string };
    mynewcar?: { status: string; provider_url: string; note: string };
  };
  provenance?: string;
  error?: string;
}

export interface MarketListing {
  id?: string;
  title?: string;
  price: number;
  currency: string;
  year?: number;
  mileage?: number;
  mileage_unit?: string;
  location?: string;
  url?: string;
  is_asking_price?: boolean;
}

export interface MarketStatistics {
  currency: string;
  listing_count: number;
  min_price?: number | null;
  max_price?: number | null;
  median_price?: number | null;
  average_price?: number | null;
  avg_mileage?: number | null;
  avg_listing_age_days?: number | null;
  price_distribution?: Record<string, number>;
  trend_indicator?: string;
  disclaimer?: string;
}

export interface MarketData {
  status: string;
  provider: string;
  geographic_coverage?: string;
  currency?: string;
  listings?: MarketListing[];
  statistics?: MarketStatistics;
  note?: string;
  provenance?: string;
  error?: string;
}

export interface NewsArticle {
  title: string;
  source: string;
  published_at?: string;
  url: string;
  description?: string;
}

export interface NewsData {
  status: string;
  provider: string;
  count: number;
  articles?: NewsArticle[];
  note?: string;
  provenance?: string;
  error?: string;
}

export interface WeatherData {
  status: string;
  provider: string;
  city?: string;
  country?: string;
  temperature_celsius?: number;
  feels_like_celsius?: number;
  relative_humidity_percent?: number;
  precipitation_mm?: number;
  wind_speed_kmh?: number;
  weather_condition?: string;
  driving_conditions?: string;
  observation_time?: string;
  provenance?: string;
  error?: string;
}

export interface FuelData {
  status: string;
  provider: string;
  city: string;
  currency?: string;
  petrol?: { price: number; unit: string; date?: string } | null;
  diesel?: { price: number; unit: string; date?: string } | null;
  note?: string;
  provenance?: string;
  error?: string;
}

export interface TrafficData {
  status: string;
  provider: string;
  city?: string;
  congestion_level?: string | null;
  incidents_count?: number;
  market_coverage?: string;
  note?: string;
  provenance?: string;
  error?: string;
}

export interface GroundedAIAnalysis {
  summary: string;
  provider: string;
  grounded_facts_count?: number;
  generated_at?: string;
}

export interface CarIntelligenceResponse {
  query: CarIntelligenceQuery;
  specifications: VehicleSpecsData;
  india_pricing: IndiaPricingData;
  market_data: MarketData;
  news: NewsData;
  weather: WeatherData;
  fuel: FuelData;
  traffic: TrafficData;
  ai_analysis: GroundedAIAnalysis;
  metadata: {
    is_cached: boolean;
    cached_at?: string;
    expires_at?: string;
    fetched_at: string;
    data_sources: Record<string, ProviderStatus>;
  };
}
