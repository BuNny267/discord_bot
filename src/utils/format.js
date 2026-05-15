function msToTime(ms){if(ms==null)return'Permanent';const s=Math.floor(ms/1000),d=Math.floor(s/86400),h=Math.floor((s%86400)/3600),m=Math.floor((s%3600)/60);return [d&&`${d}d`,h&&`${h}h`,m&&`${m}m`].filter(Boolean).join(' ')||'0s'}
module.exports={msToTime};
