/**
 * Shared TypeScript interfaces used throughout the front‑end.
 */

export type Role = 'user' | 'assistant' | 'system';

export interface Message {
  role: Role;
  content: string;
  timestamp: number;
}