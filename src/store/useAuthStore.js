import { create } from "zustand";
import { supabase } from "../lib/supabase";

export const useAuthStore = create((set, get) => ({
  user: null,
  isLoading: true,

  setUser: (user) => {
    set({ user });
  },

  initialize: async () => {
    set({ isLoading: true });

    try {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      if (error) {
        console.error("Auth session error:", error);
      }

      set({
        user: session?.user || null,
        isLoading: false,
      });

      const {
        data: { subscription },
      } = supabase.auth.onAuthStateChange((_event, session) => {
        set({
          user: session?.user || null,
          isLoading: false,
        });
      });

      return () => {
        subscription?.unsubscribe();
      };
    } catch (err) {
      console.error("Auth initialize error:", err);

      set({
        user: null,
        isLoading: false,
      });
    }
  },

  signOut: async () => {
    try {
      await supabase.auth.signOut();

      set({
        user: null,
        isLoading: false,
      });
    } catch (err) {
      console.error("Sign out error:", err);
    }
  },
}));