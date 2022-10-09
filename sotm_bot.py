import discord
import logging
import sotm_db
import discord_token

logging.basicConfig(level=logging.INFO)

"""If we have > this many cards we just list the names of the matching cards"""
CARD_SUMMARISE_LIMIT=3

"""If we have > this many cards we just say we've got a lot of matches"""
CARD_TOTAL_LIMT=20

class DiscordEmbedFormatter:
	def __init__(self, embed):
		self.embed = embed

	def title(self, title_text):
		self.embed.title = title_text

	def smallbox(self, box_title, box_text):
		self.embed.add_field(name=box_title, value=box_text, inline=True)

	def box(self, box_title, box_text):
		self.embed.add_field(name=box_title, value=box_text, inline=False)

	def footer(self, footer_text):
		self.embed.set_footer(text=footer_text)

def card_to_discord_embed(card):
	embed = discord.Embed()
	formatter = DiscordEmbedFormatter(embed)
	card.format(formatter)
	return embed

async def send_cards_as_discord_embeds(message, content, cards):
	for card in cards:
		await message.channel.send(content=content, embed=card_to_discord_embed(card), reference=message)
		content = None

		if (card.other_side):
			await message.channel.send(embed=card_to_discord_embed(card.other_side), reference=message)

def card_to_short_name(card):
	ret = f"{card.mod}|{card.deck}|{card.title}"

	if (card.other_side != None):
		ret += f" // {card.other_side.mod}|{card.other_side.deck}|{card.other_side.title}"

	return ret

async def handle_command(command, message):
	cards = sotm_db.search_cards(command)

	exact_matches = [ card for card in cards if card.is_exact_match(command) ]
	inexact_matches = [ card for card in cards if not card in exact_matches ]

	if len(cards) <= 0:
		await message.channel.send("There are no matches for {{" + str(command) + "}}", reference=message)
		return

	if len(cards) > 1:
		to_send = f"There are {len(cards)} possible matches for {{{{{command}}}}}"
	else:
		to_send = str(command) + ":"

	if len(exact_matches) > 0:
		await send_cards_as_discord_embeds(message, to_send, exact_matches)
		to_send = None

	if len(inexact_matches) > 0:
		if len(cards) > CARD_SUMMARISE_LIMIT:
			if to_send == None:
				to_send = f"{len(inexact_matches)} inexact matches"

			if len(cards) < CARD_TOTAL_LIMT:
				to_send += ":"
				for card in inexact_matches:
					to_send += "\n" + card_to_short_name(card)
			else:
				to_send += " which is too many to list."

			await message.channel.send(to_send, reference=message)
		else:
			await send_cards_as_discord_embeds(message, to_send, inexact_matches)

class MyClient(discord.Client):
	async def on_ready(self):
		print('Bot online: ', self.user)

	async def on_message(self, message):
		# don't respond to ourselves
		if message.author == self.user:
			return

		offset = 0
		while True:
			bot_command_start = message.content.find("{{", offset)
			if bot_command_start < 0: break
			bot_command_start += 2

			bot_command_newline = message.content.find("\n", bot_command_start)
			if bot_command_newline < 0: bot_command_newline = len(message.content)
			bot_command_end = message.content.find("}}", bot_command_start, bot_command_newline)
			if bot_command_end < 0: break

			await handle_command(message.content[bot_command_start:bot_command_end], message)
			offset = bot_command_end

client = MyClient()

client.run(discord_token.sotmBotToken)