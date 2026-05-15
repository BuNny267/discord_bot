const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');
const { dbPath } = require('./config');

fs.mkdirSync(path.dirname(dbPath), { recursive: true });

const db = new Database(dbPath);
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

const DEFAULT_SETTINGS = {
  automod: {
    enabled: false,
    antiSpam: false,
    antiLink: false,
    antiInvite: false,
    antiMassMention: false,
    capsFilter: false,
    emojiSpamFilter: false,
    attachmentRestriction: false,
    punishment: 'timeout',
    timeoutMs: 10 * 60 * 1000,
    whitelistChannelIds: [],
    whitelistRoleIds: [],
    maxMentions: 5,
    maxCapsRatio: 0.7,
    maxEmojiCount: 8,
    maxAttachments: 1
  },
  logs: {
    modLogChannelId: null,
    automodLogChannelId: null,
    joinLeaveLogChannelId: null,
    messageDeleteLogChannelId: null,
    messageEditLogChannelId: null,
    logJoin: false,
    logLeave: false,
    logMessageDelete: false,
    logMessageEdit: false
  },
  security: {
    enabled: false,
    lockdown: false,
    jailRoleId: null,
    trustedRoleIds: [],
    trustedChannelIds: []
  },
  moderation: {
    defaultTimeoutMs: 10 * 60 * 1000
  }
};

