import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api from "../services/api";

const RankingContext = createContext(null);

export function RankingProvider({ children }) {
  const [rankings, setRankings] = useState([]);
  const [currentDonor, setCurrentDonor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const refreshRankings = useCallback(async () => {
    const userType = String(localStorage.getItem("user_type") || "").toLowerCase();

    if (!localStorage.getItem("access") || !["donor", "ngo", "admin"].includes(userType)) {
      setRankings([]);
      setCurrentDonor(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(false);

    try {
      const { data } = await api.get("donors/ranking/");
      setRankings(Array.isArray(data) ? data : data?.rankings || []);
      setCurrentDonor(data?.current_donor || null);
    } catch {
      setRankings([]);
      setCurrentDonor(null);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshRankings();
  }, [refreshRankings]);

  return (
    <RankingContext.Provider value={{ rankings, currentDonor, loading, error, refreshRankings }}>
      {children}
    </RankingContext.Provider>
  );
}

export function useRanking() {
  const context = useContext(RankingContext);

  if (!context) {
    throw new Error("useRanking must be used within a RankingProvider.");
  }

  return context;
}
