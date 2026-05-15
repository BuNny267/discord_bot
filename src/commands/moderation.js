const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
module.exports={data:new SlashCommandBuilder().setName('moderation').setDescription('Open moderation dashboard').setDMPermission(false),async execute(i){return i.reply({ephemeral:true,embeds:[new EmbedBuilder().setColor(0x2b2d31).setTitle('Moderation Dashboard')]})}};
