from discord.ext import commands
from datetime import datetime
import copy

class TrickTwitchCustomRolesUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def role_delete_cleanup(self, discord_id, role_id, expired):   
        """ Deletes the role and calls functions to remove it from dictionary and mongoDB """
        guild = self.bot.Tricked_guild_instance
        member = guild.get_member(discord_id)
        role = guild.get_role(role_id)
        
        await self.remove_role_from_dictionary(discord_id, role_id) #remove from dictionary
        await self.remove_role_from_mongoDB(discord_id, role_id) #remove from mongoDB

        if role is not None: #If the role exists
            await role.delete(reason="Custom Twitch Role")
            print(f"deleted {role}")
            await self.announce_role_delete(member, role.name, expired)

    async def remove_role_from_dictionary(self, discord_id, role_id):
        """ Remove the role from dictioanry """
        def find_and_remove_role(self, discord_id, role_id):
            for discordID, roleList in list(self.bot.TrickTwitch_CustomRoles_Dict.items()):
                if discordID == discord_id:
                    index = 0
                    for roleID in roleList:
                        if roleID == role_id:
                            del self.bot.TrickTwitch_CustomRoles_Dict[discordID][index]
                            return True                        
                        index += 1
            return False
        val = find_and_remove_role(self, discord_id, role_id)
        if not val:
            print(f"Role did not exist in dictionary with discord_id: {discord_id} and role_id: {role_id}")
        else:
            print(f"Removed role from dictionary with discord_id: {discord_id} and role_id: {role_id}")

    async def remove_role_from_mongoDB(self, discord_id, role_id):
        """ Removes the role from mongoDB """
        result = await self.bot.db["trick-twitch"].update_one( {"discord_id": discord_id}, { '$pull': { 'roles': role_id }}) #remove the correct role id
        if (result.modified_count==0):
            print(f"Role did not exist in mongo with discord_id: {discord_id} and role_id: {role_id}")
        elif (result.modified_count==1):
            print(f"Removed role from mongo with discord_id: {discord_id} and role_id: {role_id}")

    async def announce_role_delete(self, member, role_name, expired):
        """ Logs when a role expires and can tell the role owner """
        if expired and member is not None:
            try:
                await member.send(f"Your custom Twitch role **{role_name}** has expired as it has been more than 2 months since you redeemed it.")
            except: #cannot message member
                pass
        if expired:
            await self.bot.twitch_role_log_channel.send(f"Custom Twitch role **{role_name}** has expired as it has been more than 2 months since it " 
                                                        f"was redeemed by {member}")

    async def check_any_role_expired(self):        
        """ Check if any custom twitch role has expired (if created over 2 months ago) """
        time_now = datetime.utcnow()
        time_now_unixTimeStamp = int(time_now.timestamp())
        guild = self.bot.Tricked_guild_instance
        for discordID, roleList in list(self.bot.TrickTwitch_CustomRoles_Dict.items()):
            for roleID in copy.deepcopy(roleList):
                role_instance = guild.get_role(int(roleID))
                if role_instance is not None:
                    role_creation = role_instance.created_at
                    roleCreatedAt = int(role_creation.timestamp())
                    if (time_now_unixTimeStamp - roleCreatedAt) > 5274000: #seconds in two months 
                        print(f"role expired...deleting ({roleID})")
                        await self.role_delete_cleanup(discordID, roleID, True)
                    else:
                        print(f"role not expired ({roleID}). Created {time_now_unixTimeStamp - roleCreatedAt} seconds ago. Needs to reach 5274000 to expire")

def setup(bot):
    bot.add_cog(TrickTwitchCustomRolesUtil(bot))