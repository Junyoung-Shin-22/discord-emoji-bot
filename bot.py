import asyncio
import discord
import re

import db

with open('./data/token.txt') as f:
    TOKEN = f.read().strip()

_intents = discord.Intents.all()
BOT = discord.Client(intents=_intents)

_GLOBAL_MATCH_CACHE = dict()

@BOT.event
async def on_ready():
    print(BOT.user.name, 'is ready')

_emoji_url_template = 'https://cdn.discordapp.com/emojis/{emoji_id}.{ext}'
_partial_emojis = { k: discord.PartialEmoji.from_str(v)
    for k, v in
    [('x', '❌'), ('mushroom', '🍄')]
}

# ==================== handling messages ==================== #
@BOT.event
async def on_message(message: discord.Message):
    cond = [ # conditions that the message must satisfy
        message.guild.id == 284430174089510912,
    ]
    if not all(cond):
        return
    
    content = message.content

    # check if the message is custom emoji only
    match = re.fullmatch(r'^<(a?):([0-9a-zA-Z_]+):(\d+)>$', content)
    if match is not None:
        await _handle_emoji_message(message, match)
        return
    # or a user command
    match = re.fullmatch(r'^~([0-9a-zA-Z_]+)$', content)
    if match is not None:
        await _handle_command_message(message, match)
        return

def _create_embed(**kwargs):
    author = kwargs['author']
    image_url = kwargs['image_url']

    emoji_name = kwargs['emoji_name']

    author_name = author.display_name
    author_avatar_url = author.display_avatar.url

    emb = discord.Embed()
    emb.set_author(name=author_name, icon_url=author_avatar_url)
    emb.set_image(url=image_url)
    emb.set_footer(text=emoji_name)

    return emb

async def _delete_message_and_send_embed(message, emb):
    ref = message.reference
        
    await message.delete()
    new_message = await message.channel.send(embed=emb, reference=ref, mention_author=False)

    await new_message.add_reaction(_partial_emojis['x'])

async def _handle_emoji_message(message, match):
    _GLOBAL_MATCH_CACHE[message.id] = match
    await message.add_reaction(_partial_emojis['mushroom'])

    await asyncio.sleep(3)

    try:
        await message.remove_reaction(_partial_emojis['mushroom'], BOT.user)
    except:
        pass
    _GLOBAL_MATCH_CACHE.pop(message.id, None)

async def _handle_command_message(message, match):
    emoji_name = match.group(1)
    image_url = db.fetch_image_url_by_name(emoji_name)

    if image_url is None:
        return
    
    author = message.author

    emb = _create_embed(author=author, image_url=image_url, emoji_name=emoji_name)
    await _delete_message_and_send_embed(message, emb)
# ==================== handling messages ==================== #
    
# ==================== handling reactions ==================== #
@BOT.event
async def on_raw_reaction_add(payload):
    emoji = payload.emoji
    channel_id = payload.channel_id
    message_id = payload.message_id

    # handle only registered reactions
    if emoji not in _partial_emojis.values():
        return
    
    # try to fetch the original message
    # if fails, do nothing
    try:
        message = await (await BOT.fetch_channel(channel_id)).fetch_message(message_id)
    except:
        return
    
    if emoji == _partial_emojis['x']:
        await _handle_x_reaction(payload, message)
    elif emoji == _partial_emojis['mushroom']:
        await _handle_mushroom_reaction(payload, message)
        
async def _handle_x_reaction(payload, message):
    # ignore messages that are not bot-sent embed
    if message.author.id != BOT.user.id: 
        return
    
    author_name = message.embeds[0].author.name
    if author_name == payload.member.display_name: # reaction from original author
        await message.delete()
    elif payload.member != BOT.user:
        await message.remove_reaction(payload.emoji, payload.member)

async def _handle_mushroom_reaction(payload, message):
    match = _GLOBAL_MATCH_CACHE.get(message.id)
    if match is None:
        return
    
    if payload.member == BOT.user:
        return
    elif payload.member != message.author:
        await message.remove_reaction(payload.emoji, payload.member)
        return
    

    is_animated = bool(match.group(1))
    emoji_name = match.group(2)
    emoji_id = match.group(3)

    ext = 'gif' if is_animated else 'webp'
    image_url = _emoji_url_template.format(emoji_id=emoji_id, ext=ext)
    db.add_emoji(db.EmojiModel(emoji_name, image_url))

    author = message.author

    emb = _create_embed(author=author, image_url=image_url, emoji_name=emoji_name)
    await _delete_message_and_send_embed(message, emb)
# ==================== handling reactions ==================== #