import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api } from "../api/client";
import type { Notification, User } from "../types";
import { useWebSocket } from "../hooks/useWebSocket";

const TOKEN_KEY = "aidevconnect_token";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  notifications: Notification[];
  dismissNotification: (id: string) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function wsMessageToNotification(message: { type: string; [key: string]: unknown }): Notification | null {
  switch (message.type) {
    case "match_request":
      return {
        id: crypto.randomUUID(),
        type: "match_request",
        title: "New match request",
        message: `${message.requester_username} wants to collaborate on "${message.project_title}"`,
      };
    case "match_accepted":
      return {
        id: crypto.randomUUID(),
        type: "match_accepted",
        title: "Match accepted!",
        message: `${message.recipient_username} accepted your request for "${message.project_title}"`,
      };
    case "match_rejected":
      return {
        id: crypto.randomUUID(),
        type: "match_rejected",
        title: "Match declined",
        message: `${message.recipient_username} declined your request for "${message.project_title}"`,
      };
    default:
      return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const handleWsMessage = useCallback((message: { type: string; [key: string]: unknown }) => {
    const notification = wsMessageToNotification(message);
    if (notification) {
      setNotifications((prev) => [notification, ...prev].slice(0, 5));
    }
  }, []);

  useWebSocket(token, handleWsMessage);

  const refreshUser = useCallback(async () => {
    if (!token) {
      setUser(null);
      return;
    }
    const me = await api.me(token);
    setUser(me);
  }, [token]);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const me = await api.me(token);
        if (!cancelled) setUser(me);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.login({ email, password });
    localStorage.setItem(TOKEN_KEY, access_token);
    setToken(access_token);
    const me = await api.me(access_token);
    setUser(me);
  }, []);

  const register = useCallback(async (email: string, username: string, password: string) => {
    await api.register({ email, username, password });
    await login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setNotifications([]);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      notifications,
      dismissNotification,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, token, loading, notifications, dismissNotification, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
