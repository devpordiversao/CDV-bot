import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do bot
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Função para converter texto para a fonte especial
def to_small_caps(text):
    normal = "abcdefghijklmnopqrstuvwxyz"
    small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    
    result = ""
    for char in text.lower():
        if char in normal:
            index = normal.index(char)
            result += small_caps[index]
        else:
            result += char
    return result

# Função para converter texto para fonte monospace (𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎)
def to_monospace(text):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    monospace = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    
    result = ""
    for char in text:
        if char in normal:
            index = normal.index(char)
            result += monospace[index]
        else:
            result += char
    return result

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} slash commands sincronizados!')
        print('Bot pronto para criar canais!')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

@bot.tree.command(name="criar_canais", description="Cria todos os canais VIP e de divulgação em categorias privadas")
@app_commands.default_permissions(administrator=True)
async def criar_canais(interaction: discord.Interaction):
    """Cria todos os canais VIP e de divulgação em categorias organizadas"""
    
    await interaction.response.defer()
    guild = interaction.guild
    
    try:
        # Procura ou cria o cargo Divulgador VIP
        cargo_nome = to_small_caps("divulgador vip") + " 💎"
        cargo_divulgador = discord.utils.get(guild.roles, name=cargo_nome)
        
        if not cargo_divulgador:
            # Cria o cargo se não existir
            cargo_divulgador = await guild.create_role(
                name=cargo_nome,
                color=discord.Color.from_rgb(64, 224, 208),  # Cor azul turquesa
                hoist=True,  # Mostra separado na lista de membros
                mentionable=True
            )
            await interaction.followup.send(f"✅ Cargo **{cargo_nome}** criado!")
        
        # Permissões para canais privados
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            cargo_divulgador: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        # CATEGORIA 1: ÁREA VIP
        categoria_vip = await guild.create_category(to_small_caps("ÁREA VIP"), overwrites=overwrites)
        
        canais_vip = [
            ("📢", "avisos-vip"),
            ("🎁", "benefícios"),
            ("💬", "chat-vip"),
            ("🤝", "parcerias-vip"),
            ("🎉", "eventos-vip"),
            ("🏆", "desafios-vip"),
            ("🎲", "sorteios-vip"),
            ("🌟", "early-access")
        ]
        
        for emoji, nome in canais_vip:
            nome_formatado = to_small_caps(nome)
            await categoria_vip.create_text_channel(f"{emoji}・{nome_formatado}", overwrites=overwrites)
        
        # CATEGORIA 2: DIVULGAÇÕES
        categoria_divulgacao = await guild.create_category(to_small_caps("DIVULGAÇÕES"), overwrites=overwrites)
        
        canais_divulgacao = [
            ("📱", "divulgação-social"),
            ("🎮", "divulgação-servidores"),
            ("🎬", "divulgação-youtube"),
            ("📺", "divulgação-twitch"),
            ("🎨", "divulgação-arte"),
            ("💼", "divulgação-serviços")
        ]
        
        for emoji, nome in canais_divulgacao:
            nome_formatado = to_small_caps(nome)
            await categoria_divulgacao.create_text_channel(f"{emoji}・{nome_formatado}", overwrites=overwrites)
        
        await interaction.followup.send("✅ **Todos os canais foram criados com sucesso!**\n🔒 **Todos os canais estão privados**\n💎 **Cargo '{}'** tem acesso a todos os canais\n📁 Categoria **{}** - 8 canais criados\n📁 Categoria **{}** - 6 canais criados".format(cargo_nome, to_small_caps('ÁREA VIP'), to_small_caps('DIVULGAÇÕES')))
        
    except discord.Forbidden:
        await interaction.followup.send("❌ Erro: O bot não tem permissões suficientes!")
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao criar canais: {str(e)}")

@bot.tree.command(name="limpar_canais", description="Remove todos os canais criados pelo bot")
@app_commands.default_permissions(administrator=True)
async def limpar_canais(interaction: discord.Interaction):
    """Remove todos os canais criados pelo bot (use com cuidado!)"""
    
    await interaction.response.send_message("⚠️ **ATENÇÃO!** Isso vai remover TODOS os canais VIP e de divulgação!\n\nTem certeza? Use `/confirmar_limpar` para confirmar.", ephemeral=True)

