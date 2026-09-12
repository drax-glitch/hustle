import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import * as api from "../api/api";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("life_rpg_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!localStorage.getItem("life_rpg_token")) {
      setLoading(false);
      return;
    }
    try {
      const me = await api.fetchMe();
      setUser(me);
    } catch (err) {
      logout();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loginUser = async (payload) => {
    const data = await api.login(payload);
    localStorage.setItem("life_rpg_token", data.token);
    setToken(data.token);
    setUser(data.user);
    return data.user;
  };

  const registerUser = async (payload) => {
    const data = await api.register(payload);
    localStorage.setItem("life_rpg_token", data.token);
    setToken(data.token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("life_rpg_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AppContext.Provider
      value={{ token, user, setUser, loading, loginUser, registerUser, logout, refreshUser }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used inside AppProvider");
  return ctx;
}
