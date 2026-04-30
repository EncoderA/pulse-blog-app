-- =============================================================================
-- TIMELINE SEED DATA
-- Database : pulse_blog (Neon)
-- Apply    : Run once manually in the Neon SQL console
-- Stories  : Iran–Israel escalation | US–China tariff war | India AI policy
-- =============================================================================
-- key_highlights uses \n-delimited plain text; frontend splits on \n for bullets
-- ingest_status = 'enriched' on all seed rows (all derived fields pre-populated)
-- is_mock = TRUE on all comment rows
-- =============================================================================

-- ---------------------------------------------------------------------------
-- STORY 1: Iran–Israel Conflict Escalation
-- ---------------------------------------------------------------------------
INSERT INTO timeline_posts (
    article_id, kb_source, slug, title, short_summary, published_at,
    content_length, source_url, tags, is_trending, is_ai_policy,
    quick_take, background, what_happened, key_highlights,
    impact, whats_next, policy_announced,
    focus_area, overview, impacts_detail,
    primary_image_url, ingest_status
) VALUES (
    'mock-iran-israel-001',
    'Reuters',
    'iran-launches-retaliatory-strikes',
    'Iran launches retaliatory strikes as regional tensions escalate',
    'Iran fired a wave of ballistic missiles toward Israeli territory in retaliation for strikes on Iranian military assets, triggering emergency sessions and US naval deployments.',
    '2026-04-22 14:00:00+00',
    3200,
    'https://reuters.com/world/middle-east/iran-israel-strikes-2026',
    ARRAY['Iran', 'Israel', 'missile strike', 'regional conflict', 'US response', 'Middle East'],
    TRUE, FALSE,
    'Iran launched retaliatory ballistic missiles toward Israel after weeks of escalating strikes, prompting an emergency UN Security Council session and a US carrier group deployment.',
    'Tensions between Iran and Israel have been escalating since early April 2026 following a series of Israeli airstrikes on Iranian military infrastructure in Syria. Iran had warned of a direct response if strikes continued on its proxies and strategic assets.',
    'Iran fired over 100 ballistic missiles toward Israeli territory on April 22, 2026. Israel''s Iron Dome and Arrow defence systems intercepted the majority of projectiles. The Israeli cabinet convened an emergency session within hours, and the US deployed a carrier strike group to the Eastern Mediterranean as a deterrent signal.',
    E'Iron Dome and Arrow systems intercepted the majority of Iranian ballistic missiles\nUS carrier group USS Gerald Ford deployed to Eastern Mediterranean within 48 hours\nUN Security Council convened emergency session; Russia and China vetoed a ceasefire resolution\nIsrael declared a state of emergency in the north; border communities evacuated',
    'The exchange marks the most direct Iran–Israel military confrontation since April 2024. Regional oil prices surged 12% on fears of a wider conflict. Gulf states called for de-escalation while continuing to allow US basing rights.',
    'Israel is expected to announce a retaliatory strike plan within 72 hours. US and European diplomats are shuttling between Tel Aviv and regional capitals to prevent further escalation. Iran has signalled it will respond proportionally to any further Israeli action.',
    FALSE,
    ARRAY['Middle East', 'Defence', 'Geopolitics'],
    'A direct military exchange between Iran and Israel risks drawing in regional actors and global powers, marking a dangerous new phase in Middle Eastern security.',
    'Immediate impacts include oil price volatility, heightened air-traffic disruptions over the Persian Gulf, and emergency diplomatic engagement by the US, UK, France, and Gulf states.',
    NULL,
    'enriched'
);

-- Events for Story 1
INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-10 09:00:00+00',
    'Israel strikes Iranian military assets in Syria',
    'Israeli Air Force conducted targeted strikes on Iranian Revolutionary Guard Corps command posts and weapons depots in Syria, destroying three facilities. Iran called it a "red line" violation.',
    NULL, 1
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-13 17:30:00+00',
    'Iron Dome intercepts drones; Israel declares emergency session',
    'Iran-backed groups launched a wave of drones toward northern Israel. Iron Dome intercepted 94% of projectiles. The Israeli security cabinet held an emergency overnight session to assess escalation options.',
    NULL, 2
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-16 11:00:00+00',
    'US deploys carrier group to Eastern Mediterranean',
    'The Pentagon confirmed the USS Gerald Ford carrier strike group was repositioned to the Eastern Mediterranean "in response to escalating regional tensions." The move was described as a deterrent, not an offensive posture.',
    NULL, 3
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-22 14:00:00+00',
    'Iran launches wave of ballistic missiles toward Israel',
    'Iran''s IRGC confirmed the launch of over 100 ballistic missiles toward Israeli territory. Most were intercepted. The UN Security Council convened an emergency session within hours. Israel mobilised reserve units along its northern border.',
    NULL, 4
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

