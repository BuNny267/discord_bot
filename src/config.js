require('dotenv').config();

module.exports = {
  token: process.env.BOT_TOKEN,
  clientId: process.env.CLIENT_ID,
  guildId: process.env.GUILD_ID || null,
  dbPath: process.env.DB_PATH || './data/bot.sqlite',
  defaultTimeoutMs: 10 * 60 * 1000,
  panelTheme: {
    main: 0x2b2d31,
    good: 0x57f287,
    warn: 0xfee75c,
    bad: 0xed4245,
    info: 0x5865f2
  }
};
