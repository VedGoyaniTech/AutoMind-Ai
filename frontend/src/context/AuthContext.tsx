import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthState, RegisterResponse } from '../types/user';
import { getMe, registerUser } from '../api/auth';

interface AuthContextType extends AuthState {
  login: (token: string, user: User) => void;
  logout: () => void;
  registerAccount: (data: { full_name: string; email: string; password: string; confirm_password?: string }) => Promise<RegisterResponse>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const initialToken = localStorage.getItem('automind_token');
  const initialUserStr = localStorage.getItem('automind_user');
  const initialUser: User | null = initialUserStr ? JSON.parse(initialUserStr) : null;

  const [state, setState] = useState<AuthState>({
    user: initialUser,
    token: initialToken,
    isAuthenticated: !!(initialToken && initialUser),
    isLoading: !initialUser && !!initialToken,
  });

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('automind_token');
      if (token) {
        try {
          const user = await getMe();
          localStorage.setItem('automind_user', JSON.stringify(user));
          setState({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // If getMe fails but we have initial local user, keep authenticated session
          if (!initialUser) {
            localStorage.removeItem('automind_token');
            localStorage.removeItem('automind_user');
            setState({ user: null, token: null, isAuthenticated: false, isLoading: false });
          } else {
            setState((prev) => ({ ...prev, isLoading: false }));
          }
        }
      } else {
        setState((prev) => ({ ...prev, isLoading: false }));
      }
    };
    initAuth();
  }, []);

  const login = (token: string, user: User) => {
    localStorage.setItem('automind_token', token);
    localStorage.setItem('automind_user', JSON.stringify(user));
    setState({
      user,
      token,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  const registerAccount = async (data: { full_name: string; email: string; password: string; confirm_password?: string }) => {
    const res = await registerUser(data);
    if (res.access_token && res.user) {
      login(res.access_token, res.user);
    }
    return res;
  };

  const logout = () => {
    localStorage.removeItem('automind_token');
    localStorage.removeItem('automind_user');
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  const refreshUser = async () => {
    try {
      const user = await getMe();
      localStorage.setItem('automind_user', JSON.stringify(user));
      setState((prev) => ({ ...prev, user }));
    } catch (e) {
      console.error('Refresh user error:', e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        registerAccount,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
