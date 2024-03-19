import sqlite3 as sql
from dataclasses import dataclass

@dataclass
class EmojiModel:
    name: str
    url: str

_CON = sql.connect('./data/db.db')
_CUR = _CON.cursor()

# -------------------- initialize db -------------------- #
_EMOJI_TABLE = _CUR.execute("""SELECT * FROM sqlite_schema WHERE name='emoji'""").fetchone()

if _EMOJI_TABLE is None:
    _CUR.execute(
        """CREATE TABLE emoji (name TEXT UNIQUE, url TEXT)"""
    )
    _CON.commit()
    print('DB initialized')
else:
    print('DB loaded')
# -------------------- initialize db -------------------- #


def add_emoji(emoji: EmojiModel):
    emoji_name = emoji.name
    emoji_url = emoji.url

    fetched_emoji = _CUR.execute("""SELECT * FROM emoji WHERE name=?""", (emoji_name,)).fetchone()
    if fetched_emoji is not None: # emoji exists in the table
        _CUR.execute("""UPDATE emoji SET url=? WHERE name=?""",
                     (emoji_url, emoji_name))
    
    else: # emoji not exist in the table
        _CUR.execute("""INSERT INTO emoji VALUES (?, ?)""", (emoji_name, emoji_url))
    _CON.commit()

def fetch_image_url_by_name(emoji_name: str) -> str:
    image_url = _CUR.execute("""SELECT url FROM emoji WHERE name=?""",(emoji_name,)).fetchone()
    
    if image_url is not None:
        image_url = image_url[0]

    return image_url

def debug():
    emoji_1 = EmojiModel('abc', 'http://url/abc.png')
    emoji_2 = EmojiModel('xyz', 'http://url/xyz.webp')
    emoji_3 = EmojiModel('abc', 'http://url/abc.gif')

    add_emoji(emoji_1)
    add_emoji(emoji_2)
    add_emoji(emoji_3)

    print(fetch_image_url_by_name('xyz'))
    print(fetch_image_url_by_name('abc'))
    print(fetch_image_url_by_name('asdf'))


if __name__ == '__main__':
    debug()