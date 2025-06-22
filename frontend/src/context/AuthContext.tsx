import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import type { ReactNode } from "react";
import api from "../services/api";


type User = { // Blueprint response from the cookie
    id: number;
    email: string; 
}

type AuthContextType = { // variable types for value in <AuthContext.Provider needs to be defined. See line 52.
    user: User | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({children}: {children: ReactNode}) { // Children is just a parameter set to give access for whatever you will be putting in between AuthContext.Provider
    const [user, setUser] = useState<User | null>(null); // Setting a current user

    useEffect(() => { // Read the session from the cookie to set the current user.
        api.get("/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => setUser(null)) 
    }, [])

    const login = async (email: string, password: string) => {
        try {
            await api.post("/auth/login", {email, password}); // Gets a cookie from the successful POST request
            const res = await api.get("/auth/me"); // Uses the cookie to send a GET request
            setUser(res.data); // Uses the cookie from the GET request to set a user.
        } 
        catch (err: any) {
            const message = err.response?.data?.error || "Login Failed";
            throw new Error(message)
        }
        
    }

    const register = async (email: string, password: string) => {
        try {
            await api.post("/auth/register", {email, password});
            const res = await api.get("/auth/me");
            setUser(res.data);
        }
        catch (err: any) {
            const message = err.response?.data?.error || "Registration Failed";
            throw new Error(message)
        }
    }

    const logout = async() => {
        await api.post("/auth/logout");
        setUser(null);
    }
    // AuthProvider passes the functions as values to the AuthContext component.
    return (
        <AuthContext.Provider value={{user, login, register, logout}}> 
            {children} 
        </AuthContext.Provider>
    )
}

export function useAuth() { // Allowing function components to be more easily accessed across files.
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

