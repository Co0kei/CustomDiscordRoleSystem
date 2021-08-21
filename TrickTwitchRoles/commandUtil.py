import discord
from discord.ext import commands
from datetime import datetime
import string
from discord_slash.utils.manage_components import wait_for_component
import re
from dateutil.relativedelta import relativedelta
import traceback

class TrickTwitchCustomRolesCommandUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timeout = 30

    async def wait_for_member(self, author_id, start_message, component):
        """ Check only user that ran the command can use the components """
        def check(component): return component.origin_message_id == start_message.id
        while True:
            try: button_ctx = await wait_for_component(self.bot, components=component, check=check, timeout=self.timeout)
            except: return False
            else:
                if author_id != button_ctx.author.id: await button_ctx.send("You cannot use this. Use `/trick` to start your own session.", hidden=True)
                else: return button_ctx

    async def create_role(self, ctx, button_ctx, start_message):
        """ Method to handle creating a custom role """
        if ctx.author.id not in self.bot.TrickTwitch_CustomRoles_RedeemedUserList:
            await button_ctx.send(embed=self.bot.getTwitchEmbed.redeem(), hidden=True)
            return False
        #enter role name
        returnState = await self.role_name(ctx, button_ctx, start_message)
        if returnState == False: return #timeout
        else: role_name = returnState
        #choose colour
        returnState = await self.role_colour(ctx, start_message)
        if returnState == False: return #timeout
        else: role_colour = returnState
        #role confirmation creation (create OR cancel)
        confirm_embed = self.bot.getTwitchEmbed.confirm(role_name, role_colour)
        confirm_components = self.bot.getTwitchComponent.confirm()
        await start_message.edit(embed=confirm_embed, components=[confirm_components])
        returnVal = await self.wait_for_member(ctx.author.id, start_message, confirm_components)
        if returnVal == False: return False
        else: button_ctx = returnVal
        if button_ctx.custom_id == "cancel": 
            home_embed = self.bot.getTwitchEmbed.home(ctx.author)
            home_components = self.bot.getTwitchComponent.home()
            await button_ctx.edit_origin(embed=home_embed, components=[home_components])
            return False
        #await button_ctx.defer(edit_origin=True)
        #disabled_components = self.bot.getTwitchComponent.confirm(True)
        #await start_message.edit(components=[disabled_components])
        #create role
        try:
            role = await ctx.guild.create_role(name=role_name, colour=role_colour, reason=f"Custom Twitch role for {ctx.author}")
            await ctx.author.add_roles(role, reason="Custom Twitch Role")
            try:
                position = int(ctx.author.top_role.position) + 1
                await role.edit(position=position)
            except: pass
            two_months = datetime.utcnow() + relativedelta(months=+2)
            unixTimeStamp = int(two_months.timestamp())
            received_embed = self.bot.getTwitchEmbed.received(role.mention, unixTimeStamp, role_colour)
            received_components = self.bot.getTwitchComponent.received()
            await button_ctx.edit_origin(embed=received_embed, components=[received_components])
            #update to mongoDB
            result = await self.bot.db["trick-twitch"].update_one( {"discord_id": ctx.author.id}, { '$push': { 'roles': role.id }}, upsert = True) #remove the correct role id
            #add to dictionary
            if ctx.author.id in self.bot.TrickTwitch_CustomRoles_Dict:
                roleList = self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id]
                roleList.append(role.id)
                self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id] = roleList
            else: self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id] = [role.id]
            self.bot.TrickTwitch_CustomRoles_RedeemedUserList.remove(ctx.author.id) #remove user from redeemed user list
        except Exception as e:
            print(e)
            error_menu = discord.Embed(description="<:cross:872834807476924506> There was an error creating your role. Please try again.", colour=self.bot.twitch_embed_colour)
            await button_ctx.send(embed = error_menu)
            return False
        #received message components
        returnVal = await self.wait_for_member(ctx.author.id, start_message, received_components)
        if returnVal == False: return False
        else: button_ctx = returnVal
        await button_ctx.edit_origin(embed=received_embed, components=[received_components])

    async def edit_role(self, ctx, button_ctx, start_message):
        """ Method to edit one of a member's Custom Twitch Roles """
        if ctx.author.id not in self.bot.TrickTwitch_CustomRoles_Dict or self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id] == []:
            await button_ctx.send(embed=self.bot.getTwitchEmbed.no_roles(), hidden=True)
            return False
        numOfRoles = len(self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id])
        #choose role to edit menu
        choose_role_edit_embed = self.bot.getTwitchEmbed.choose_edit(ctx.author.id)
        choose_role_edit_components = self.bot.getTwitchComponent.choose_edit(numOfRoles)
        await button_ctx.edit_origin(embed = choose_role_edit_embed, components=[choose_role_edit_components])
        returnVal = await self.wait_for_member(ctx.author.id, start_message, choose_role_edit_components)
        if returnVal == False: return False
        else: button_ctx = returnVal
        if button_ctx.custom_id == "main":
            home_embed = self.bot.getTwitchEmbed.home(ctx.author)
            home_components = self.bot.getTwitchComponent.home()
            await button_ctx.edit_origin(embed=home_embed, components=[home_components])
            return False
        list_index = int(button_ctx.custom_id)
        #get role info
        role_id = self.bot.TrickTwitch_CustomRoles_Dict[ctx.author.id][list_index]
        guild = self.bot.Tricked_guild_instance
        role = guild.get_role(role_id)
        role_colour = role.colour
        unixTimeStamp = int((role.created_at + relativedelta(months=+2)).timestamp())
        edit_embed = self.bot.getTwitchEmbed.edit(role.mention, unixTimeStamp, role_colour)
        edit_components = self.bot.getTwitchComponent.edit()
        await button_ctx.edit_origin(embed=edit_embed, components=[edit_components])
        while True:
            edited_msg = ""
            returnVal = await self.wait_for_member(ctx.author.id, start_message, edit_components)
            if returnVal == False: return False
            else:
                button_ctx = returnVal

                if button_ctx.custom_id == "name":
                    returnState = await self.role_name(ctx, button_ctx, start_message)
                    if returnState == False:  pass
                    else: 
                        role_name = returnState
                        try:
                            await role.edit(name=role_name)
                            edited_msg = f"**Updated role name to `{role_name}`**"
                        except Exception as e:
                            print(traceback.print_exc())
                            error_menu = discord.Embed(description="<:cross:872834807476924506> There was an error changing your role name. Please check the characters.", colour=self.bot.twitch_embed_colour)
                            await ctx.send(embed=error_menu, components=[], delete_after=3)
                    
                elif button_ctx.custom_id == "colour": 
                    colour_embed = self.bot.getTwitchEmbed.role_colour()
                    colour_dropdown = self.bot.getTwitchComponent.role_colour()
                    await button_ctx.edit_origin(embed=colour_embed,components=[colour_dropdown])
                    returnState = await self.role_colour(ctx, start_message)
                    if returnState == False:  pass
                    else: 
                        role_colour = returnState
                        try:
                            await role.edit(colour=role_colour)
                            edited_msg = f"**Updated role colour to `{role_colour}`**"
                        except Exception as e:
                            print(traceback.print_exc())
                            error_menu = discord.Embed(description="<:cross:872834807476924506> There was an error changing your role colour. Please check the hex code.", colour=self.bot.twitch_embed_colour)
                            await ctx.send(embed=error_menu, components=[], delete_after=3)
                
                elif button_ctx.custom_id == "pos":
                    if ctx.author.top_role == role:
                        error_menu = discord.Embed(description="<:cross:872834807476924506> This is already your highest role!", colour=self.bot.twitch_embed_colour)
                        await button_ctx.send(embed=error_menu, components=[], delete_after=3)
                    else:
                        try:
                            position = int(ctx.author.top_role.position) + 1
                            await role.edit(position=position)
                            edited_msg = f"**Updated role position to `your top role` (This can be very temperamental)**"
                            await button_ctx.edit_origin(embed=edit_embed,components=[edit_components])
                        except Exception as e:
                            print(traceback.print_exc())
                            error_menu = discord.Embed(description="<:cross:872834807476924506> There was an error moving your role.", colour=self.bot.twitch_embed_colour)
                            await button_ctx.send(embed=error_menu, components=[], delete_after=3)

                elif button_ctx.custom_id == "delete": 
                    options = ["yes","y","no","n"]
                    def resetCheck(m):
                        return m.content.lower() in options and m.channel == ctx.channel and m.author == ctx.author
                    response = await button_ctx.send("**:warning: You are about to delete your custom role. Continue? (yes/no)**")
                    try:
                        UserReply = await self.bot.wait_for('message', timeout = 10.0, check=resetCheck)
                    except: await response.delete()
                    else: #if they reply with yes or no
                        if UserReply.content.lower() == "yes" or UserReply.content.lower() == "y":  
                            try:                            
                                await self.bot.getTwitchRoleUtil.role_delete_cleanup(ctx.author.id, role_id, False) 
                                await ctx.channel.delete_messages([response,UserReply])
                                #edited_msg = f"**You `deleted` your role!**"
                                error_menu = discord.Embed(description="**You `deleted` your role!**", colour=self.bot.twitch_embed_colour)
                                await ctx.send(embed=error_menu, components=[], delete_after=3)
                                return False                                
                            except:
                                error_menu = discord.Embed(description="<:cross:872834807476924506> There was an error deleting your role.", colour=self.bot.twitch_embed_colour)
                                await ctx.send(embed=error_menu, components=[], delete_after=3)
                        else:
                            error_menu = discord.Embed(description="<:cross:872834807476924506> Reset aborted!", colour=self.bot.twitch_embed_colour)
                            await ctx.send(embed=error_menu, components=[], delete_after=3)
                        await ctx.channel.delete_messages([response,UserReply])
                elif button_ctx.custom_id == "main": 
                    home_embed = self.bot.getTwitchEmbed.home(ctx.author)
                    home_components = self.bot.getTwitchComponent.home()
                    await button_ctx.edit_origin(embed=home_embed, components=[home_components])
                    return False
                edit_embed = self.bot.getTwitchEmbed.edit(role.mention, unixTimeStamp, role_colour, edited_msg)
                await start_message.edit(embed=edit_embed, components=[edit_components])

    async def role_name(self, ctx, button_ctx, start_message):
        """ Method that returns False for a timeout or returns a valid role name"""
        name_embed = self.bot.getTwitchEmbed.role_name()        
        await button_ctx.edit_origin(content=None, embed=name_embed,components=[])
        validName = False
        while validName == False:
            await start_message.edit(content=None,embed=name_embed, components=[])
            def check(m): return m.author.id == ctx.author.id and m.channel == ctx.channel
            try: userReply = await self.bot.wait_for('message', check=check, timeout=self.timeout) 
            except: return False #timeout
            else:
                roleName = userReply.content
                await userReply.delete()
                passedChecks = True
                if roleName == None:
                    error_menu = discord.Embed(description="<:cross:872834807476924506> Please enter a role name.", colour=self.bot.twitch_embed_colour)
                    await ctx.send(embed=error_menu, delete_after=3)
                    passedChecks = False
                if any(word in roleName.lower() for word in self.bot.bannedRoleWords):
                    error_menu = discord.Embed(description="<:cross:872834807476924506> You are not allowed inappropriate names.", colour=self.bot.twitch_embed_colour)
                    await ctx.send(embed=error_menu, delete_after=3)
                    passedChecks = False
                for role in ctx.guild.roles:
                    if roleName.lower() == role.name.lower():
                        error_menu = discord.Embed(description="<:cross:872834807476924506> You cannot use an existing role name.", colour=self.bot.twitch_embed_colour)
                        await ctx.send(embed=error_menu, delete_after=3)
                        passedChecks = False
                        break
                allowed = string.ascii_letters + string.digits + r'`!"£$%^&*()_+{}:@~<>?|-=[];#,./\ '
                # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`!"£$%^&*()_+{}:@~<>?|-=[];#,./\
                def check_characters(mystring):
                    return all(c in allowed for c in mystring)
                if not check_characters(roleName):
                    error_menu = discord.Embed(description="<:cross:872834807476924506> You can only use letters, numbers and some common symbols in your role name.", colour=self.bot.twitch_embed_colour)
                    await ctx.send(embed=error_menu, components=[], delete_after=3)
                    passedChecks = False
                if passedChecks:
                    return roleName

    async def role_colour(self, ctx, start_message):
        """ Choose a colour from dropdown. Returns False if timeout or returns the colour """
        colour_embed = self.bot.getTwitchEmbed.role_colour()
        colour_dropdown = self.bot.getTwitchComponent.role_colour()
        hex_embed = self.bot.getTwitchEmbed.hex()
        validColour = False
        while validColour == False:
            await start_message.edit(content=None,embed=colour_embed,components=[colour_dropdown])
            button_ctx = await self.wait_for_member(ctx.author.id, start_message, colour_dropdown)
            if button_ctx == False: return False #timeout
            selected = button_ctx.selected_options[0]
            if selected == "custom":
                await button_ctx.edit_origin(content=None, embed=hex_embed,components=[])
                def check(m): return m.author.id == ctx.author.id and m.channel == ctx.channel
                try: userReply = await self.bot.wait_for('message', check=check, timeout=self.timeout)
                except: return False #timeout
                await userReply.delete()
                HEX_COLOR_REGEX = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
                def is_hex_color(input_string):
                    if input_string=='': return False
                    regexp = re.compile(HEX_COLOR_REGEX)
                    if regexp.search(input_string):
                        return True
                    return False
                if is_hex_color(userReply.content):
                    try:
                        hexcolour = (userReply.content).lstrip('#')
                        colour = discord.Colour(int(f"0x{hexcolour}", 16))
                        return colour
                    except Exception as e: 
                        print(e)
                EmbedColor = discord.Colour.dark_theme()
                await ctx.send(embed=discord.Embed(description="<:cross:872834807476924506> Invalid hex code.", colour=EmbedColor), components=[], delete_after=3)
            else:
                await button_ctx.edit_origin(content=None, embed=colour_embed, components=[colour_dropdown])
                val = selected.lstrip('#')
                colour = discord.Colour(int(f"0x{val}", 16))
                return colour

def setup(bot):
    bot.add_cog(TrickTwitchCustomRolesCommandUtil(bot))