@bot.tree.command(name="confirmar_limpar", description="Confirma a remoção de todos os canais")
@app_commands.default_permissions(administrator=True)
async def confirmar_limpar(interaction: discord.Interaction):
    """Confirma a remoção dos canais"""
    
    await interaction.response.defer()
    guild = interaction.guild
    
    try:
        categorias_para_remover = [to_small_caps("ÁREA VIP"), to_small_caps("DIVULGAÇÕES")]
        canais_removidos = 0
        
        for categoria in guild.categories:
            if categoria.name in categorias_para_remover:
                # Remove todos os canais da categoria
                for channel in categoria.channels:
                    await channel.delete()
                    canais_removidos += 1
                # Remove a categoria
                await categoria.delete()
        
        # Remove o cargo Divulgador VIP
        cargo_nome = to_small_caps("divulgador vip") + " 💎"
        cargo_divulgador = discord.utils.get(guild.roles, name=cargo_nome)
        if cargo_divulgador:
            await cargo_divulgador.delete()
            await interaction.followup.send(f"✅ Canais e cargo removidos com sucesso! ({canais_removidos} canais deletados)")
        else:
            await interaction.followup.send(f"✅ Canais removidos com sucesso! ({canais_removidos} canais deletados)")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao remover canais: {str(e)}")

@bot.tree.command(name="setvip", description="Dá o cargo Divulgador VIP para um usuário")
@app_commands.default_permissions(administrator=True)
async def setvip(interaction: discord.Interaction, usuario: discord.Member):
    """Adiciona o cargo Divulgador VIP a um usuário"""
    
    guild = interaction.guild
    
    try:
        # Procura ou cria o cargo Divulgador VIP
        cargo_nome = to_small_caps("divulgador vip") + " 💎"
        cargo_divulgador = discord.utils.get(guild.roles, name=cargo_nome)
        
        if not cargo_divulgador:
            # Cria o cargo se não existir
            cargo_divulgador = await guild.create_role(
                name=cargo_nome,
                color=discord.Color.from_rgb(64, 224, 208),  # Cor azul turquesa
                hoist=True,  # Mostra separado na lista de membros
                mentionable=True
            )
            
            # Adiciona permissões aos canais VIP
            categorias_alvo = [to_small_caps("ÁREA VIP"), to_small_caps("DIVULGAÇÕES")]
            for categoria in guild.categories:
                if categoria.name in categorias_alvo:
                    await categoria.set_permissions(cargo_divulgador, view_channel=True, send_messages=True)
                    for channel in categoria.channels:
                        await channel.set_permissions(cargo_divulgador, view_channel=True, send_messages=True)
        
        # Adiciona o cargo ao usuário
        await usuario.add_roles(cargo_divulgador)
        await interaction.response.send_message(f"✅ Cargo **{cargo_nome}** adicionado para {usuario.mention}!")
        
    except discord.Forbidden:
        await interaction.response.send_message("❌ Erro: O bot não tem permissões suficientes!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro: {str(e)}")

@bot.tree.command(name="setcargo", description="Dá um cargo específico para um usuário")
@app_commands.default_permissions(administrator=True)
async def setcargo(interaction: discord.Interaction, cargo: discord.Role, usuario: discord.Member):
    """Adiciona um cargo específico a um usuário"""
    
    try:
        # Verifica se o cargo do bot é maior que o cargo que está tentando dar
        if cargo.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message(f"❌ Não posso dar o cargo **{cargo.name}** pois ele é igual ou superior ao meu cargo!", ephemeral=True)
            return
        
        # Adiciona o cargo ao usuário
        await usuario.add_roles(cargo)
        await interaction.response.send_message(f"✅ Cargo **{cargo.name}** adicionado para {usuario.mention}!")
        
    except discord.Forbidden:
        await interaction.response.send_message("❌ Erro: O bot não tem permissões suficientes!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro: {str(e)}")

