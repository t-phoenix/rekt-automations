-- Create Supabase Schema for Rekt Automations

-- 1. Automation Runs Table (Top-level tracker)
CREATE TABLE rekt_meme_automation_runs (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    status TEXT NOT NULL,
    configuration JSONB
);

-- 2. Content Generations Table (Text Flow)
CREATE TABLE rekt_meme_content_generations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    platforms TEXT[],
    trends_data JSONB,
    business_context JSONB,
    generated_text JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Trend Research Table (Standalone Trend Flow)
CREATE TABLE rekt_meme_trend_research (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    raw_trends JSONB,
    filtered_trends JSONB,
    scored_trends JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Meme Generations Table (Meme & Animation Flows)
CREATE TABLE rekt_meme_generations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    sentiment TEXT,
    template_used TEXT,
    meme_text JSONB,
    image_storage_path TEXT,
    video_storage_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Twitter Engagement Table (Standalone Twitter Flow)
CREATE TABLE rekt_meme_twitter_engagement (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    scraped_tweets JSONB,
    scored_tweets JSONB,
    suggested_replies JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Competition Research Table (Competition Flow)
CREATE TABLE rekt_competition_research (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    competitors JSONB NOT NULL DEFAULT '[]'::jsonb,
    intermediary_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    processed_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_output JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. KOL Research Table (KOL Flow)
CREATE TABLE rekt_kol_research (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT REFERENCES rekt_meme_automation_runs(id) ON DELETE CASCADE,
    target_criteria JSONB NOT NULL DEFAULT '{}'::jsonb,
    identified_kols JSONB NOT NULL DEFAULT '[]'::jsonb,
    engagement_plans JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. Storage Bucket ('rekt_media')
INSERT INTO storage.buckets (id, name, public) 
VALUES ('rekt_media', 'rekt_media', true)
ON CONFLICT (id) DO NOTHING;

-- Storage Policies for 'rekt_media' bucket (Allowing service roles full access, public read)
CREATE POLICY "Public Access" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'rekt_media');

CREATE POLICY "Service Role Full Access" 
ON storage.objects FOR ALL 
USING (bucket_id = 'rekt_media');