-- Quotes for Story 1
INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, 'We will respond to any aggression with full force. Our patience is not unlimited.', 'Iranian Foreign Ministry Spokesperson', 1
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, 'Israel has the right and the obligation to defend itself. We will act when and how we choose.', 'Israeli Prime Minister''s Office', 2
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

-- Comments for Story 1 (mock)
INSERT INTO timeline_comments (post_id, comment_text, commenter_name, commenter_designation, commenter_image_url, is_mock, display_order)
SELECT id, 'This is the most serious direct military confrontation between Iran and Israel we have seen. The region is at a genuine inflection point.', 'Dr. Aisha Rahman', 'Senior Defence Analyst, IISS', NULL, TRUE, 1
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

INSERT INTO timeline_comments (post_id, comment_text, commenter_name, commenter_designation, commenter_image_url, is_mock, display_order)
SELECT id, 'Oil markets are pricing in a prolonged crisis. A 15–20% sustained price spike is plausible if the Strait of Hormuz faces any disruption.', 'Marcus Johansson', 'Energy Markets Strategist', NULL, TRUE, 2
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';


-- ---------------------------------------------------------------------------
-- STORY 2: US–China Tariff War Escalation
-- ---------------------------------------------------------------------------
INSERT INTO timeline_posts (
    article_id, kb_source, slug, title, short_summary, published_at,
    content_length, source_url, tags, is_trending, is_ai_policy,
    quick_take, background, what_happened, key_highlights,
    impact, whats_next, policy_announced,
    focus_area, overview, impacts_detail,
    primary_image_url, ingest_status
) VALUES (
    'mock-us-china-tariff-001',
    'Bloomberg',
    'us-raises-tariffs-on-china-145-percent',
    'US raises tariffs on Chinese goods to 145%; Beijing retaliates with 125%',
    'The White House announced sweeping 145% tariffs on a broad range of Chinese imports. Beijing responded within days with 125% counter-tariffs on US goods, sending global markets lower and triggering supply chain warnings across the tech sector.',
    '2026-04-14 16:00:00+00',
    2900,
    'https://bloomberg.com/news/articles/us-china-tariffs-escalation-2026',
    ARRAY['tariffs', 'trade war', 'supply chain', 'semiconductors', 'US-China', 'economics'],
    TRUE, FALSE,
    'The US imposed 145% tariffs on Chinese imports; China retaliated with 125% on US goods. Tech and manufacturing sectors warned of severe supply chain disruption as both sides dug in.',
    'US–China trade tensions have been building since early 2026 following disputes over semiconductor export controls and Chinese subsidies to state-owned manufacturers. The Biden-era tariff framework had largely held, but the new administration moved to dramatically raise rates in April.',
    'On April 2, 2026, the White House announced 145% tariffs on a wide range of Chinese goods including electronics, steel, and consumer products. Beijing responded on April 7 with 125% counter-tariffs on US agricultural products, aircraft parts, and energy exports. Markets fell sharply, and major technology companies issued profit warnings citing supply chain disruption.',
    E'US 145% tariffs cover electronics, steel, consumer goods, and intermediate manufacturing inputs\nChina''s 125% counter-tariffs target US agriculture, aircraft components, and LNG exports\nNasdaq fell 4.2% on the day of Beijing''s announcement; semiconductor index dropped 7.1%\nMajor tech OEMs warned of 3–6 month supply chain disruption for components sourced from China\nBoth sides agreed to back-channel diplomatic talks after G7 pressure',
    'The tariff exchange is the sharpest trade escalation between the US and China since 2018–2019. US consumer prices for electronics are expected to rise 8–12% within six months. Chinese export-dependent manufacturers face an existential challenge, particularly in the solar panel and EV battery sectors.',
    'Both governments have agreed to informal back-channel talks brokered by Switzerland. A formal negotiation framework is expected to be announced within 30 days. Markets are watching for any signal of a phased tariff reduction in exchange for Chinese concessions on intellectual property and state subsidies.',
    FALSE,
    ARRAY['Trade', 'Economics', 'US-China Relations', 'Supply Chain'],
    'The tariff escalation reflects a fundamental realignment of global trade architecture as both superpowers contest technology supply chains and manufacturing dominance.',
    'Short-term: equity market volatility, consumer price increases, and manufacturing slowdowns in both countries. Medium-term: accelerated decoupling of semiconductor and battery supply chains; reshoring investment in Mexico, India, and Southeast Asia.',
    NULL,
    'enriched'
);

