import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
import re
from pathlib import Path

# botのトークン
BOT_TOKEN = "your_discord_bot_token"

################# Discord #####################

# 共有用のサーバ
SERVER_ID_TEST = "your_discord_server_id"
# にきのもののサーバID
SERVER_ID_NIKI = "your_discord_server_id"

# osu!ディレクトリ - osuのチャネルID
CHANNER_ID_OSU_NETSU = "your_discord_channel_id"
# osu!ディレクトリ - ビートマップ共有チャネルID
CHANNER_ID_OSU_MAP = "your_discord_channel_id"

################## osu! ######################

OSU_CLIENT_ID = "your_client_id"
OSU_CLIENT_SECRET = 'your_client_secret'
OSU_API_BASE = 'https://osu.ppy.sh/api/v2'
OSU_OAUTH_TOKEN_URL = 'https://osu.ppy.sh/oauth/token'
BASE_DIR = Path(__file__).resolve().parent

# 正規表現でosu譜面URLからビートマップセットIDを抽出
def extract_beatmapset_id(text: str) -> int | None:
    match = re.search(r'https?://osu\.ppy\.sh/beatmapsets/(\d+)', text)
    if match is None:
        return None
    return int(match.group(1))

class OsuApiClient:
    def __init__(self) -> None:
        self._access_token: str | None = None
        self._token_task: asyncio.Task[str] | None = None

    async def _request_access_token(self) -> str:
        if not OSU_CLIENT_ID or not OSU_CLIENT_SECRET:
            raise RuntimeError('OSU_CLIENT_ID または OSU_CLIENT_SECRET が未設定です。')

        data = {
            'client_id': OSU_CLIENT_ID,
            'client_secret': OSU_CLIENT_SECRET,
            'grant_type': 'client_credentials',
            'scope': 'public',
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(OSU_OAUTH_TOKEN_URL, data=data) as response:
                response.raise_for_status()
                payload = await response.json()
                token = payload.get('access_token')
                if not token:
                    raise RuntimeError('osu API の access_token を取得できませんでした。')
                return token

    async def get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        if self._token_task is None:
            self._token_task = asyncio.create_task(self._request_access_token())

        self._access_token = await self._token_task
        self._token_task = None
        return self._access_token

    async def fetch_beatmapset_difficulties(self, beatmapset_id: int) -> list[float]:
        access_token = await self.get_access_token()
        url = f'{OSU_API_BASE}/beatmapsets/{beatmapset_id}'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.json()

        maps = []
        for beatmap in payload.get('beatmaps', []):
            if beatmap.get('mode') != 'osu':
                continue
            tmp = {
                'status': beatmap.get('status'),
                'difficulty_rating': round(float(beatmap.get('difficulty_rating')), 2),
                'total_length': beatmap.get('total_length'),
                'ar': beatmap.get('ar'),
                'bpm': beatmap.get('bpm')
            }

            maps.append(tmp)

        # 星の高い順にソートして全件返す
        return sorted(maps, key=lambda x: x['difficulty_rating'], reverse=True)

def calc(time: int) -> str:
    minutes = int(time / 60)
    seconds = time % 60
    return str(minutes) + ':' + f'{seconds:02}'

osu_api_client = OsuApiClient()

# Botの起動
bot = commands.Bot(command_prefix=['/', '!', '！'], case_insensitive=True, intents=discord.Intents.all())
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# コマンド コマンドリスト
@bot.command(name='こまんど', aliases=['cmd, コマンド'])
async def cmd(ctx: commands.Context) -> None:
    await ctx.send('コマンド接頭辞 "/" or "!" or "！"\n'
    'コマンド名: 別名\n' \
    'こまんど: cmd, コマンド: このリストを表示\n'
    'たえるたえない: taerutaenai\n'
    'そんなのありかよ: rassya, sonnanoarikayo\n'
    'なし: nassya, nasi, nashi\n'
    'ちびらっしゃー: tibi, tibirassya\n'
    '自動で開く: gomi\n'
    '雨になって: rain, 雨, ame, あめになって\n'
    'ウルト: ult, うると')


# コマンド $たえるたえない (日本語) と $taerutaenai (英字)
@bot.command(name='たえるたえない', aliases=['taerutaenai'])
async def taerutaenai(ctx: commands.Context) -> None:
    await ctx.send('ｴｸﾞｲｴｸﾞｲｴｸﾞｲｴｸﾞｲ')

# コマンド $sonnanoarikayo
@bot.command(name='そんなのありかよ', aliases=['sonnanoarikayo', 'rassya'])
async def sonnanoarikayo(ctx: commands.Context) -> None:
    file = discord.File(BASE_DIR / 'rassya_icon.png')
    await ctx.send('ありなんだよ', file=file)

# コマンド $sonnanoarikayo
@bot.command(name='なし', aliases=['nasi', 'nashi', 'nassya'])
async def sonnanoarikayo(ctx: commands.Context) -> None:
    file = discord.File(BASE_DIR / 'rassya_icon_nasi.png')
    await ctx.send('なしなんだよ....', file=file)

# コマンド $sonnanoarikayo
@bot.command(name='ちびらっしゃー', aliases=['tibi', 'tibirassya'])
async def tibirassya(ctx: commands.Context) -> None:
    file = discord.File(BASE_DIR / 'small_rassya.png')
    await ctx.send('可愛いｲﾝ', file=file)

# コマンド 
@bot.command(name='雨になって', aliases=['ame', 'あめになって', '雨', 'rain'])
async def gomi(ctx: commands.Context) -> None:
    file = discord.File(BASE_DIR / 'odoriko.gif')
    await ctx.send('何分か後に行くｲﾝ', file=file)

# コマンド !ウルト
@bot.command(name='ウルト', aliases=['ult', 'うると'])
async def uruto(ctx: commands.Context) -> None:
    file = discord.File(BASE_DIR / 'mamoru_ult.mp4')
    await ctx.send(file=file)


@bot.event
async def on_message(message):
    # GODか
    if random.randint(1, 8192) == 1:
        message.channel.send('8192分の1を引き当てました。あなたはGODｲﾝ!')


    # osu!ディレクトリ - ビートマップ共有チャネル用のon_messageイベント
    if message.channel.id == CHANNER_ID_OSU_MAP:
        await on_message_osu_share(message)
    await bot.process_commands(message)

# osu!ディレクトリ - ビートマップ共有チャネル用のon_messageイベント 
async def on_message_osu_share(message):
    if message.author.bot:  # Botのメッセージは無視
        return

    beatmapset_id = extract_beatmapset_id(message.content)
    if beatmapset_id is None:
        return

    try:
        maps = await osu_api_client.fetch_beatmapset_difficulties(beatmapset_id)
    except Exception:
        await message.channel.send('osuの譜面情報を取得できませんでした。')
        return


    # info = ' / '.join(f'{map:.2f}★' for map in maps)
    response = f"# mode osu! Ranked 時間 {calc(maps[0]['total_length'])}\n"
    for map in maps:
        response += f" - {map['difficulty_rating']}★ / BPM {map['bpm']} / AR {map['ar']}\n"
        
    await message.channel.send(response)


if __name__ == '__main__':
    bot.run(BOT_TOKEN)
