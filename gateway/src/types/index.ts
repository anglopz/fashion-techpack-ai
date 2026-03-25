export interface CreateTechPackRequest {
  description: string;
  garment_type?: string;
  target_season?: string;
  fabric_preferences?: string[];
  color_palette?: string[];
  style_references?: string[];
  engine?: "langgraph" | "crewai";
}

export interface CreateTechPackResponse {
  id: string;
  status: string;
  engine: string;
  ws_url: string;
}

export interface TechPackResult {
  id: string;
  status: string;
  engine: string;
  tech_pack?: Record<string, unknown>;
  created_at?: string;
  processing_time_ms?: number;
}

export interface CreateFabricRequest {
  name: string;
  composition: string;
  weight_gsm: number;
  width_cm: number;
  color: string;
  care_instructions: string[];
}

export interface FabricSearchResult {
  results: Array<{
    id: string;
    name: string;
    similarity: number;
    [key: string]: unknown;
  }>;
}

export interface WSMessage {
  agent?: string;
  status: string;
  message?: string;
  data?: Record<string, unknown>;
  event?: string;
}

export interface AuthPayload {
  sub: string;
  iat: number;
  exp: number;
  [key: string]: unknown;
}