-- Events for Story 2
INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-02 12:00:00+00',
    'White House announces 145% tariff on Chinese imports',
    'President announced sweeping tariffs of 145% on a broad range of Chinese goods including electronics, intermediate manufacturing inputs, steel, and consumer products. The move was framed as a response to "unfair Chinese trade practices and intellectual property theft."',
    NULL, 1
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-07 08:00:00+00',
    'Beijing responds with 125% counter-tariffs on US goods',
    'China''s Ministry of Commerce announced 125% retaliatory tariffs on US agricultural products, aircraft components, and LNG exports. The response was described as "firm, proportionate, and necessary to protect Chinese sovereignty and economic interests."',
    NULL, 2
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-14 09:30:00+00',
    'Markets fall; tech sector issues supply chain warnings',
    'Global equity markets sold off sharply. The Nasdaq fell 4.2%; the Philadelphia Semiconductor Index dropped 7.1%. Apple, Nvidia, and Dell issued statements warning of supply chain disruption lasting 3–6 months for China-sourced components.',
    NULL, 3
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-25 15:00:00+00',
    'Both sides agree to back-channel negotiations',
    'Following G7 pressure and Swiss mediation, the US and China confirmed informal back-channel talks. Neither side announced a tariff pause, but both described the talks as "constructive." Markets recovered partially on the news.',
    NULL, 4
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

-- Quotes for Story 2
INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, 'America will no longer subsidise China''s economic rise at the expense of American workers and American industry.', 'US Trade Representative', 1
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, 'China does not want a trade war, but we are not afraid of one. We will protect our national interests by any means necessary.', 'Chinese Ministry of Commerce Spokesperson', 2
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

-- Comments for Story 2 (mock)
INSERT INTO timeline_comments (post_id, comment_text, commenter_name, commenter_designation, commenter_image_url, is_mock, display_order)
SELECT id, 'This is the deepest trade rupture between the two largest economies in a generation. The decoupling of technology supply chains is now accelerating in ways that will reshape global manufacturing for decades.', 'Prof. Linda Chen', 'International Trade Economist, MIT', NULL, TRUE, 1
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';

INSERT INTO timeline_comments (post_id, comment_text, commenter_name, commenter_designation, commenter_image_url, is_mock, display_order)
SELECT id, 'India and Southeast Asia are the quiet beneficiaries here. We are already seeing redirected FDI flows that would have gone to China five years ago.', 'Rajiv Menon', 'Emerging Markets Strategist, Goldman Sachs', NULL, TRUE, 2
FROM timeline_posts WHERE article_id = 'mock-us-china-tariff-001';