@bot.tree.command(name="ajuda", description="Mostra os comandos disponíveis do bot")
async def ajuda(interaction: discord.Interaction):
    """Mostra os comandos disponíveis"""
    
    embed = discord.Embed(
        title="🤖 Comandos do Bot",
        description="Lista de comandos slash disponíveis:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="/criar_canais",
        value="Cria todos os canais VIP e de divulgação (privados) + cargo",
        inline=False
    )
    
    embed.add_field(
        name="/criar_canais_normais",
        value="Cria canais públicos (Info, Comunidade, Suporte, Divulgação)",
        inline=False
    )
    
    embed.add_field(
        name="/renomear_cargos",
        value="Edita todos os cargos para a fonte 𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎",
        inline=False
    )
    
    embed.add_field(
        name="/setvip @usuario",
        value="Dá o cargo Divulgador VIP para um usuário",
        inline=False
    )
    
    embed.add_field(
        name="/setcargo @cargo @usuario",
        value="Dá um cargo específico para um usuário",
        inline=False
    )
    
    embed.add_field(
        name="/limpar_canais",
        value="Inicia o processo de remoção dos canais",
        inline=False
    )
    
    embed.add_field(
        name="/confirmar_limpar",
        value="Confirma a remoção de todos os canais criados",
        inline=False
    )
    
    embed.add_field(
        name="/ajuda",
        value="Mostra esta mensagem de ajuda",
        inline=False
    )
    
    embed.set_footer(text="⚠️ Comandos de criação/remoção/cargos requerem permissão de Administrador")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="renomear_cargos", description="Renomeia todos os cargos existentes para fonte Monospace")
@app_commands.default_permissions(administrator=True)
async def renomear_cargos(interaction: discord.Interaction):
    """Edita todos os cargos para a fonte monospace"""
    
    await interaction.response.defer()
    guild = interaction.guild
    
    try:
        cargos_editados = 0
        cargos_ignorados = []
        
        # Ignora cargos de bots, @everyone e cargo "Dono"
        for role in guild.roles:
            # Pula @everyone
            if role.name == "@everyone":
                continue
            
            # Pula cargos de bots
            if role.managed:
                cargos_ignorados.append(f"{role.name} (bot)")
                continue
            
            # Pula cargo "Dono" (em qualquer variação)
            if "dono" in role.name.lower() or "owner" in role.name.lower():
                cargos_ignorados.append(f"{role.name} (Dono)")
                continue
            
            # Pula se o cargo do bot é menor ou igual
            if role.position >= guild.me.top_role.position:
                cargos_ignorados.append(f"{role.name} (hierarquia)")
                continue
            
            # Renomeia o cargo
            nome_antigo = role.name
            nome_novo = to_monospace(role.name)
            
            # Só edita se o nome mudou
            if nome_antigo != nome_novo:
                await role.edit(name=nome_novo)
                cargos_editados += 1
        
        mensagem = f"✅ **{cargos_editados} cargos renomeados com sucesso!**"
        
        if cargos_ignorados:
            mensagem += f"\n\n⚠️ **Cargos ignorados ({len(cargos_ignorados)}):**\n"
            mensagem += "\n".join(f"- {cargo}" for cargo in cargos_ignorados[:10])
            if len(cargos_ignorados) > 10:
                mensagem += f"\n... e mais {len(cargos_ignorados) - 10}"
        
        await interaction.followup.send(mensagem)
        
    except discord.Forbidden:
        await interaction.followup.send("❌ Erro: O bot não tem permissões suficientes!")
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao renomear cargos: {str(e)}")

