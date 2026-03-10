-- 1. Competition Research Table (Competition Flow)
CREATE TABLE IF NOT EXISTS rekt_competition_research (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    competitors JSONB NOT NULL DEFAULT '[]'::jsonb,
    intermediary_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    processed_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_output JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. KOL Research Table (KOL Flow)
CREATE TABLE IF NOT EXISTS rekt_kol_research (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    target_criteria JSONB NOT NULL DEFAULT '{}'::jsonb,
    identified_kols JSONB NOT NULL DEFAULT '[]'::jsonb,
    engagement_plans JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
