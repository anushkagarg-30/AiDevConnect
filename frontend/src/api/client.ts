import type { MatchRequest, Project, ProjectMatch, TokenResponse, User } from "../types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const data = await response.json();
      message = data.detail ?? message;
      if (Array.isArray(message)) {
        message = message.map((item) => item.msg ?? JSON.stringify(item)).join(", ");
      }
    } catch {
      // ignore parse errors
    }
    throw new ApiError(response.status, String(message));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  register: (data: { email: string; username: string; password: string }) =>
    request<User>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<TokenResponse>("/api/v1/auth/login/json", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: (token: string) => request<User>("/api/v1/auth/me", {}, token),

  listProjects: (token: string) => request<Project[]>("/api/v1/projects", {}, token),

  createProject: (
    token: string,
    data: { title: string; description: string; skills_needed?: string },
  ) =>
    request<Project>("/api/v1/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  deleteProject: (token: string, projectId: number) =>
    request<void>(`/api/v1/projects/${projectId}`, { method: "DELETE" }, token),

  getMatches: (token: string, projectId: number) =>
    request<ProjectMatch[]>(`/api/v1/projects/${projectId}/matches`, {}, token),

  createMatchRequest: (
    token: string,
    data: { project_id: number; requester_project_id?: number },
  ) =>
    request<MatchRequest>("/api/v1/matches", {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  listSentMatches: (token: string) =>
    request<MatchRequest[]>("/api/v1/matches/sent", {}, token),

  listReceivedMatches: (token: string) =>
    request<MatchRequest[]>("/api/v1/matches/received", {}, token),

  acceptMatch: (token: string, matchId: number) =>
    request<MatchRequest>(`/api/v1/matches/${matchId}/accept`, { method: "POST" }, token),

  rejectMatch: (token: string, matchId: number) =>
    request<MatchRequest>(`/api/v1/matches/${matchId}/reject`, { method: "POST" }, token),
};

export function getWsUrl(token: string): string {
  if (import.meta.env.VITE_API_URL) {
    const wsBase = import.meta.env.VITE_API_URL.replace(/^http/, "ws");
    return `${wsBase}/api/v1/ws?token=${encodeURIComponent(token)}`;
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/v1/ws?token=${encodeURIComponent(token)}`;
}

export { ApiError };
