export interface WSMessage {
  agent?: string;
  status: string;
  message?: string;
  data?: Record<string, unknown>;
  event?: string;
}
