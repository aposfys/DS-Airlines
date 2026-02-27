import React, { createContext, useContext, useState, useEffect } from "react";
import api, { getMe } from "../api";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const response = await getMe();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem("token");
        setUser(null);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (token) => {
    localStorage.setItem("token", token);
    await fetchUser();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
