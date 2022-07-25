import discord
import logging
import sotm_db
import discord_token

logging.basicConfig(level=logging.INFO)

class DiscordEmbedFormatter:
	def __init__(self, embed):
		self.embed = embed

	def title(self, title_text):
		self.embed.title = title_text

	def smallbox(self, box_title, box_text):
		self.embed.add_field(name=box_title, value=box_text, inline=True)

	def box(self, box_title, box_text):
		self.embed.add_field(name=box_title, value=box_text, inline=False)

async def handle_command(command, channel):
	cards = sotm_db.search_cards(command)
	for card in cards:
		embed = discord.Embed()
		formatter = DiscordEmbedFormatter(embed)
		card.format(formatter)

		await channel.send(embed=embed)

class MyClient(discord.Client):
	async def on_ready(self):
		print('Bot online: ', self.user)

	async def on_message(self, message):
		# don't respond to ourselves
		if message.author == self.user:
			return

		offset = 0
		while True:
			bot_command_start = message.content.find("[[", offset)
			if bot_command_start < 0: break
			bot_command_start += 2

			bot_command_newline = message.content.find("\n", bot_command_start)
			if bot_command_newline < 0: bot_command_newline = len(message.content)
			bot_command_end = message.content.find("]]", bot_command_start, bot_command_newline)
			if bot_command_end < 0: break

			await handle_command(message.content[bot_command_start:bot_command_end], message.channel)
			offset = bot_command_end

client = MyClient()

client.run(discord_token.sotmBotToken)