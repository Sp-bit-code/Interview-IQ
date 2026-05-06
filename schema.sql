-- InterviewIQ Database Schema
-- Run this completely in the Supabase SQL Editor

-- 1. Users table (Optional extension if you want custom data, otherwise Supabase Auth handles core user login)
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Sessions table
CREATE TABLE public.sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  track TEXT NOT NULL,          -- HR, Technical, General
  difficulty TEXT NOT NULL,     -- Fresher, Mid-Level, Senior
  duration INTEGER DEFAULT 0,   -- in seconds
  overall_score NUMERIC(3, 1),  -- e.g. 8.5
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Session Scores table (per dimension)
CREATE TABLE public.session_scores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
  dimension TEXT NOT NULL,      -- Communication, Confidence, Body Language, Speaking Pace
  score NUMERIC(3, 1) NOT NULL  -- 0.0 to 10.0
);

-- 4. Transcripts table
CREATE TABLE public.transcripts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
  speaker TEXT NOT NULL,        -- 'user' or 'ai'
  text TEXT NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Reports table
CREATE TABLE public.reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
  markdown_content TEXT,
  pdf_url TEXT,
  share_token TEXT UNIQUE,
  expires_at TIMESTAMPTZ
);

-- 6. Badges table (Gamification)
CREATE TABLE public.badges (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  badge_type TEXT NOT NULL,     -- e.g. 'Eye Contact Pro', '90+ Club'
  earned_at TIMESTAMPTZ DEFAULT NOW()
);
