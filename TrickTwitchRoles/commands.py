from discord.ext import commands
from discord.ext.commands import BucketType
from discord_slash import cog_ext

class TrickTwitchCustomRolesCommandsV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def delrole(self, ctx, discord_id, role_ID):
        print(self.bot.TrickTwitch_CustomRoles_Dict)
        await self.bot.getTwitchRoleUtil.role_delete_cleanup(int(discord_id), int(role_ID))
        print(self.bot.TrickTwitch_CustomRoles_Dict)

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def checkexpired(self, ctx):
        print(self.bot.TrickTwitch_CustomRoles_Dict)
        await self.bot.getTwitchRoleUtil.check_any_role_expired()
        print(self.bot.TrickTwitch_CustomRoles_Dict)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1,1, BucketType.user)
    async def redeem(self, ctx, user=None):
        """ Allows the user to create another custom twitch role """
        await self.bot.getTwitchRoleUtil.check_any_role_expired() #check if any roles expired
        twitchMod = False
        for role in ctx.author.roles:
            if role.id == self.bot.twitch_mod_id: #twitch mod
                twitchMod = True
        if twitchMod == False: return await ctx.send("You must be a twitch mod to use this.")
        if user == None: return await ctx.send("Please enter a user to grant a custom role to.")
        user = user.replace("<","")
        user = user.replace("@","")
        user = user.replace(">","")
        user = user.replace("!","")
        user = user.replace("?","")
        try: user = int(user)
        except: return await ctx.send("Invalid user.")
        if ctx.guild.get_member(user) == None: return await ctx.send("Invalid user.")
        user_id = user
        if user_id in self.bot.TrickTwitch_CustomRoles_RedeemedUserList: return await ctx.send("This user can already create a role using **/trick**.")
        self.bot.TrickTwitch_CustomRoles_RedeemedUserList.append(user_id)
        await ctx.send("This user can now create a custom role using **/trick**.")
        print(self.bot.TrickTwitch_CustomRoles_RedeemedUserList)

    @commands.command(name="trick")
    @commands.guild_only()
    @commands.cooldown(1,1,BucketType.user)
    async def trick_normal_command(self, ctx):
        """ Normal message content based command"""
        await self.trick_command(ctx, False)

    @cog_ext.cog_slash(name="trick",
                guild_ids=[643397747986268164],
                description="Create and manage your custom roles redeemed from YouGotTricked's streams.")
    async def trick_slash_command(self, ctx):
        """ Discord Slash command"""
        await self.trick_command(ctx, True)

    async def trick_command(self, ctx, slash):
        """ Create and manage up to 5 custom twitch roles """
        guild = self.bot.Tricked_guild_instance
        if ctx.guild.id != guild.id: return
   
        #print(f"roles: {self.bot.TrickTwitch_CustomRoles_Dict}")
        #print(f"eligible users: {self.bot.TrickTwitch_CustomRoles_RedeemedUserList}")
        #print(f"ongoing: {self.bot.Ongoing_TrickTwitch_CustomRoles}")

        # If ongoing role creation: return
        if ctx.author.id in self.bot.Ongoing_TrickTwitch_CustomRoles: 
            if slash: return await ctx.reply(embed=self.bot.getTwitchEmbed.ongoing(ctx.author.id))
            else: return await ctx.reply(embed=self.bot.getTwitchEmbed.ongoing(ctx.author.id), mention_author=False)

        home_embed = self.bot.getTwitchEmbed.home(ctx.author)
        home_components = self.bot.getTwitchComponent.home()
        home_embed_finish = self.bot.getTwitchEmbed.home(ctx.author, True)        
        if slash: start_message = await ctx.reply(embed=home_embed, components=[home_components])
        else: start_message = await ctx.reply(embed=home_embed, mention_author=False, components=[home_components])
        self.bot.Ongoing_TrickTwitch_CustomRoles[ctx.author.id] = start_message.jump_url #add to ongoing dict

        while True:
            returnVal = await self.bot.getTwitchCommandUtil.wait_for_member(ctx.author.id, start_message, home_components)
            if returnVal == False: 
                del self.bot.Ongoing_TrickTwitch_CustomRoles[ctx.author.id]
                return await start_message.edit(embed = home_embed_finish, components=[])
            else:
                button_ctx = returnVal
                if button_ctx.custom_id == "create":
                    if ctx.author.id in self.bot.TrickTwitch_CustomRoles_Dict and len(self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id]) >= 4: await button_ctx.send(embed=self.bot.getTwitchEmbed.max(), hidden=True)
                    else: await self.bot.getTwitchCommandUtil.create_role(ctx, button_ctx, start_message)

                elif button_ctx.custom_id == "edit":
                    await self.bot.getTwitchCommandUtil.edit_role(ctx, button_ctx, start_message)

                elif button_ctx.custom_id == "cancel":
                    del self.bot.Ongoing_TrickTwitch_CustomRoles[ctx.author.id]
                    return await button_ctx.edit_origin(embed = home_embed_finish, components=[])
                await start_message.edit(embed=home_embed, components=[home_components])

def setup(bot):
    bot.add_cog(TrickTwitchCustomRolesCommandsV2(bot))