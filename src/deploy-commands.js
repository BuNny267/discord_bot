const fs = require('fs');
const path = require('path');
const { REST, Routes } = require('discord.js');
const { token, clientId, guildId } = require('./config');
const commands=[]; for(const f of fs.readdirSync(path.join(__dirname,'commands')).filter(x=>x.endsWith('.js'))){commands.push(require(path.join(__dirname,'commands',f)).data.toJSON());}
const rest=new REST({version:'10'}).setToken(token);
(async()=>{if(guildId) await rest.put(Routes.applicationGuildCommands(clientId,guildId),{body:commands}); else await rest.put(Routes.applicationCommands(clientId),{body:commands}); console.log(`Registered ${commands.length} commands.`)})();
