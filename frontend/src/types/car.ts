export interface SourceInfo {
  id: number;
  name: string;
  domain: string;
  base_url: string;
  reliability_score: number;
  source_type?: string;
}

export interface CarVariantSummary {
  id: number;
  manufacturer_name: string;
  model_name: string;
  variant_name: string;
  model_year: number;
  body_type: string;
  fuel_type: string;
  transmission: string;
  ex_showroom_price: number;
  estimated_on_road_price: number;
  currency: string;
  combined_mileage?: number;
  electric_range?: number;
  seating_capacity: number;
  airbags: number;
  safety_rating?: number;
  image_url?: string;
  is_saved?: boolean;
}

export interface CarDetail {
  id: number;
  manufacturer_name: string;
  model_name: string;
  variant_name: string;
  model_year: number;
  body_type: string;
  ex_showroom_price: number;
  estimated_on_road_price: number;
  currency: string;
  country: string;
  fuel_type: string;
  transmission: string;
  engine_cc?: number;
  cylinders?: number;
  horsepower?: number;
  torque_nm?: number;
  mileage_city?: number;
  mileage_highway?: number;
  combined_mileage?: number;
  battery_capacity?: number;
  electric_range?: number;
  charging_time?: number;
  seating_capacity: number;
  airbags: number;
  safety_rating?: number;
  boot_space?: number;
  ground_clearance?: number;
  length?: number;
  width?: number;
  height?: number;
  wheelbase?: number;
  drive_type: string;
  features?: Record<string, any>;
  safety_features?: Record<string, any>;
  infotainment_features?: Record<string, any>;
  comfort_features?: Record<string, any>;
  pros?: string[];
  cons?: string[];
  description?: string;
  image_url?: string;
  source_url?: string;
  source?: SourceInfo;
  is_saved?: boolean;
  last_updated: string;
}

export interface CarSearchFilterParams {
  query?: string;
  manufacturer?: string;
  body_type?: string;
  fuel_type?: string;
  transmission?: string;
  price_min?: number;
  price_max?: number;
  min_mileage?: number;
  min_airbags?: number;
  min_safety_rating?: number;
  page?: number;
  page_size?: number;
}