@bot.tree.command(name="criar_canais_normais", description="Cria canais públicos (Info, Comunidade, Suporte, Divulgação)")
@app_commands.default_permissions(administrator=True)
async def criar_canais_normais(interaction: discord.Interaction):
    """Cria todos os canais públicos do servidor e remove os antigos (exceto VIP)"""
    
    await interaction.response.defer()
    guild = interaction.guild
    
    try:
        # Categorias VIP que NÃO devem ser deletadas
        categorias_vip = [
            to_small_caps("ÁREA VIP"), 
            to_small_caps("DIVULGAÇÕES"),
            "💎 ᴀʀᴇᴀ ᴠɪᴘ 🜲"  # Nova categoria VIP criada manualmente
        ]
        
        # Remove TODOS os canais e categorias, EXCETO as VIP
        canais_deletados = 0
        canais_ignorados = []
        await interaction.followup.send("🗑️ Removendo canais antigos... (mantendo área VIP)")
        
        for categoria in guild.categories:
            # Se NÃO for categoria VIP, deleta
            if categoria.name not in categorias_vip:
                # Deleta todos os canais dentro da categoria
                for channel in categoria.channels:
                    try:
                        await channel.delete()
                        canais_deletados += 1
                    except discord.HTTPException as e:
                        # Canal obrigatório do servidor comunitário
                        if e.code == 50074:
                            canais_ignorados.append(channel.name)
                        else:
                            raise
                # Tenta deletar a categoria (pode falhar se tiver canais obrigatórios)
                try:
                    await categoria.delete()
                except discord.HTTPException:
                    pass  # Ignora se não conseguir deletar a categoria
        
        # Deleta canais que não estão em nenhuma categoria
        for channel in guild.channels:
            if channel.category is None and not isinstance(channel, discord.VoiceChannel):
                try:
                    await channel.delete()
                    canais_deletados += 1
                except discord.HTTPException as e:
                    if e.code == 50074:
                        canais_ignorados.append(channel.name)
                    else:
                        raise
        
        msg_deletados = f"✅ {canais_deletados} canais antigos removidos!"
        if canais_ignorados:
            msg_deletados += f"\n⚠️ {len(canais_ignorados)} canais obrigatórios mantidos: {', '.join(canais_ignorados)}"
        msg_deletados += "\n🔨 Criando novos..."
        await interaction.followup.send(msg_deletados)
        
        # CATEGORIA 1: INFORMAÇÕES
        categoria_info = await guild.create_category(to_small_caps("INFORMACOES"))
        
        canais_info = [
            ("📜", "regras"),
            ("📢", "anuncios"),
            ("🎉", "novidades"),
            ("ℹ️", "informacoes")
        ]
        
        for emoji, nome in canais_info:
            nome_formatado = to_small_caps(nome)
            await categoria_info.create_text_channel(f"{emoji}・{nome_formatado}")
        
        # CATEGORIA 2: COMUNIDADE
        categoria_comunidade = await guild.create_category(to_small_caps("COMUNIDADE"))
        
        canais_comunidade = [
            ("💬", "chat-geral"),
            ("🎮", "gaming"),
            ("🎵", "musica"),
            ("🖼️", "midias"),
            ("🤖", "comandos-bot")
        ]
        
        for emoji, nome in canais_comunidade:
            nome_formatado = to_small_caps(nome)
            await categoria_comunidade.create_text_channel(f"{emoji}・{nome_formatado}")
        
        # CATEGORIA 3: SUPORTE
        categoria_suporte = await guild.create_category(to_small_caps("SUPORTE"))
        
        canais_suporte = [
            ("🎫", "tickets"),
            ("❓", "ajuda"),
            ("💡", "sugestoes")
        ]
        
        for emoji, nome in canais_suporte:
            nome_formatado = to_small_caps(nome)
            await categoria_suporte.create_text_channel(f"{emoji}・{nome_formatado}")
        
        # CATEGORIA 4: CENTRAL DE PUBLICIDADE
        categoria_publicidade = await guild.create_category(to_small_caps("CENTRAL DE PUBLICIDADE"))
        
        canais_publicidade = [
            ("📱", "midias-sociais"),
            ("💬", "servidores-discord"),
            ("📹", "canais-youtube"),
            ("🎬", "lives-twitch"),
            ("🖼️", "artes-digitais"),
            ("🛠️", "servicos-ofertas")
        ]
        
        for emoji, nome in canais_publicidade:
            nome_formatado = to_small_caps(nome)
            await categoria_publicidade.create_text_channel(f"{emoji}・{nome_formatado}")
        
        await interaction.followup.send("✅ **Todos os canais públicos foram criados!**\n💎 **Área VIP preservada**\n📁 4 categorias públicas criadas com 18 canais!")
        
    except discord.Forbidden:
        await interaction.followup.send("❌ Erro: O bot não tem permissões suficientes!")
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao criar canais: {str(e)}")

# Executar o bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERRO: Token do Discord não encontrado no arquivo .env")
        print("Por favor, adicione DISCORD_TOKEN=seu_token_aqui no arquivo .env")
    else:
        bot.run(token)
      
