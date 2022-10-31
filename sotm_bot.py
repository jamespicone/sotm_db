import discord
import logging
import sotm_db
import discord_token

logging.basicConfig(level=logging.INFO)

"""If we have > this many cards we just list the names of the matching cards"""
CARD_SUMMARISE_LIMIT=3

"""If we have > this many cards we just say we've got a lot of matches"""
CARD_TOTAL_LIMT=20

BOT_VERSION = "0.1"

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

async def handle_card_command(commandword, command, message):
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

async def handle_adv_card_command(commandword, command, message):
	pass

async def handle_deck_command(commandword, command, message):
	pass

async def handle_mod_command(commandword, command, message):
	pass

async def handle_help_command(commandword, command, message):
	helpmessage = """
	Welcome to SOTMBot!
	You can ask the bot to do things simply by sending a message with the command sequence.
	Some commands you can send:
	- `help:{{}}` gets this help message
	- `about:{{}}` gets the current version of the SOTMBot
	- `card:{{search phrase}}` (or just `{{search phrase}}`) finds all the cards with a name matching `search phrase`
	"""

	if commandword is None:
		helpmessage += "(You are seeing this because you spoke to SOTMBot directly but didn't include a command)"
	else:
		if commandword.lower() != "help":
			helpmessage += f"(You are seeing this because you asked for a `{commandword}` command, which doesn't exist)"

	await message.channel.send(reference=message, content=helpmessage)

async def handle_about_command(commandword, command, message):
	await message.channel.send(reference=message, content=f"SOTMBot version {BOT_VERSION}")

command_funcs = {
	"card": handle_card_command,
	"cardadv": handle_adv_card_command,
	"deck": handle_deck_command,
	"mod": handle_mod_command,
	"help": handle_help_command,
	"about": handle_about_command,
	"version": handle_about_command
}

class MyClient(discord.Client):
	async def on_ready(self):
		print('Bot online: ', self.user)

	async def on_message(self, message):
		# don't respond to ourselves
		if message.author == self.user:
			return

		command_found = False

		offset = 0
		while True:
			bot_command_start = message.content.find("{{", offset)
			if bot_command_start < 0: break
			bot_command_start += 2

			bot_command_newline = message.content.find("\n", bot_command_start)
			if bot_command_newline < 0: bot_command_newline = len(message.content)
			bot_command_end = message.content.find("}}", bot_command_start, bot_command_newline)
			if bot_command_end < 0: break

			command_found = True

			commandword = "card"
			possible_commandword = message.content[offset:bot_command_start-2].rsplit(maxsplit=1)
			if len(possible_commandword) > 0 and possible_commandword[-1][-1] == ":":
				commandword = possible_commandword[-1][:-1]

			commandfunc = command_funcs.get(commandword, handle_help_command)
			await commandfunc(commandword, message.content[bot_command_start:bot_command_end], message)
			offset = bot_command_end

		if not command_found and client.user.mentioned_in(message):
			await handle_help_command(None, None, message)

	async def on_thread_create(self, thread):
		await thread.join()

client = MyClient()

client.run(discord_token.sotmBotToken)