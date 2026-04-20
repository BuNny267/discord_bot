SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS plugins (
    name TEXT PRIMARY KEY,
    enabled INTEGER DEFAULT 1,
    version TEXT DEFAULT '1.0.0',
    hidden INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS auto_replies (
    trigger TEXT PRIMARY KEY,
    response TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS welcome_settings (
    guild_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    channel_id INTEGER,
    message TEXT,
    embed_enabled INTEGER DEFAULT 1,
    image_url TEXT,
    attach_image INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id INTEGER PRIMARY KEY,
    bot_channel_id INTEGER,
    log_channel_id INTEGER,
    automod_log_channel_id INTEGER,
    mod_log_channel_id INTEGER,
    welcome_channel_id INTEGER,
    moderation_channel_id INTEGER,
    config_channel_id INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS role_settings (
    guild_id INTEGER NOT NULL,
    role_name TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    enabled INTEGER DEFAULT 1,
    PRIMARY KEY (guild_id, role_name)
);
CREATE TABLE IF NOT EXISTS log_channels (
    guild_id INTEGER PRIMARY KEY,
    automod_log_channel_id INTEGER,
    mod_log_channel_id INTEGER,
    join_leave_log_channel_id INTEGER,
    message_log_channel_id INTEGER,
    role_log_channel_id INTEGER,
    plugin_log_channel_id INTEGER,
    form_log_channel_id INTEGER,
    ticket_log_channel_id INTEGER,
    appeal_log_channel_id INTEGER,
    transcript_log_channel_id INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    guild_id INTEGER,
    channel_id INTEGER,
    user_id INTEGER,
    data TEXT NOT NULL,
    delivered INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS automod_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    rule_type TEXT NOT NULL,
    rule_data TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS automod_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER,
    channel_id INTEGER,
    rule_name TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS moderation_cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reason TEXT,
    duration TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS moderation_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS form_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    target_channel_id INTEGER NOT NULL,
    log_channel_id INTEGER,
    fields_json TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS form_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    message_id INTEGER,
    status TEXT DEFAULT 'submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticket_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    channel_id INTEGER,
    role_id INTEGER,
    enabled INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    channel_id INTEGER,
    status TEXT DEFAULT 'open',
    claimed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS appeals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    case_id INTEGER,
    appeal_text TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    reviewer_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reaction_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    emoji TEXT NOT NULL,
    enabled INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS leveling_settings (
    guild_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    xp_per_message INTEGER DEFAULT 5,
    cooldown_seconds INTEGER DEFAULT 60,
    announce_levelup INTEGER DEFAULT 1,
    levelup_channel_id INTEGER,
    role_rewards_json TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS user_xp (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    PRIMARY KEY (guild_id, user_id)
);
CREATE TABLE IF NOT EXISTS custom_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    response TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embed_json TEXT,
    schedule_type TEXT NOT NULL,
    schedule_value TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    last_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS quote_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER,
    channel_id INTEGER,
    message_id INTEGER,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS bot_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
