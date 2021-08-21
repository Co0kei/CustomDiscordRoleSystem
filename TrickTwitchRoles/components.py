import discord
from discord.ext import commands
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option
from discord_slash.model import ButtonStyle

class TrickTwitchCustomRolesComponents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def home(self, disabled=False):
        """ The start components """
        return create_actionrow(*[
            create_button(style=ButtonStyle.green, label="Create", custom_id="create", emoji=self.bot.get_emoji(873224615881748523), disabled = True if disabled else False),
            create_button(style=ButtonStyle.blurple, label="Edit", custom_id="edit", emoji="\U0000270f", disabled = True if disabled else False),
            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel", emoji=self.bot.get_emoji(872834807476924506), disabled = True if disabled else False)
            ])
        #return create_actionrow(*buttons)

    def role_colour(self):
        """ Dropdown for selecting role colour """
        return create_actionrow(
                        create_select(
                            options=[
                                create_select_option("Custom", value="custom", emoji="\U0000270f"),
                                create_select_option("Random", value=str(discord.Color.random()), emoji=self.bot.get_emoji(878628667343921192)),
                                create_select_option("Red", value=str(discord.Color.red()), emoji=self.bot.get_emoji(878621258474995712)),
                                create_select_option("Dark Red", value=str(discord.Color.dark_red()), emoji=self.bot.get_emoji(878622829459947540)),
                                create_select_option("Orange", value=str(discord.Color.orange()), emoji=self.bot.get_emoji(878624460394090506)),
                                create_select_option("Dark Orange", value=str(discord.Color.dark_orange()), emoji=self.bot.get_emoji(878624476831580200)),
                                create_select_option("Yellow", value=str(discord.Color.gold()), emoji=self.bot.get_emoji(878624491322900531)),
                                create_select_option("Gold", value=str(discord.Color.dark_gold()), emoji=self.bot.get_emoji(878624510767693874)),
                                create_select_option("Green", value=str(discord.Color.green()), emoji=self.bot.get_emoji(878625342653354014)),
                                create_select_option("Dark Green", value=str(discord.Color.dark_green()), emoji=self.bot.get_emoji(878625351775944764)),
                                create_select_option("Blue", value=str(discord.Color.blue()), emoji=self.bot.get_emoji(878625380372717588)),
                                create_select_option("Dark Blue", value=str(discord.Color.dark_blue()), emoji=self.bot.get_emoji(878625390514565131)),
                                create_select_option("Magenta", value=str(discord.Color.magenta()), emoji=self.bot.get_emoji(878625421749551144)),
                                create_select_option("Dark Magenta", value=str(discord.Color.dark_magenta()), emoji=self.bot.get_emoji(878625431593553971)),
                                create_select_option("Purple", value=str(discord.Color.purple()), emoji=self.bot.get_emoji(878625456667131934)),
                                create_select_option("Dark Purple", value=str(discord.Color.dark_purple()), emoji=self.bot.get_emoji(878625465001185280)),
                                create_select_option("Blurple", value=str(discord.Color.blurple()), emoji=self.bot.get_emoji(878625479224078336)),
                                create_select_option("Teal", value=str(discord.Color.teal()), emoji=self.bot.get_emoji(878625501126750258)),
                                create_select_option("Dark Teal", value=str(discord.Color.dark_teal()), emoji=self.bot.get_emoji(878625512711409744)),
                                create_select_option("Light Gray", value=str(discord.Color.lighter_grey()), emoji=self.bot.get_emoji(878625530214232126)),
                                create_select_option("Gray", value=str(discord.Color.light_grey()), emoji=self.bot.get_emoji(878625540788076574)),
                                create_select_option("Dark Gray", value=str(discord.Color.dark_grey()), emoji=self.bot.get_emoji(878626592077778985)),
                                create_select_option("Darker Gray", value=str(discord.Color.darker_grey()), emoji=self.bot.get_emoji(878626606334218240)),
                            ],
                            placeholder="Select a colour!", 
                            min_values=1,
                            max_values=1,  
                        ))

    def confirm(self, disabled = False):
        """ Confirmation to create role buttons"""
        return create_actionrow(*[
                create_button(style=ButtonStyle.green, label="Create", custom_id="create", emoji=self.bot.get_emoji(873224615881748523), disabled = True if disabled else False),
                create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel", emoji=self.bot.get_emoji(872834807476924506),  disabled = True if disabled else False)
                ])

    def received(self):
        """ Button to return to home menu"""
        return create_actionrow(*[
                create_button(style=ButtonStyle.green, label="Main Menu", custom_id="main"),
                ])

    def edit(self):
        """ Buttons for editing menu """
        return create_actionrow(*[            
                create_button(style=ButtonStyle.blurple, label="Name", custom_id="name"),
                create_button(style=ButtonStyle.blurple, label="Colour", custom_id="colour"),
                create_button(style=ButtonStyle.blurple, label="Top Role", custom_id="pos"),
                create_button(style=ButtonStyle.red, label="Delete", custom_id="delete"),

                create_button(style=ButtonStyle.green, label="Main Menu", custom_id="main")
                ])

    def choose_edit(self, numOfRoles):
        """ Buttons to choose which role to edit """
        return create_actionrow(*[create_button(style=ButtonStyle.blurple if numOfRoles >= 1 else ButtonStyle.grey, label="Role 1",  custom_id="0"),
                    create_button(style=ButtonStyle.blurple if numOfRoles >= 2 else ButtonStyle.grey, label="Role 2", custom_id="1", disabled = True if numOfRoles < 2 else False),
                    create_button(style=ButtonStyle.blurple if numOfRoles >= 3 else ButtonStyle.grey, label="Role 3", custom_id="2", disabled = True if numOfRoles < 3 else False),
                    create_button(style=ButtonStyle.blurple if numOfRoles >= 4 else ButtonStyle.grey, label="Role 4", custom_id="3", disabled = True if numOfRoles < 4 else False),
                    create_button(style=ButtonStyle.green, label="Main Menu", custom_id="main")])

def setup(bot):
    bot.add_cog(TrickTwitchCustomRolesComponents(bot))