-- ---------------------------------------------------------------------------
-- STORY 3: India National AI Policy
-- ---------------------------------------------------------------------------
INSERT INTO timeline_posts (
    article_id, kb_source, slug, title, short_summary, published_at,
    content_length, source_url, tags, is_trending, is_ai_policy,
    quick_take, background, what_happened, key_highlights,
    impact, whats_next, policy_announced,
    focus_area, overview, impacts_detail,
    primary_image_url, ingest_status
) VALUES (
    'mock-india-ai-policy-001',
    'The Hindu',
    'india-launches-national-ai-policy',
    'India launches national AI policy targeting public infrastructure and startup ecosystem',
    'The Indian government unveiled a comprehensive national AI policy establishing compute access programs, safety guidelines, and sector-specific pilots across healthcare, agriculture, education, and public services.',
    '2026-04-05 10:00:00+00',
    2600,
    'https://thehindu.com/sci-tech/technology/india-national-ai-policy-2026',
    ARRAY['AI policy', 'India', 'compute access', 'digital infrastructure', 'startups', 'public services'],
    FALSE, TRUE,
    'India announced a national AI policy with compute access, safety frameworks, and sector pilots — positioning AI as a strategic pillar of the national digital economy.',
    'India''s AI ecosystem has grown rapidly since 2023, with domestic startups, IIT research labs, and enterprise teams deploying AI systems across finance, healthcare, and agriculture. The absence of a national framework had created fragmentation in regulation, infrastructure access, and data governance.',
    'On April 5, 2026, the government launched the National AI Mission with four pillars: a national compute and data infrastructure program; responsible AI guidelines covering transparency, accountability, and privacy; priority sector pilots in healthcare, agriculture, education, public services, and language technology; and a startup and research funding program backed by ₹10,000 crore over five years.',
    E'National AI compute infrastructure: sovereign GPU clusters accessible to startups, universities, and government agencies\nResponsible AI framework: mandatory transparency and explainability standards for high-impact AI systems\nPriority pilots: AI diagnostic tools in 500 district hospitals; crop advisory systems for 10 million farmers\nLanguage AI: dedicated program for 22 scheduled languages and 100+ regional dialects\n₹10,000 crore funding over 5 years for deep-tech startups, academic labs, and public-private partnerships',
    'The policy provides a unified framework that reduces infrastructure barriers for AI development in India. For startups and enterprises, it signals stronger government demand for locally relevant, explainable AI systems. For international players, it sets compliance expectations and market access conditions.',
    'Implementation committees are being formed across eight ministries. Sector-specific pilot programs will launch within 90 days. The responsible AI standards will be open for public consultation before being finalised by end of 2026.',
    TRUE,
    ARRAY['Technology', 'Policy', 'Artificial Intelligence', 'Digital India'],
    'Position India as a global leader in trusted, inclusive AI that solves local problems at national scale while building a sovereign AI capability not dependent on any single foreign technology stack.',
    'Compute program launches in Q3 2026 with 10,000 H100-equivalent GPU hours available to registered researchers and startups. Responsible AI certification will be required for government procurement of AI systems by January 2027. First pilot outcomes expected Q4 2026.',
    NULL,
    'enriched'
);

-- Events for Story 3
INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-03-20 09:00:00+00',
    'Draft policy circulated to ministries for review',
    'The Ministry of Electronics and IT circulated a draft National AI Mission document to eight ministries for feedback. The draft outlined four strategic pillars and proposed a ₹10,000 crore budget over five years.',
    NULL, 1
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-05 10:00:00+00',
    'National AI Mission officially announced',
    'Prime Minister announced the National AI Mission at a national technology summit in New Delhi. The policy was framed around four pillars: sovereign compute, responsible AI, sector pilots, and startup funding. Industry associations and AI researchers responded positively.',
    NULL, 2
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';

INSERT INTO timeline_events (post_id, event_time, event_title, event_content, event_image_url, sequence_order)
SELECT id, '2026-04-18 11:00:00+00',
    'Implementation committees formed; sector pilots identified',
    'The government constituted eight ministry-level implementation committees. Priority pilot sectors were confirmed: district hospital AI diagnostics, farmer crop advisory systems, multilingual government services, and AI-assisted tax compliance tools.',
    NULL, 3
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';

-- Quotes for Story 3
INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, 'Artificial intelligence must become a force multiplier for every citizen, every startup, and every public service in India.', 'Prime Minister of India', 1
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';

INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, 'India''s AI opportunity depends on trust, access, and strong research capacity. This policy addresses all three.', 'NITI Aayog CEO', 2
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';

-- Comments for Story 3 (mock)
INSERT INTO timeline_comments (post_id, comment_text, commenter_name, commenter_designation, commenter_image_url, is_mock, display_order)
SELECT id, 'The compute access program is the most critical piece. Indian startups have been constrained by GPU scarcity — this changes the economics of building foundation models domestically.', 'Priya Subramaniam', 'AI Startup Founder & YC Alumni', NULL, TRUE, 1
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';

INSERT INTO timeline_comments (post_id, comment_text, commenter_name, commenter_designation, commenter_image_url, is_mock, display_order)
SELECT id, 'The language AI program is what excites me most. 22 scheduled languages and 100+ dialects — if executed well, this could be the world''s most inclusive multilingual AI initiative.', 'Dr. Vikram Nair', 'Computational Linguistics, IIT Madras', NULL, TRUE, 2
FROM timeline_posts WHERE article_id = 'mock-india-ai-policy-001';
