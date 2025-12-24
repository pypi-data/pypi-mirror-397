-- HERMIOS PROTOCOL: SUPABASE DATABASE SETUP
-- Target: Postgres (Supabase)

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS public.hermios_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- 2. Create API Keys Table
CREATE TABLE IF NOT EXISTS public.hermios_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.hermios_users(id) ON DELETE CASCADE,
    key_hash TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- 3. Create Audit Logs Table (ZOO Verification)
CREATE TABLE IF NOT EXISTS public.hermios_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.hermios_users(id),
    command_type TEXT NOT NULL, -- 'STANDARD' or 'OVERRIDE'
    raw_prompt TEXT NOT NULL,
    sanitized_prompt TEXT,
    status TEXT NOT NULL, -- 'SUCCESS', 'HALT', 'ERROR'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.hermios_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hermios_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hermios_audit_logs ENABLE ROW LEVEL SECURITY;

-- 5. Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_hermios_api_keys_hash ON public.hermios_api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_hermios_audit_logs_user ON public.hermios_audit_logs(user_id);
