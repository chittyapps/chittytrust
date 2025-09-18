/**
 * @chittyos/cloudflare-core TypeScript definitions
 */

export interface ChittyCoreConfig {
  services?: {
    schema?: ServiceConfig;
    id?: ServiceConfig;
    trust?: ServiceConfig;
    evidence?: ServiceConfig;
    marketplace?: ServiceConfig;
    ai?: ServiceConfig;
  };
  ai?: {
    enabled?: boolean;
    vectorize?: { enabled?: boolean };
    models?: string[];
  };
  worldOrder?: {
    phase?: number;
    target?: string;
    resistance?: string;
  };
  security?: {
    apiKeys?: boolean;
    rateLimit?: { requests: number; window: number };
    cors?: { enabled: boolean; origins: string[] };
  };
}

export interface ServiceConfig {
  enabled?: boolean;
  domain?: string;
}

export interface ServiceHealth {
  service: string;
  domain: string;
  status: 'active' | 'error' | 'maintenance';
  uptime: number;
  requests: number;
  errors: number;
  features: string[];
  ready: boolean;
}

export interface WorldOrderStatus {
  current_phase: number;
  phase_info: {
    name: string;
    description: string;
    status: string;
  };
  target: string;
  status: string;
  global_reach: string;
  resistance: string;
  next_milestone: string;
  secret_weapons: string[];
}

export interface TrustResult {
  persona_id: string;
  composite_score: number;
  chitty_level: string;
  ai_enhanced: boolean;
  calculated_at: string;
  chittyos_powered: boolean;
}

export interface EvidenceResult {
  evidence_id: string;
  status: string;
  blockchain_recorded: boolean;
  court_admissible: boolean;
  chittyos_verified: boolean;
}

export interface AIAnalysisResult {
  analysis: string;
  confidence: number;
  model_used: string;
  chittyos_enhanced: boolean;
}

export interface HealthCheckResult {
  status: string;
  uptime: number;
  services: ServiceHealth[];
  world_order: WorldOrderStatus;
  version: string;
  chittyos: {
    core: string;
    trust_network: string;
    global_reach: string;
  };
}

export declare class ChittyCloudflareCore {
  config: ChittyCoreConfig;
  services: Map<string, any>;
  initialized: boolean;
  startTime: number;

  constructor(config?: ChittyCoreConfig);
  
  initialize(): Promise<ChittyCloudflareCore>;
  initializeService(name: string, config: ServiceConfig): Promise<void>;
  initializeAI(): Promise<void>;
  
  getServiceFeatures(serviceName: string): string[];
  getServiceHealth(): ServiceHealth[];
  getWorldOrderStatus(): WorldOrderStatus;
  
  handleRequest(request: Request, env: any, ctx: any): Promise<Response>;
  getServiceByDomain(hostname: string): any;
  routeToService(service: any, request: Request, env: any, ctx: any): Promise<Response>;
  
  calculateTrust(personaId: string, options?: any): Promise<TrustResult>;
  processEvidence(evidenceData: any, options?: any): Promise<EvidenceResult>;
  analyzeWithAI(prompt: string, model?: string): Promise<AIAnalysisResult>;
  
  healthCheck(): HealthCheckResult;
  
  isServiceEnabled(serviceName: string): boolean;
  getServiceUrl(serviceName: string): string | null;
  trackEvent(event: string, data?: any): void;
}

export declare function createChittyCore(config?: ChittyCoreConfig): ChittyCloudflareCore;

export declare const defaultConfigs: {
  minimal: ChittyCoreConfig;
  full: ChittyCoreConfig;
  worldDomination: ChittyCoreConfig;
};

export default ChittyCloudflareCore;