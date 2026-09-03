import { CarVariantSummary } from './car';

export interface SourceCard {
  id: number;
  title: string;
  website: string;
  url: string;
  domain: string;
  reason: string;
  reliability_score: number;
}

export type ResearchStage = 'understanding' | 'searching' | 'comparing' | 'ranking' | 'generating';

export interface ResearchStep {
  stage: ResearchStage;
  message: string;
  timestamp: number;
  completed: boolean;
}

export interface VehicleImageItem {
  id: string;
  url: string;
  alt: string;
  category: 'exterior' | 'interior' | 'feature';
  caption: string;
}

export interface VehicleGallery {
  type: 'vehicle_gallery';
  vehicle: {
    manufacturer: string;
    model: string;
    tagline?: string;
  };
  images: VehicleImageItem[];
}

export interface ChatMessage {
  id?: number;
  conversation_id?: number;
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    sources?: SourceCard[];
    cars?: CarVariantSummary[];
    gallery?: VehicleGallery;
    pricing_quote?: any;
    comparison?: any;
    follow_up?: {
      fields?: string[];
      question?: string;
    };
    agent_plan?: any;
    feedback?: {
      id?: number;
      rating: 'up' | 'down';
      reasonCode?: string | null;
      comment?: string | null;
    };
    parsed_constraints?: Record<string, any>;
  };
  created_at?: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}
