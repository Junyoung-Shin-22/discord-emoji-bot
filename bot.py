import discord
import re

import db

with open('./token.txt') as f:
    TOKEN = f.read().strip()

_intents = discord.Intents.all()
BOT = discord.Client(intents=_intents)

@BOT.event
async def on_ready():
    print(BOT.user.name, 'is ready')

_emoji_url_template = 'https://cdn.discordapp.com/emojis/{emoji_id}.{ext}'

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

async def _handle_emoji_message(message, match):
    is_animated = bool(match.group(1))
    emoji_name = match.group(2)
    emoji_id = match.group(3)

    ext = 'gif' if is_animated else 'webp'
    image_url = _emoji_url_template.format(emoji_id=emoji_id, ext=ext)
    db.add_emoji(db.EmojiModel(emoji_name, image_url))

    author = message.author

    emb = _create_embed(author=author, image_url=image_url, emoji_name=emoji_name)
    ref = message.reference
        
    await message.delete()
    await message.channel.send(embed=emb, reference=ref, mention_author=False)

async def _handle_command_message(message, match):
    emoji_name = match.group(1)
    image_url = db.fetch_image_url_by_name(emoji_name)

    if image_url is None:
        return
    
    author = message.author

    emb = _create_embed(author=author, image_url=image_url, emoji_name=emoji_name)
    ref = message.reference
        
    await message.delete()
    await message.channel.send(embed=emb, reference=ref, mention_author=False)