function init() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS guild_settings (
      guild_id TEXT PRIMARY KEY,
      data TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS blocked_words (
      guild_id TEXT NOT NULL,
      word TEXT NOT NULL,
      PRIMARY KEY (guild_id, word)
    );

    CREATE TABLE IF NOT EXISTS regex_filters (
      guild_id TEXT NOT NULL,
      pattern TEXT NOT NULL,
      PRIMARY KEY (guild_id, pattern)
    );

    CREATE TABLE IF NOT EXISTS cases (
      case_id INTEGER PRIMARY KEY AUTOINCREMENT,
      guild_id TEXT NOT NULL,
      user_id TEXT NOT NULL,
      moderator_id TEXT NOT NULL,
      action TEXT NOT NULL,
      reason TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active',
      duration_ms INTEGER DEFAULT NULL,
      dm_status TEXT DEFAULT 'unknown',
      appeal_status TEXT DEFAULT 'none',
      meta TEXT DEFAULT '{}',
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS punishments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      guild_id TEXT NOT NULL,
      user_id TEXT NOT NULL,
      case_id INTEGER NOT NULL,
      type TEXT NOT NULL,
      active INTEGER NOT NULL DEFAULT 1,
      expires_at INTEGER DEFAULT NULL,
      reason TEXT NOT NULL,
      moderator_id TEXT NOT NULL,
      dm_status TEXT DEFAULT 'unknown',
      meta TEXT DEFAULT '{}',
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      FOREIGN KEY(case_id) REFERENCES cases(case_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_trail (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      guild_id TEXT NOT NULL,
      moderator_id TEXT NOT NULL,
      action TEXT NOT NULL,
      details TEXT NOT NULL,
      created_at INTEGER NOT NULL
    );
  `);
}

const now = () => Date.now();

function deepMerge(base, patch) {
  const out = Array.isArray(base) ? [...base] : { ...base };
  for (const [k, v] of Object.entries(patch || {})) {
    if (v && typeof v === 'object' && !Array.isArray(v) && base[k] && typeof base[k] === 'object' && !Array.isArray(base[k])) out[k] = deepMerge(base[k], v);
    else out[k] = v;
  }
  return out;
}

function getGuildSettings(guildId) {
  const row = db.prepare('SELECT data FROM guild_settings WHERE guild_id = ?').get(guildId);
  if (!row) {
    saveGuildSettings(guildId, DEFAULT_SETTINGS);
    return JSON.parse(JSON.stringify(DEFAULT_SETTINGS));
  }
  return deepMerge(JSON.parse(JSON.stringify(DEFAULT_SETTINGS)), JSON.parse(row.data));
}
function saveGuildSettings(guildId, settings) {
  db.prepare(`INSERT INTO guild_settings (guild_id, data) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET data = excluded.data`).run(guildId, JSON.stringify(settings));
  return settings;
}
function patchGuildSettings(guildId, patch) {
  const updated = deepMerge(getGuildSettings(guildId), patch);
  saveGuildSettings(guildId, updated);
  return updated;
}
function addBlockedWord(guildId, word) { db.prepare('INSERT OR IGNORE INTO blocked_words (guild_id, word) VALUES (?, ?)').run(guildId, word); }
function removeBlockedWord(guildId, word) { db.prepare('DELETE FROM blocked_words WHERE guild_id = ? AND word = ?').run(guildId, word); }
function clearBlockedWords(guildId) { db.prepare('DELETE FROM blocked_words WHERE guild_id = ?').run(guildId); }
function listBlockedWords(guildId) { return db.prepare('SELECT word FROM blocked_words WHERE guild_id = ? ORDER BY word ASC').all(guildId).map(r => r.word); }
function addRegex(guildId, pattern) { db.prepare('INSERT OR IGNORE INTO regex_filters (guild_id, pattern) VALUES (?, ?)').run(guildId, pattern); }
function removeRegex(guildId, pattern) { db.prepare('DELETE FROM regex_filters WHERE guild_id = ? AND pattern = ?').run(guildId, pattern); }
function clearRegex(guildId) { db.prepare('DELETE FROM regex_filters WHERE guild_id = ?').run(guildId); }
function listRegex(guildId) { return db.prepare('SELECT pattern FROM regex_filters WHERE guild_id = ? ORDER BY pattern ASC').all(guildId).map(r => r.pattern); }

function createCase({ guildId, userId, moderatorId, action, reason, durationMs = null, dmStatus = 'unknown', appealStatus = 'none', meta = {} }) {
  const ts = now();
  const result = db.prepare(`INSERT INTO cases (guild_id, user_id, moderator_id, action, reason, status, duration_ms, dm_status, appeal_status, meta, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)`).run(guildId, userId, moderatorId, action, reason, durationMs, dmStatus, appealStatus, JSON.stringify(meta), ts, ts);
  return { caseId: result.lastInsertRowid, caseTag: `CASE-${String(result.lastInsertRowid).padStart(6, '0')}` };
}
function getCase(caseId) { return db.prepare('SELECT * FROM cases WHERE case_id = ?').get(caseId); }
function updateCase(caseId, patch) {
  const current = getCase(caseId); if (!current) return null;
  const merged = { ...current, ...patch, updated_at: now() };
  db.prepare(`UPDATE cases SET user_id = ?, moderator_id = ?, action = ?, reason = ?, status = ?, duration_ms = ?, dm_status = ?, appeal_status = ?, meta = ?, updated_at = ? WHERE case_id = ?`).run(merged.user_id, merged.moderator_id, merged.action, merged.reason, merged.status, merged.duration_ms, merged.dm_status, merged.appeal_status, merged.meta, merged.updated_at, caseId);
  return merged;
}
function listCasesByGuild(guildId, limit = 15, offset = 0) { return db.prepare('SELECT * FROM cases WHERE guild_id = ? ORDER BY case_id DESC LIMIT ? OFFSET ?').all(guildId, limit, offset); }
function listActivePunishments(guildId) { return db.prepare('SELECT * FROM punishments WHERE guild_id = ? AND active = 1 ORDER BY id DESC LIMIT 50').all(guildId); }
function createPunishment({ guildId, userId, caseId, type, reason, moderatorId, expiresAt = null, dmStatus = 'unknown', meta = {} }) {
  const ts = now();
  return db.prepare(`INSERT INTO punishments (guild_id, user_id, case_id, type, active, expires_at, reason, moderator_id, dm_status, meta, created_at, updated_at) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)`).run(guildId, userId, caseId, type, expiresAt, reason, moderatorId, dmStatus, JSON.stringify(meta), ts, ts);
}
function updatePunishmentActiveByCase(caseId, active, extra = {}) {
  const row = db.prepare('SELECT * FROM punishments WHERE case_id = ?').get(caseId); if (!row) return null;
  db.prepare('UPDATE punishments SET active = ?, dm_status = ?, meta = ?, updated_at = ? WHERE case_id = ?').run(active ? 1 : 0, extra.dmStatus ?? row.dm_status, extra.meta ? JSON.stringify(extra.meta) : row.meta, now(), caseId);
  return db.prepare('SELECT * FROM punishments WHERE case_id = ?').get(caseId);
}
function addAudit(guildId, moderatorId, action, details) { db.prepare('INSERT INTO audit_trail (guild_id, moderator_id, action, details, created_at) VALUES (?, ?, ?, ?, ?)').run(guildId, moderatorId, action, JSON.stringify(details ?? {}), now()); }
function listAudit(guildId, limit = 50, offset = 0) { return db.prepare('SELECT * FROM audit_trail WHERE guild_id = ? ORDER BY id DESC LIMIT ? OFFSET ?').all(guildId, limit, offset); }

init();
module.exports = { db, DEFAULT_SETTINGS, getGuildSettings, saveGuildSettings, patchGuildSettings, addBlockedWord, removeBlockedWord, clearBlockedWords, listBlockedWords, addRegex, removeRegex, clearRegex, listRegex, createCase, getCase, updateCase, listCasesByGuild, createPunishment, listActivePunishments, updatePunishmentActiveByCase, addAudit, listAudit };
