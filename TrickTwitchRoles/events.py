from discord.ext import commands
import discord
import copy

class TrickTwitchCustomRolesEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #//public enum {}

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """ If a role is deleted in Tricked and is a custom twitch role and was not deleted by Tricked Bot """
        guild = self.bot.Tricked_guild_instance
        if role.guild.id != guild.id: return
        for discordID, roleList in list(self.bot.TrickTwitch_CustomRoles_Dict.items()):
            for roleID in copy.deepcopy(roleList):
                if roleID == role.id:
                    async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
                        if entry.target.id == role.id:
                            member = guild.get_member(int(discordID))
                            deleted_by = entry.user
                            if deleted_by.id != self.bot.user.id:
                                await self.bot.getTwitchRoleUtil.role_delete_cleanup(discordID, role.id, False) 
                                await self.bot.twitch_role_log_channel.send(f"{member}'s custom Twitch role with name **{role.name}** got deleted by {deleted_by}!")
                                break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """ When a member leaves Tricked check if they have any custom twitch roles. If so delete them."""
        guild = self.bot.Tricked_guild_instance
        if member.guild.id != guild.id: return
        if member.id in self.bot.TrickTwitch_CustomRoles_Dict:
            roleList = self.bot.TrickTwitch_CustomRoles_Dict[member.id]            
            for roleID in copy.deepcopy(roleList):
                role_instance = guild.get_role(int(roleID))
                if role_instance is not None:
                    await self.bot.getTwitchRoleUtil.role_delete_cleanup(member.id, role_instance.id, False) 
                    await self.bot.twitch_role_log_channel.send(f"{member} has left the server so their **{role_instance.name}** role has been deleted.")
        

def setup(bot):
    bot.add_cog(TrickTwitchCustomRolesEvents(bot))