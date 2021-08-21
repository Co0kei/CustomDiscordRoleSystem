import discord
from discord.ext import commands
from dateutil.relativedelta import relativedelta

class TrickTwitchCustomRolesEmbeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def home(self, author, disabled=False):
        """ The start menu """
        content="use `/trick` to start a new session!" if disabled else "select a button to begin!"
        return discord.Embed(title=f"Hey **{author}**, {content}", description=f""
                                                                                f"<:tick:873224615881748523> Create a new role\n"
                                                                                f"\U0000270f Edit existing Twitch roles\n"
                                                                                f"<:cross:872834807476924506> Closes this menu", colour=self.bot.twitch_embed_colour)

    def role_name(self):
        """ Menu for setting role name"""
        return discord.Embed(title="**What would you like the name of your role to be?**", description=f"Please `write` in this channel.", colour=self.bot.twitch_embed_colour)

    def role_colour(self):
        """ Menu for choosing role colour from dropdown """
        return discord.Embed(title="**Choose a colour for your role from the dropdown!**", description=f"You can select `custom` to enter a hex code of your choice.", colour=self.bot.twitch_embed_colour)

    def hex(self):
        """ Menu for entering a hex code"""
        return discord.Embed(title="**Please enter a hex colour code.**", description=f"You can view hex codes [here](https://htmlcolorcodes.com/). "
                                 "Hex codes start with a `#` and have either 3 or 6 characters after the `#` such as `#438F87`.\n"
                                 "Please `write` in this channel.", colour=self.bot.twitch_embed_colour)

    def confirm(self, role_name, colour):
        """ Confirmation to create role """
        return discord.Embed(title="**Do you want to create your role?**",description=f"Name: `{role_name}`\nColour: `{colour}`\n\n"
                                          f"You can see the colour of your role at the edge of this embed.\nYou will be able to edit your role with the `/trick` command!", 
                                          colour=colour)

    def received(self, role_mention, unixTimeStamp, colour):
        """ Role received menu """
        return discord.Embed(title="**You have Received your Role**", description=f"You have your {role_mention} role!\n"
                    f"Your role expires <t:{unixTimeStamp}:R>\n"
                    f"If you wish to edit it you can use `/trick` again.", colour=colour)

    def edit(self, role_mention, unixTimeStamp, colour, extra=""):
        """ Edit role home menu"""
        if extra != "": extra = f"\n\n{extra}"
        return discord.Embed(title="Trick Twitch Custom Role", description=""
                                        f"**Role:** {role_mention} (expires <t:{int(unixTimeStamp)}:R>)\n\n"
                                       # f"Expires \n"
                                        f"You can edit your role name, colour, set it to your highest role or delete your role with the buttons below."
                                        f"{extra}", colour=colour)

    def choose_edit(self, author_id):
        """ Choose which of the four twitch roles you want to edit """
        guild = self.bot.Tricked_guild_instance
        roles = self.bot.TrickTwitch_CustomRoles_Dict[author_id] #unixTimeStamp = 
        msg = "You can have up to 4 roles at once.\n\n"
        msg += f"**Role 1:** {guild.get_role(int(roles[0])).mention} (expires <t:{int(int((guild.get_role(int(roles[0])).created_at + relativedelta(months=+2)).timestamp()))}:R>)\n"
        if len(roles) >= 2: msg += f"**Role 2:** {guild.get_role(int(roles[1])).mention} (expires <t:{int(int((guild.get_role(int(roles[1])).created_at + relativedelta(months=+2)).timestamp()))}:R>)\n"
        if len(roles) >= 3: msg += f"**Role 3:** {guild.get_role(int(roles[2])).mention} (expires <t:{int(int((guild.get_role(int(roles[2])).created_at + relativedelta(months=+2)).timestamp()))}:R>)\n"
        if len(roles) >= 4: msg += f"**Role 4:** {guild.get_role(int(roles[3])).mention} (expires <t:{int(int((guild.get_role(int(roles[3])).created_at + relativedelta(months=+2)).timestamp()))}:R>)\n"
        return discord.Embed(title="**Please choose which role you would like to edit.**", description=msg, colour=self.bot.twitch_embed_colour)

    def redeem(self):
        """ If user hasn't redeemed a twitch role """
        trick = self.bot.get_user(399431125765849089)
        support = self.bot.get_channel(870943261735419924)
        return discord.Embed(description=f"<:cross:872834807476924506> **You must redeem this from {trick.mention}'s Twitch Streams!**\n\n"
                                        f"For help open a general support ticket in {support.mention}", colour=self.bot.twitch_embed_colour)

    def ongoing(self, author_id):
        """ If user has ongoing session """
        jumpLink = self.bot.Ongoing_TrickTwitch_CustomRoles[author_id]
        return discord.Embed(description=f"<:cross:872834807476924506> You already have an active session [here]({jumpLink}).", colour=self.bot.twitch_embed_colour)

    def max(self):
        """ If user has 4 custom twitch roles already """
        return discord.Embed(description=f"<:cross:872834807476924506> You already have the maximum number of custom Twitch roles redeemed (4)!", colour=self.bot.twitch_embed_colour)

    def no_roles(self):
        """ if user has no custom twitch roles yet """
        return discord.Embed(description=f"<:cross:872834807476924506> You need to create a custom Twitch role first!", colour=self.bot.twitch_embed_colour)

def setup(bot):
    bot.add_cog(TrickTwitchCustomRolesEmbeds(bot))



