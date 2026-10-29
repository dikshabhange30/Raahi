import { createContext, useContext, useEffect, useState, useCallback } from "react";
import api, { tokenStorage } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    if (!tokenStorage.get()) {
      setUser(null);
      setIsAdmin(false);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get("/users/me");
      setUser(data);
      // The backend has no is_admin flag, so we ask an admin-only route.
      // 200 = admin. 403 = normal user. (The backend enforces this, not the UI.)
      try {
        await api.get("/safety/admin/reports");
        setIsAdmin(true);
      } catch {
        setIsAdmin(false);
      }
    } catch {
      tokenStorage.clear();
      setUser(null);
      setIsAdmin(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const signIn = async (token) => {
    tokenStorage.set(token);
    setLoading(true);
    await fetchUser();
  };

  const signOut = () => {
    tokenStorage.clear();
    setUser(null);
    setIsAdmin(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAdmin, loading, signIn, signOut, refreshUser: fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
