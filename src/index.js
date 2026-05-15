const fs = require('fs');
const path = require('path');
const { Client, GatewayIntentBits, Partials, Collection, Events } = require('discord.js');
const { token } = require('./config');
require('./db');

const client = new Client({ intents:[GatewayIntentBits.Guilds,GatewayIntentBits.GuildMembers,GatewayIntentBits.GuildMessages,GatewayIntentBits.MessageContent,GatewayIntentBits.GuildModeration], partials:[Partials.Channel,Partials.Message,Partials.GuildMember,Partials.User]});
client.commands = new Collection();
for (const file of fs.readdirSync(path.join(__dirname,'commands')).filter(f=>f.endsWith('.js'))) {
  const cmd = require(path.join(__dirname,'commands',file));
  client.commands.set(cmd.data.name, cmd);
}
client.on(Events.InteractionCreate, async (interaction)=>{ if(!interaction.isChatInputCommand()) return; const cmd=client.commands.get(interaction.commandName); if(!cmd) return; try{ await cmd.execute(interaction);}catch(e){ if(interaction.replied||interaction.deferred) await interaction.followUp({ephemeral:true,content:`Error: ${e.message}`}); else await interaction.reply({ephemeral:true,content:`Error: ${e.message}`}); }});
client.once(Events.ClientReady,()=>console.log(`Logged in as ${client.user.tag}`));
client.login(token);
