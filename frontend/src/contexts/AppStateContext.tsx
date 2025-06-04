import React, { createContext, useContext, useEffect, useState } from "react";

interface AppState {
  selectedFolder: string | null;
  scanResults: any | null;
  organizationPlan: any | null;
  currentStep: number;
  lastActivity: Date | null;
}

interface AppStateContextType {
  state: AppState;
  updateState: (updates: Partial<AppState>) => void;
  resetState: () => void;
}

const defaultState: AppState = {
  selectedFolder: null,
  scanResults: null,
  organizationPlan: null,
  currentStep: 0,
  lastActivity: null,
};

const AppStateContext = createContext<AppStateContextType | undefined>(
  undefined
);

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used within AppStateProvider");
  }
  return context;
};

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, setState] = useState<AppState>(() => {
    const saved = localStorage.getItem("appState");
    return saved ? JSON.parse(saved) : defaultState;
  });

  useEffect(() => {
    localStorage.setItem("appState", JSON.stringify(state));
  }, [state]);

  const updateState = (updates: Partial<AppState>) => {
    setState((prev) => ({
      ...prev,
      ...updates,
      lastActivity: new Date(),
    }));
  };

  const resetState = () => {
    setState(defaultState);
    localStorage.removeItem("appState");
  };

  return (
    <AppStateContext.Provider value={{ state, updateState, resetState }}>
      {children}
    </AppStateContext.Provider>
  );
};
