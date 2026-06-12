export interface User {
  id: number;
  email: string;
  username: string;
  role: "user" | "admin";
  created_at: string;
}

export interface Project {
  id: number;
  user_id: number;
  title: string;
  description: string;
  skills_needed: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectMatch {
  project: Project;
  similarity: number;
  owner_username: string;
}

export type MatchStatus = "pending" | "accepted" | "rejected";

export interface MatchRequest {
  id: number;
  requester_id: number;
  recipient_id: number;
  project_id: number;
  requester_project_id: number | null;
  status: MatchStatus;
  created_at: string;
  updated_at: string;
  requester_username: string;
  recipient_username: string;
  project: Project;
  requester_project: Project | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export type WsMessage =
  | { type: "connected"; user_id: number }
  | {
      type: "match_request";
      match_request_id: number;
      requester_id: number;
      requester_username: string;
      project_id: number;
      project_title: string;
      requester_project_id: number | null;
    }
  | {
      type: "match_accepted";
      match_request_id: number;
      recipient_id: number;
      recipient_username: string;
      project_id: number;
      project_title: string;
    }
  | {
      type: "match_rejected";
      match_request_id: number;
      recipient_id: number;
      recipient_username: string;
      project_id: number;
      project_title: string;
    };

export interface Notification {
  id: string;
  type: WsMessage["type"];
  title: string;
  message: string;
}
