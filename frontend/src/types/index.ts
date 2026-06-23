// API Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  departments: string[];
  is_active: boolean;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  document_ids?: string[];
}

export interface SourceCitation {
  filename: string;
  department: string;
  chunk_index: number;
  score: number;
  content_snippet: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: SourceCitation[];
  blocked: boolean;
  block_reason?: string;
  latency_ms: number;
}

export interface Conversation {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  created_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  department: string;
  sensitivity: string;
  status: string;
  chunk_count: number;
  uploaded_by: string;
  created_at: string;
}

export interface MonitoringSummary {
  total_requests: number;
  avg_latency_ms: number;
  total_tokens: number;
  total_cost_usd: number;
  guardrail_triggers: number;
  error_count: number;
}

export interface EvalRun {
  id: string;
  run_name: string;
  dataset_name: string;
  total_questions: number;
  status: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface EvalResult {
  id: string;
  run_id: string;
  question: string;
  ground_truth: string;
  generated_answer: string;
  faithfulness?: number;
  answer_relevancy?: number;
  context_precision?: number;
  context_recall?: number;
}
