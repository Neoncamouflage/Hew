import discord
from discord.ext import commands
import requests
import requests.auth
import random
import math
import json
import sqlite3
from sqlite3 import Error
import aiosqlite
import re
import asyncio


cards = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
questList = {1:{'questID':1,'name':'Kill Kobolds','desc':"Kobolds are a blight on this land. Get rid of a few of them for me will ya?",'reward':'[0]','xp':50,'coins':100,'goal':2,'progress':0,'type':'kill','target':'Kobold','repeatable':1,'completed':0}
,2:{'questID':2,'name':'Kill Goblins','desc':"Goblins... I swear. Worse than Kobolds! Do everyone a favor and take some out.",'reward':'[0]','xp':75,'coins':150,'goal':2,'progress':0,'type':'kill','target':'Goblin','repeatable':1,'completed':0}
,3:{'questID':3,'name':'Kill Thieves','desc':"As if we needed more to deal with, some hooligans are out there robbing folks. Teach them how bad an idea that is.",'reward':'[0]','xp':100,'coins':200,'goal':3,'progress':0,'type':'kill','target':'Thief','repeatable':1,'completed':0}
,4:{'questID':4,'name':'Kill Bugbears','desc':"Some really ugly beasts are ambushing merchants on the road. Take out a couple and maybe the rest will leave.",'reward':'[0]','xp':150,'coins':250,'goal':2,'progress':0,'type':'kill','target':'Bugbear','repeatable':1,'completed':0}}

places = ['Town','Sewer','Docks','Forest','Farmland',"Haunted House","Kobold Lair","Dump","Brewery","Blacksmith","Wizard Tower","Cliffs","Shipwreck","Orchard",
          'Town Hall','Castle','Graveyard']
races = ["human","elf","orc","halfling","gnome","dwarf",'dragonborn']
classes = {'paladin':'con','rogue':'dex','monk':'con','wizard':'int','sorcerer':'cha','cleric':'wis','warlock':'int','druid':'wis','ranger':'dex','fighter':'str','barbarian':'str','bard':'cha'}

levels = {1:0, 2: 300, 3: 610, 4: 1060, 5: 1712, 6: 2657, 7: 4028, 8: 6016, 9: 8898, 10: 13077, 11: 19137, 12: 27924, 13: 40665, 14: 59139, 15: 85927, 16: 124769, 17: 181090, 18: 262756, 19: 381171, 20: 552873}
easyQuestions = {"How many standard classes are there?":"12","Which ability score is used for a Bard's spellcasting?":"charisma","When you increase your ability scores as you level up, how high can your score go?":'20',
                 "What ability score increase does an Elf character get?":'dexterity',"When rolling for ability scores, you use a die with how many sides?":'6',"What type of damage prevents a troll from regenerating?":'fire',
                 "What is the actual racial name for a 'Dark Elf'?":'drow',"What ability allows a Barbarian to inflict additional damage?":'rage',"What 9th level spell allows you to do effectively anything?":'wish',
                 "Strength, Dexterity, Intelligence, Wisdom, Charisma. What's missing?":'constitution',"What is the name of the five-headed dragon (who is also a demon) that is a frequent D&D archvillain?":'tiamat',
                 "What is the highest value piece of standard currency, above gold pieces?":'platinum',"Which of the following does not have darkvison (Answer with the letter)?\nA. Gnolls\nB. Harpy\nC. Goblin":'b',"Magic missiles create how many projectiles at 1st level?":'3'}
mediumQuestions = {'What is the language of the Fey?':'sylvan','How many experience points are required for your first level up?':'300',"Which is the Arcane Tradition that focuses on modifying matter?":'transmutation',
                   "At level 2, a rogue can do what type of action as a bonus action?":'disengage',"What monster has a large central eye, multiple spellcasting eyestalks and floats above the ground?":"beholder",
                   "What kind of hit die does a sorcerer use? Type just the number of the die.":"6","There are two main types of dragons: Metallic and...":'chromatic'}
hardQuestions = {"Who is the god orcs worship?":'gruumsh',"What was the first official campaign setting created for Dungeons and Dragons?":'greyhawk',"How many Lay on Hands points does a paladin have at first level?":'5',
                 "What is the name of the massive dungeon complex that exists beneath the city of Waterdeep?":'undermountain',"What realm does Strahd von Zarovich rule over?":'ravenloft',"What is another name for a mind-flayer?":'illithid',
                 "Which of these is not an oath available to Paladins (Answer with the letter)?\nA. Devotion\nB. Crown\nC. Valor\nD. Redemption":'c ',
                 "What percent is the chance of a blink dog appearing BEHIND you?":"75","How much damage does a frost weapon add?":"1d6"}
scrambles = {'boelawr':'owlbear','oodkbl':'kobold','irdzwa':'wizard','honbbolig':'hobgoblin','aubgebr':'bugbear','eigdeagsn':'disengage','intnstcituoo':'constitution','ihcotca':'chaotic',
             'rdannbgoor':'dragonborn','uoger':'rogue','eorrsrce':'sorcerer','taamti':'tiamat','acamrhis':'charisma','gdnaro':'dragon','fuwlal':'lawful','fnerilan':'infernal',
             'iltihmr':'mithril'}

#Class and commands
class Adventure(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    def is_me():
        def predicate(ctx):
            return ctx.message.author.id == 262426987979735040

        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = f"You can do that again in {round(error.retry_after)} seconds"
            await ctx.send(msg)
        else:
            raise error

    #Admin commands
    @commands.command()
    @is_me()
    async def sql(self,ctx,*,args):
        if 'SELECT' in args:
            try:
                async with aiosqlite.connect("hewDB.db") as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(args) as cursor:
                        r = await cursor.fetchall()
                        await ctx.send(r[0].keys())
                        for each in r:
                            myData = []
                            for every in each:
                                myData.append(every)
                            await ctx.send(myData)

            except Exception as e:
                await ctx.send("**Error:**\n"+str(e))
        else:
            try:
                async with aiosqlite.connect("hewDB.db") as db:
                    await db.execute(args)
                    await db.commit()
                await ctx.send('Submitted')

            except Exception as e:
                await ctx.send("**Error:**\n"+str(e))

    @commands.command()
    @is_me()
    async def setMoney(self,ctx,arg):
        await db_query(f""" UPDATE adventureData
        SET money = {arg}
        WHERE id = {ctx.author.id}""")

    @commands.command()
    async def idea(self,ctx, *, arg):
        f = open('gameIdea.txt', 'a+')
        f.write(arg + '\n')
        f.close()
        await ctx.send(f'I\'ll keep that in mind {ctx.author.name}')

    @commands.command()
    async def handbook(self,ctx):
        content = "Welcome to Hewbris (Alpha build v1.0). This is an early version of a large, co-operative adventure game played within a Discord server.\n***Warning. This is a very early alpha version. Game data may be lost and changes to game mechanics will occur without notice.***\n\n\n"
        content += "To start you'll need to `!register` with a race. At the moment none of the races offer any benefit or altered stats. You'll also need to `!setclass` to pick your class - typing the command without specifying a class will list of all options and their corresponding stat boost. "
        content += "Currently stats affect only limited mechanics, but this will be expanded as time passes. Strength boosts melee damage, Dexterity boosts ranged damage and the chance you'll go first in combat, Constitution increases the HP you earn each level, Charisma boosts your success in certain interactions, Intelligence boosts magic damage, and Wisdom currently has no effect.\n\n"
        content += "Once you're all registered you have a few options. You can `!search` to explore the local area for items and money, `!hunt` and `!fish` for things to sell, or go to the `!townboard` to get some quests. Most quests require that you kill monsters, and these will be found randomly as you play the game. Once you reach higher levels, you can start to explore the Dungeons and Tombs with keys."
        content += "Dungeons award XP and loot for every kill, and you face a boss at the end for higher rewards. Tombs allow you to bring friends, but rewards and XP are only given to those that finish the Tomb.\nYou can view your character data with the `!sheet` command, and a clickable arrow reaction at the bottom will level you up if you have the required XP.\n\n"

        content += "If you have a game idea, feel free to add it using the `!idea <suggestion here>` command. Whatever you type after `!idea` will be entered into a list of suggestions for future development. Upcoming features include:\nMagic system and spells\nPets\nGuilds\nPvP\nStorylines\nAnd more!"
        await ctx.author.send(content)

    @commands.command()
    @is_me()
    async def ideas(self,ctx):
        f = open('gameIdea.txt', 'r')
        contents = f.read()
        f.close()
        if len(contents) > 2000:
            x=[contents[i:i + 2000] for i in range(0, len(contents), 2000)]
            for each in x:
                await ctx.send(each)
        else:
            await ctx.send(contents)

    @commands.command(aliases = ['quest'])
    async def quests(self,ctx):
        x = await db_query(f'''SELECT * FROM quests WHERE playerID = {ctx.author.id}''')
        if x == None:
            await ctx.send(f"You don't have any quests! You should check out the `!townboard` to get one.")
            return
        resp = ''
        for each in x:
            resp+= f'**{each["name"]}** - {each["progress"]}/{each["goal"]}\n*{each["desc"]}*\n'
        if resp == '':
            await ctx.send(f"You don't have any quests! You should check out the `!townboard` to get one.")
            return
        await ctx.send(f"Quests:\n{resp}")

    @commands.command()
    async def townboard(self,ctx):
        board = {}
        count = 1
        embed = discord.Embed(color=ctx.author.color,timestamp=ctx.message.created_at,description="*You visit the local town board to see what tasks are available.*\n\nType the number of the listing you would like to accept. ***Type 'N' to leave***\n")
        embed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
        for each in range(1,random.randint(3,4)):
            thisQuest = random.choice(list(questList))
            thisQuest = questList[thisQuest]
            board[count] = {'name':thisQuest['name'],'desc':thisQuest['desc'],'id':thisQuest['questID']}
            embed.add_field(name=f"{count} - {thisQuest['name']}",value=thisQuest['desc'],inline=False)
            count+=1
        await ctx.send(embed=embed)
        def answer(m):
            return m.author == ctx.author and ((m.content.isdigit() and m.content in [1,2,3,'1','2','3']) or m.content.lower() in 'n')
        try:
            ans = await self.bot.wait_for('message', check=answer, timeout=45.0)
        except asyncio.TimeoutError:
            await ctx.send("Not seeing anything that strikes your interest, you leave the town board")
        if ans.content.lower() != 'n':
            await startQuest(ctx,board[int(ans.content)]['id'])
        else:
            await ctx.send("You leave the town board.")

    #Profile and Settings Commands
    @commands.command()
    async def register(self,ctx,arg=None):
        if arg == None:
            await ctx.send(f"To register, you'll need to let me know what race you'd like to be. Type !register followed by your race. Valid races are {', '.join(races)}.")
            return
        if arg.lower() in races:
            x = await db_query(f'''INSERT INTO adventureData (id,name,race,money,xp) VALUES({ctx.author.id},'{ctx.author.name}','{arg.capitalize()}',0,0)''')
            y = await db_query(f'''CREATE TABLE IF NOT EXISTS inv{ctx.author.id} (id integer PRIMARY KEY,name text NOT NULL,desc text,stats text,quantity integer)''')
            z = await db_query(f'''INSERT INTO inv{ctx.author.id} (id,name,desc,stats,quantity) VALUES(8,'Wooden Sword','You have a sword...but not much of one','1d4',1)''')
            if y == True and x == True and z == True:
                await ctx.send(f"Character registered! Your next step will be to select a class with !setclass.")
            else:
                await ctx.send("Character failed to register! Make sure you don't already have a character.")
        else:
            await ctx.send(f"You need to register with a valid race. Type '!register race'. Valid races are {', '.join(races)}.")

    @commands.command()
    async def unregister(self,ctx):
        myID = ctx.author.id
        try:
            await db_query(f"""DELETE FROM adventureData
            WHERE id={myID}""")
            await db_query(f"""DELETE FROM quests WHERE playerID = {myID}""")
            await db_query(f""" DROP TABLE inv{myID}""")
            await ctx.send("Character deleted")
        except Exception as e:
            print(str(e))

    @commands.command(aliases = ['level'])
    async def levels(self,ctx):
        content = ''
        for each in levels:
            content+= f'**Level:** {each}  **XP:** {levels[each]}\n'
        await ctx.send(content)

    @commands.command(aliases = ['sheet'])
    async def profile(self,ctx,user: discord.Member = None):
        idNames = {None:'None'}
        idArmor = {}
        itemData = await db_query(f"""SELECT item_id,name,armor FROM items""")
        for each in itemData:
            idNames[each['item_id']] = each['name']
            idArmor[each['item_id']] = each['armor']
        if user == None:
            try:
                myData = await db_query(f"""SELECT * FROM adventureData WHERE id = {ctx.author.id}""")
                data = myData[0]
                upgrade = False
                if data['xp'] >= levels[data['level']+1]:
                    levelUp = f"***{data['level']}***\n*Level Up Available*"
                    upgrade = True
                else:
                    levelUp = f"{data['level']}"
                embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at,
                                      description="")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url='https://i0.wp.com/www.sageadvice.eu/wp-content/uploads/2017/09/221548.jpg')
                embed.add_field(name="Level", value=levelUp, inline=True)
                embed.add_field(name="Race", value=f"{data['race']}", inline=True)
                embed.add_field(name="Class", value=f"{data['class']}", inline=True)
                embed.add_field(name="Strength", value=f"{data['str']}", inline=True)
                embed.add_field(name="XP", value=f"{data['xp']}", inline=True)
                embed.add_field(name="HP", value=f"{data['hp']}", inline=True)
                embed.add_field(name="Dexterity", value=f"{data['dex']}", inline=True)
                embed.add_field(name="Head", value=f"{idNames[data['head']]}", inline=True)
                embed.add_field(name="Torso", value=f"{idNames[data['torso']]}", inline=True)
                embed.add_field(name="Constitution", value=f"{data['con']}", inline=True)
                embed.add_field(name="Hands", value=f"{idNames[data['hands']]}",
                                inline=True)
                embed.add_field(name="Feet", value=f"{idNames[data['feet']]}", inline=True)
                embed.add_field(name="Intelligence", value=f"{data['int']}", inline=True)
                embed.add_field(name="Right Hand", value=f"{idNames[data['right_hand']]}", inline=True)
                embed.add_field(name="Left Hand", value=f"{idNames[data['left_hand']]}", inline=True)
                embed.add_field(name="Wisdom", value=f"{data['wis']}", inline=True)
                embed.add_field(name="Legs", value=f"{idNames[data['legs']]}", inline=True)
                embed.add_field(name='\u200b',value='\u200b',inline=True)
                embed.add_field(name="Charisma", value=f"{data['cha']}", inline=False)
                sheetMessage = await ctx.send(embed=embed)
                if upgrade:
                    await sheetMessage.add_reaction('⬆️')

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) =='⬆️'

                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                        if str(reaction.emoji) == '⬆️':
                            await sheetMessage.clear_reaction(reaction)
                            if (data['level'] + 1) % 2 == 0:
                                await ctx.send("You can now add an ability point. Type str, wis, dex, int, con, or cha to apply your point.")

                                def check(m):
                                    return m.author == ctx.author

                                try:
                                    answer = await self.bot.wait_for('message', check=check, timeout=25.0)
                                except asyncio.TimeoutError:
                                    await ctx.send("I guess you need some more time to decide.")
                                    return
                                if answer.content.lower() not in ['int','dex','cha','wis','str','con']:
                                    await ctx.send("That's not valid. Maybe try again when you know what you want.")
                                    return
                                else:
                                    x = await db_query(f"""UPDATE adventureData SET {answer.content.lower()} = {answer.content.lower()} + 1 WHERE id = {ctx.author.id}""")
                            await ctx.send(f"***{ctx.author.name} Leveled Up!***")
                            await db_query(
                                f"""UPDATE adventureData SET level = level + 1, hp = hp + {round(data['con']*1.5)} WHERE id = {ctx.author.id}""")
                            myData = await db_query(f"""SELECT * FROM adventureData WHERE id = {ctx.author.id}""")
                            data = myData[0]
                            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at,
                                                  description="")
                            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                            embed.set_thumbnail(
                                url='https://i0.wp.com/www.sageadvice.eu/wp-content/uploads/2017/09/221548.jpg')
                            embed.add_field(name="Level", value=levelUp, inline=True)
                            embed.add_field(name="Race", value=f"{data['race']}", inline=True)
                            embed.add_field(name="Class", value=f"{data['class']}", inline=True)
                            embed.add_field(name="Strength", value=f"{data['str']}", inline=True)
                            embed.add_field(name="XP", value=f"{data['xp']}", inline=True)
                            embed.add_field(name="HP", value=f"{data['hp']}", inline=True)
                            embed.add_field(name="Dexterity", value=f"{data['dex']}", inline=True)
                            embed.add_field(name="Head", value=f"{idNames[data['head']]}", inline=True)
                            embed.add_field(name="Torso", value=f"{idNames[data['torso']]}", inline=True)
                            embed.add_field(name="Constitution", value=f"{data['con']}", inline=True)
                            embed.add_field(name="Hands", value=f"{idNames[data['hands']]}",
                                            inline=True)
                            embed.add_field(name="Feet", value=f"{idNames[data['feet']]}", inline=True)
                            embed.add_field(name="Intelligence", value=f"{data['int']}", inline=True)
                            embed.add_field(name="Right Hand", value=f"{idNames[data['right_hand']]}", inline=True)
                            embed.add_field(name="Left Hand", value=f"{idNames[data['left_hand']]}", inline=True)
                            embed.add_field(name="Wisdom", value=f"{data['wis']}", inline=True)
                            embed.add_field(name="Legs", value=f"{idNames[data['legs']]}", inline=True)
                            embed.add_field(name='\u200b', value='\u200b', inline=True)
                            embed.add_field(name="Charisma", value=f"{data['cha']}", inline=False)
                            await sheetMessage.edit(embed=embed)


                    except asyncio.TimeoutError:
                        await sheetMessage.clear_reaction(reaction)
                        return

            except Exception as e:
                print(str(e))
                await ctx.send("Sorry, doesn't look like we have any data for you. Try registering a character with #register")
        else:
            try:
                myData = await db_query(f"""SELECT * FROM adventureData WHERE id = {user.id}""")
                data = myData[0]
                await ctx.send(data)
                embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at,
                                      description="")
                embed.set_author(name=f"{user.name}", icon_url=user.avatar_url)
                embed.set_thumbnail(
                    url='https://i0.wp.com/www.sageadvice.eu/wp-content/uploads/2017/09/221548.jpg')
                embed.add_field(name="Level", value=levelUp, inline=True)
                embed.add_field(name="Race", value=f"{data['race']}", inline=True)
                embed.add_field(name="Class", value=f"{data['class']}", inline=True)
                embed.add_field(name="Strength", value=f"{data['str']}", inline=True)
                embed.add_field(name="XP", value=f"{data['xp']}", inline=True)
                embed.add_field(name="HP", value=f"{data['hp']}", inline=True)
                embed.add_field(name="Dexterity", value=f"{data['dex']}", inline=True)
                embed.add_field(name="Head", value=f"{idNames[data['head']]}", inline=True)
                embed.add_field(name="Torso", value=f"{idNames[data['torso']]}", inline=True)
                embed.add_field(name="Constitution", value=f"{data['con']}", inline=True)
                embed.add_field(name="Hands", value=f"{idNames[data['hands']]}",
                                inline=True)
                embed.add_field(name="Feet", value=f"{idNames[data['feet']]}", inline=True)
                embed.add_field(name="Intelligence", value=f"{data['int']}", inline=True)
                embed.add_field(name="Right Hand", value=f"{idNames[data['right_hand']]}", inline=True)
                embed.add_field(name="Left Hand", value=f"{idNames[data['left_hand']]}", inline=True)
                embed.add_field(name="Wisdom", value=f"{data['wis']}", inline=True)
                embed.add_field(name="Legs", value=f"{idNames[data['legs']]}", inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name="Charisma", value=f"{data['cha']}", inline=False)
                embed.add_field(name="Left Hand", value=f"{idNames[data['left_hand']]}", inline=True)
                await ctx.send(embed=embed)
            except Exception as e:
                print(str(e))
                await ctx.send("Sorry, doesn't look like we have any data for them.")

    @commands.command()
    async def setclass(self,ctx,args=None):
        x = await db_query(f'''SELECT class FROM adventureData WHERE id = {ctx.author.id}''')
        if x[0]['class'] != None:
            await ctx.send("You already have a class buddy, you'll need a new character to pick again.")
            return
        if args == None or args.lower() not in classes:
            content = f"You're gonna need to pick a valid class there by typing your class after !setclass.\n"
            content += f"Now keep in mind that each class gets a specific attribute bonus:\nConstitution: Paladin, Monk\nIntelligence: Wizard, Warlock\nCharisma: Bard, Sorcerer\nDexterity: Rogue, Ranger\nWisdom: Cleric, Druid\nStrength: Barbarian, Fighter"
            await ctx.send(content)
        else:
            cPick = args.lower()
            await ctx.send(f"Are you sure you want to pick a {args.title()}? This will come with a boost to {classes[cPick].upper()}, and you don't get to change your mind after. Type Y if so.")
            def check(m):
                return m.author == ctx.author

            try:
                answer = await self.bot.wait_for('message', check=check, timeout=25.0)
            except asyncio.TimeoutError:
                await ctx.send("I guess you need some more time to decide.")
                return
            if answer.content.lower() == 'y':
               x = await db_query(f"""UPDATE adventureData SET class = '{cPick}', {classes[cPick]} = {classes[cPick]} + 1 WHERE id = {ctx.author.id}""")
               await ctx.send(f"Class set! You're now a {cPick.title()}.")
            else:
                await ctx.send("That's ok, you can pick again later.")
                return

    @commands.command()
    async def raid(self,ctx):
        keys = {}
        x = await db_query(f"""SELECT * FROM inv{ctx.author.id} WHERE name IN ('Green Dungeon Key','Blue Dungeon Key','Black Dungeon Key','Red Dungeon Key','White Dungeon Key')""")
        if len(x) == 0:
            await ctx.send("You exit the town and head to The Tombs. There are several keyholes in a large center obilisk, each with a distinct color. Unfortunately you don't have any matching keys.")
            return
        for each in x:
            keys[each['name'].lower().split()[0]] = each['id']
        await ctx.send("You exit the town and head to The Tombs. There are several keyholes in a large center obelisk, each with a distinct color. Which key would you like to use?")
        def is_correct(m):
            return m.author == ctx.author and m.content.lower() in list(keys.keys())
        try:
            select = await self.bot.wait_for('message', check=is_correct, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send('After contemplating for a while, you decide to come back to the dungeon another day.')
            return
        await ctx.send(f"Taking the {select.content.title()} Key out you place it into the obelisk's keyhole. After turning the key shatters, the ground shakes and a nearby tomb opens. Before you step inside, who will accompany you?")
        embed = discord.Embed(color=ctx.author.color,description="")
        #embed.set_thumbnail(url='https://i0.wp.com/www.sageadvice.eu/wp-content/uploads/2017/09/221548.jpg')
        embed.add_field(name=f"{ctx.author.name} has started a raid into The Tombs! Who will join their attempt?",
                        value='In a Tomb raid you will not earn XP or loot from killing enemies. Only the survivor(s) that make it past the final boss will reap their rewards.', inline=True)
        tombMessage = await ctx.send(embed = embed)
        await adjustItem(ctx.author.id,keys[select.content.lower()],1,'remove')
        await tombMessage.add_reaction('👍')
        raidMembers = [ctx.author]
        def check(reaction, user):
            return str(reaction.emoji) in ['👍'] and user != ctx.author

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)

                if str(reaction.emoji) == '👍':
                    if user.name != "Hew Hackinstone":
                        raidMembers.append(user)
            except asyncio.TimeoutError:
                await tombMessage.delete()
                break
        class Player():
            def __init__(self,user,hp,ac,weapon,potions,gremlin,stat,init,damage,acc,level,con):
                self.user = user
                self.hp = hp
                self.maxHP = hp
                self.ac = ac
                self.weapon = weapon
                self.potions = potions
                self.gremlin = gremlin
                self.stat = stat
                self.init = init
                self.damage = damage
                self.acc = acc
                self.choice = ''
                self.level = level
                self.con = con

        raidFighters = []
        for member in raidMembers:
            gremlin = False
            stuff = await db_query(f"""SELECT * FROM adventureData WHERE id = {member.id}""")
            playerInv = await db_query(f"""SELECT * FROM inv{member.id}""")
            p1hPots = 0
            for each in playerInv:
                if each['id'] == 21:
                    gremlin = True
                elif each['id'] == 38:
                    p1hPots = each['quantity']

            p1AC = 0
            p1Arm = []
            idNames = {}
            idDamage = {}
            idArmor = {}
            idLoot = {}
            idStats = {}
            itemData = await db_query(f"""SELECT * FROM items""")
            for each in itemData:
                idNames[each['item_id']] = each['name']
                idDamage[each['item_id']] = each['damage']
                idArmor[each['item_id']] = each['armor']
                idLoot[each['item_id']] = each['loot_table']
                idStats[each['item_id']] = each['attr_bonus']

            each = stuff[0]
            p1HP = each['hp']
            p1Con = each['con']
            p1toHit = each['level']
            p1Weapon = each['right_hand'] if each['right_hand'] != None else 111
            p1Stat = each[idStats[p1Weapon]]
            p1Init = each['dex']
            p1Damage = idDamage[p1Weapon].split('d')
            p1Acc = each['left_hand']
            p1Arm.append(each['head'])
            if each['torso'] != None:
                p1AC = idArmor[each['torso']]
            else:
                p1AC = 10
            p1Arm.append(each['legs'])
            p1Arm.append(each['hands'])
            p1Arm.append(each['feet'])
            for each in p1Arm:
                if each != None:
                    p1AC += idArmor[each]
            raidFighters.append(Player(member,p1HP,p1AC,p1Weapon,p1hPots,gremlin,p1Stat,p1Init,p1Damage,p1Acc,p1toHit,p1Con))
        difficulty = {'blue': 3, 'green': 5, 'red': 9, 'white': 15, 'black': 20}
        raidXP = {'blue': 2000, 'green': 5000, 'red': 12000, 'white': 22000, 'black': 45000}
        fights = {'blue': 4, 'green': 5, 'red': 6, 'white': 8, 'black': 10}
        bossDifficulty = {'blue': 101, 'green': 102, 'red': 103, 'white': 104, 'black': 105}
        enemyList = await db_query(f"""SELECT * FROM enemies WHERE difficulty < {difficulty[select.content.lower()] +1}""")
        for i in range(fights[select.content.lower()]):
            results = await raidBattle(self.bot,ctx,raidFighters,random.choice(enemyList)['enemy_id'],idDamage,idNames,idLoot,idStats)
            if results[0] == False:
                return
            else:
                raidFighters = results[1]
        results = await raidBattle(self.bot,ctx,raidFighters,bossDifficulty[select.content.lower()],idDamage,idNames,idLoot,idStats)
        if results[0] == False:
            return
        else:
            raidFighters = results[1]
        await ctx.send(f"**The party has beaten the dungeon!**\n Each surviving member earns {round(raidXP[select.content.lower()]/len(raidFighters))} XP and the following loot has been distributed:")
        lootItems = await db_query(f"""SELECT * FROM items WHERE loot_table < {difficulty[select.content.lower()] +1}""")
        lootContent = ''
        totalLoot = random.randint(2,difficulty[select.content.lower()]*2)
        for each in raidFighters:
            await giveXP(each.user.id,round(raidXP[select.content.lower()]/len(raidFighters)))
            coinWin = random.randint(200,difficulty[select.content.lower()]*1000)
            lootContent+= f"**{each.user.name}:**\n"
            lootContent += f"{coinWin} Coins\n"
            await adjustMoney(each.user.id,coinWin)
            for every in range(round(totalLoot/len(raidFighters))):
                myLoot = random.choice(lootItems)
                lootContent += myLoot['name']+'\n'
                await adjustItem(each.user.id,myLoot['item_id'])
        await ctx.send(lootContent)


    @commands.command()
    async def dungeon(self,ctx):
        x = await db_query(f"""SELECT * FROM inv{ctx.author.id} WHERE name IN ('Green Dungeon Key','Blue Dungeon Key','Black Dungeon Key','Red Dungeon Key','White Dungeon Key')""")
        if len(x) == 0:
            await ctx.send("You exit the town and head to the local dungeon. There are several entrances each with a stone door, colored locks can be seen in the center of each door. Unfortunately you don't have any matching keys.")
            return
        keys = {}
        for each in x:
            keys[each['name'].lower().split()[0]] = each['id']
        await ctx.send("You exit the town and head to the local dungeon. Approaching the multiple entrances, you take note of the colored locks in each stone door. What color key would you like to use?")

        def is_correct(m):
            return m.author == ctx.author and m.content.lower() in list(keys.keys())
        try:
            select = await self.bot.wait_for('message', check=is_correct, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send('After contemplating for a while, you decide to come back to the dungeon another day.')
            return
        await adjustItem(ctx.author.id,keys[select.content.lower()],1,'remove')
        await ctx.send(f"Taking the {select.content.title()} Key out, you approach the door with the corresponding lock. After some effort, the key turns and you walk into the foreboding structure.")
        difficulty = {'blue': 3, 'green': 5, 'red': 9, 'white': 15, 'black': 20}
        bossDifficulty = {'blue':101,'green':102,'red':103,'white':104,'black':105}
        enemyOptions = await db_query(f"""SELECT * FROM enemies WHERE difficulty < {difficulty[select.content.lower()]}""")
        boss = await db_query(f"""SELECT * FROM enemies WHERE difficulty = {bossDifficulty[select.content.lower()]}""")
        first = True
        for i in range(3,random.randint(5,10)):
            if first == True:
                win = await battle(self.bot,ctx,ctx.author.id,random.choice(list(enemyOptions))['enemy_id'])
                first = False
            else: win = await battle(self.bot,ctx,ctx.author.id,random.choice(list(enemyOptions))['enemy_id'],win[1])
            if win[0] == False: return
        await ctx.send(f"Finally, you've made it to the boss of the dungeon. One last battle.")
        bossWin = await battle(self.bot,ctx,ctx.author.id,boss[0]['enemy_id'],win[1])
        if bossWin[0]:
            await ctx.send(f"**{ctx.author.name} cleared the {select.content.title()} dungeon!** Looting the final chamber you find the following:")
            content = ''
            loot = await db_query(f"""SELECT * FROM items WHERE rarity IN ('Common','Uncommon','Rare')""")
            coinWin = random.randint(200,8000)
            content += f'{coinWin} coins\n'
            await adjustMoney(ctx.author.id,coinWin)
            for i in range(random.randint(2,5)):
                thisLoot = random.choice(list(loot))
                content += thisLoot['name']+'\n'
                await adjustItem(ctx.author.id,thisLoot['item_id'])
            await ctx.send(content)

    #Activity Commands
    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fish(self,ctx):
        fishList = await db_query(f'''SELECT * FROM items WHERE type = 'Fish' ''')
        myFish = random.choice(list(fishList))
        catch = random.randint(1,9)
        if catch > 3:
            await ctx.send(f'You caught a **{myFish["name"]}**!')
            await adjustItem(ctx.author.id,myFish["item_id"])
        else:
            await ctx.send("Nothing's biting right now, sorry.")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hunt(self,ctx):
        animalList = await db_query(f'''SELECT * FROM items WHERE type = 'Animal' ''')
        myAnimal = random.choice(list(animalList))
        catch = random.randint(1,30)
        if catch > 10:
            if myAnimal['name'] == 'Baby Owlbear':
                if random.randint(1,2) == 1:
                    await ctx.send(f"You killed a **{myAnimal['name']}**! Before you can take it, you hear a screeching hoot from behind you!")
                    win = await battle(self.bot,ctx,ctx.author.id,10)
                    if win[0]:
                        y = await adjustItem(ctx.author.id, myAnimal['item_id'])
                        await ctx.send("After killing the mother, you take the baby's corpse as your prize as well.")
                    return
                else:
                    await ctx.send(f"You killed a **{myAnimal['name']}**!")
                    y = await adjustItem(ctx.author.id, myAnimal['item_id'])
                    return

            y = await adjustItem(ctx.author.id,myAnimal['item_id'])
            if y[0]:
                await ctx.send(f'You killed a **{myAnimal["name"]}**!')
            else:
                await ctx.send(y[1])
        else:
            await ctx.send("Couldn't find a thing.")

    @commands.command()
    async def give(self,ctx,user: discord.Member = None,*,args = None):
        if user == None or args == None:
            await ctx.send("If you want to give an item or coins you need to @ someone, and then say what you're giving. You can put a number after to give more than one.")
            return
        try:
            itemName, itemQty = [i for i in re.split(r'(\d+)', args) if i]
        except:
            itemName = args
            itemQty = 1
        itemQty = int(itemQty)
        itemName = itemName.strip()
        if itemName.lower() in ['coin','coins','money','gold','cash']:
            myMoney = await db_query(f"""SELECT money FROM adventureData WHERE id = {ctx.author.id}""")
            if myMoney[0]['money'] < itemQty:
                await ctx.send("You don't have that much money.")
                return
            await adjustMoney(ctx.author.id,itemQty,'remove')
            await adjustMoney(user.id,itemQty)
            await ctx.send(f"{ctx.author.name} gave {user.name} {itemQty} coins.")
        else:
            valid = await isValid(itemName)
            if valid[0]:
                hasItem = False
                hasEnough = False
                inventory = await db_query(f"""SELECT * FROM inv{ctx.author.id}""")
                for each in inventory:
                    if each['id'] == valid[1]['item_id']:
                        hasItem = True
                        if each['quantity'] >= itemQty:
                            hasEnough = True
                if hasItem and hasEnough:
                    await adjustItem(ctx.author.id, valid[1]['item_id'], itemQty, 'remove')
                    await adjustItem(user.id, valid[1]['item_id'], itemQty)
                    await ctx.send(f"{ctx.author.name} gave {user.name} {itemName} X {itemQty}")
                elif hasItem == False:
                    await ctx.send("You don't have that item")
                else:
                    await ctx.send("You don't have that many of those.")
            else:
                await ctx.send("That's not a valid item.")

    @commands.command()
    async def sell(self,ctx,*,args=None):
        if args == None:
            await ctx.send("Hey pal, you need to tell me what you're selling. You can also put a number after if you'd like to sell more than one.")
            return
        #if args.lower() == 'all':
            #await ctx.send("Really? All of it? Are you sure?")
        try:
            itemName, itemQty = [i for i in re.split(r'(\d+)', args) if i]
        except:
            itemName = args
            itemQty = 1
        itemName = itemName.strip()
        valid = await isValid(itemName)
        if not valid[0]:
            await ctx.send("Sorry, that's an invalid item.")
            return
        else:
            result2 = await adjustItem(ctx.author.id,valid[1]['item_id'],itemQty,"remove")
            if result2[0]:
                result = await adjustMoney(ctx.author.id, valid[1]['sell_value'] * int(itemQty))
                if result[0]:
                    await ctx.send(f"Sold for {valid[1]['sell_value']*int(itemQty)}!")
                else:
                    await ctx.send(result[1])
            else:
                await ctx.send(result2[1])

    @commands.command()
    async def buy(self,ctx,*,args=None):
        if args == None:
            await ctx.send("Hey pal, you need to tell me what you're buying. You can also put a number after if you'd like to sell more than one.")
            return
        try:
            itemName, itemQty = [i for i in re.split(r'(\d+)', args) if i]
        except:
            itemName = args
            itemQty = 1
        itemName = itemName.strip()
        valid = await isValid(itemName)
        if not valid[0]:
            await ctx.send("Sorry, that's an invalid item.")
            return
        else:
            currMoney = await db_query(f"""SELECT money FROM adventureData WHERE id = {ctx.author.id}""")
            if int(currMoney[0]['money']) < valid[1]['buy_value']:
                await ctx.send(f"Yeah, sorry bud. Your {currMoney[0]['money']} coins isn't gonna cut it.")
                return
            result = await adjustMoney(ctx.author.id,valid[1]['buy_value']*int(itemQty),"remove")
            result2 = await adjustItem(ctx.author.id,valid[1]['item_id'],itemQty,)
            if result[0] and result2[0]:
                await ctx.send(f"Purchased for {valid[1]['buy_value']*int(itemQty)}!")
            else:
                if result[0]:
                    await ctx.send(result2[1])
                else:
                    await ctx.send(result[1])

    @commands.command(aliases = ['balance','money','coins'])
    async def bal(self,ctx):
        myMoney = await db_query(f'''SELECT money FROM adventureData WHERE id = {ctx.author.id}''')
        embed = discord.Embed(color=ctx.author.color,description="")
        embed.add_field(name=f"💰 {myMoney[0]['money']}", value=f"{ctx.author.name}'s Coinpurse", inline=True)
        await ctx.send(embed = embed)

    @commands.command(aliases = ['inventory'])
    async def inv(self,ctx):
        myInv = await db_query(f"""SELECT * FROM inv{ctx.author.id}""")
        response = ''
        if len(myInv) == 0:
            await ctx.send("Your inventory is empty.")
            return
        embed = discord.Embed(title="**INVENTORY**", color=0x00d13f)
        embed.set_author(name = f'{ctx.author.name}',icon_url=ctx.author.avatar_url)
        for each in myInv:
            myItem = await itemInfo(each['id'])
            response = ''
            response+= '*'+each['desc']+'*'
            if myItem['damage'] != None:
                response += f'\nDamage: {myItem["damage"]}\nAttribute: {myItem["attr_bonus"].upper()}'
            elif myItem['armor'] != None:
                if myItem['equip_slot'] == 'torso':
                    response += f'\nBase AC: {myItem["armor"]}'
                else:
                    response += f'\nArmor: {myItem["armor"]}'
            response+=f"\nSell price: {myItem['sell_value']}\n"
            embed.add_field(name=f"**{each['name']}** X {each['quantity']}",value=response,inline=True)
        await ctx.author.send(embed=embed)

    @commands.command(aliases = ['shop'])
    async def store(self,ctx):
        items = await db_query(f''' SELECT * FROM items WHERE buy_value IS NOT NULL''')
        embedShop = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embedWeapons = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embedArmor = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embedShop.set_author(name="Shop - General")
        embedWeapons.set_author(name="Shop - Weapons")
        embedArmor.set_author(name="Shop - Armor")
        for each in items:
            shopValShop = f"*{each['description']}*\nCost: {each['buy_value']}"
            shopValWeapons = f"*{each['description']}*\nCost: {each['buy_value']}"
            shopValArmor = f"*{each['description']}*\nCost: {each['buy_value']}"
            if each['damage'] != None:
                shopValWeapons += f'\nDamage: {each["damage"]}\nAttribute: {each["attr_bonus"].upper()}'
                embedWeapons.add_field(name=each['name'], value=shopValWeapons, inline=True)
            elif each['armor'] != None:
                if each['equip_slot'] == 'torso':
                    shopValArmor += f'\nBase AC: {each["armor"]}'
                else:
                    shopValArmor += f'\nArmor: {each["armor"]}'
                embedArmor.add_field(name=each['name'], value=shopValArmor, inline=True)
            else:
                embedShop.add_field(name=each['name'], value=shopValShop, inline=True)
        shopMessage = await ctx.send(embed=embedShop)
        await shopMessage.add_reaction('🧺')
        await shopMessage.add_reaction("🗡️")
        await shopMessage.add_reaction("🦾")
        await shopMessage.add_reaction('🚪')
        page = 'shop'
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🗡️", "🦾", '🧺','🚪']
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == '🗡️' and page != 'weapons':
                    page = 'weapons'
                    await shopMessage.edit(embed=embedWeapons)

                elif str(reaction.emoji) == '🦾' and page != 'armor':
                    page = 'armor'
                    await shopMessage.edit(embed=embedArmor)

                elif str(reaction.emoji) == '🧺' and page != 'shop':
                    page = 'shop'
                    await shopMessage.edit(embed=embedShop)
                elif str(reaction.emoji) == '🚪':
                    await shopMessage.delete()

                await shopMessage.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await shopMessage.delete()
                break

    @commands.command()
    async def equip(self,ctx,*,args=None):
        if args == None:
            await ctx.send("Hold on, you need to tell me what we're equipping when you use that command.")
            return
        valid = await isValid(args)
        if valid[0]:
            hasItem = False
            inventory = await db_query(f"""SELECT * FROM inv{ctx.author.id}""")
            for each in inventory:
                if each['id'] == valid[1]['item_id']:
                    hasItem = True
            if hasItem == False:
                await ctx.send("You have to have the item in your inventory to equip it.")
                return
            currItem = await db_query(f"""SELECT {valid[1]['equip_slot']} FROM adventureData WHERE id = {ctx.author.id}""")
            if currItem[0][valid[1]['equip_slot']] not in [None,'None']:
                x = await adjustItem(ctx.author.id,currItem[0][valid[1]['equip_slot']])
                if not x:
                    await ctx.send("Oh hey, something went wrong.")
                    return
            y = await adjustItem(ctx.author.id,valid[1]['item_id'],1,"remove")
            z = await db_query(f"""UPDATE adventureData SET {valid[1]['equip_slot']} = {valid[1]['item_id']} WHERE id = {ctx.author.id}""")
            if y and z:
                await ctx.send("Item equipped!")
            else:
                await ctx.send("Oops, something went wrong there.")
        else:
            await ctx.send("Hey now, that's not a valid item.")

    @commands.command(aliases = ['explore'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def search(self,ctx):
        uniqueList = []
        while len(uniqueList) < 3:
            x = random.choice(places)
            if x.lower() not in uniqueList:
                uniqueList.append(x.lower())
        await ctx.send("Let's take a look around. Where do you want to search?")
        await ctx.send(', '.join(uniqueList).title())
        def is_correct(m):
            return m.author == ctx.author and m.content.lower() in uniqueList
        try:
            select = await self.bot.wait_for('message', check=is_correct, timeout=15.0)
        except asyncio.TimeoutError:
            await ctx.send('Sorry, guess you\'re not there anymore.')
        await ctx.send(f"Searching the {select.content.title()}!")
        odds = random.randint(1,100)
        if odds < 5:
            y = await adjustMoney(ctx.author.id,random.randint(1,300),"remove")
            if y[0]:
                await ctx.send(f"While searching the {select.content.title()} you trip and hit your head, blacking out. When you wake up, you realize you've lost some coins.")
            else:
                await ctx.send(f"While searching the {select.content.title()} you trip and hit your head, blacking out. You can tell you were searched, but I guess whoever tried to rob you had pity.")
        elif odds < 25:
            await ctx.send(f'Before you can search the {select.content.title()} you\'re ambushed!')
            enemies = await db_query(f"""SELECT * FROM enemies WHERE difficulty < 3""")
            pick = random.choice(list(enemies))
            await battle(self.bot,ctx,ctx.author.id,pick['enemy_id'])
        elif odds <40:
            items = await db_query(f'''SELECT * FROM items WHERE rarity = 'Common' AND type IN ('Weapon','Armor')''')
            myWin = random.choice(list(items))
            y = await adjustItem(ctx.author.id,myWin['item_id'])
            if y[0]:
                await ctx.send(f"While searching around the {select.content.title()} you were lucky enough to find a {myWin['name']}!")
            else:
                await ctx.send(
                    f"While searching around the {select.content.title()} you were lucky enough to find a {myWin['name']}!\nSomeone else grabbed it before you though.")
        elif odds <60:
            items = await db_query(
                f'''SELECT * FROM items WHERE rarity IN ('Common','Uncommon') AND type IN ('Animal','Fish')''')
            myWin = random.choice(list(items))
            y = await adjustItem(ctx.author.id,myWin['item_id'])
            if y[0]:
                await ctx.send(f"While scouring the {select.content.title()} you stumbled across a dead {myWin['name']}! It's still fresh enough to take with you.")
            else:
                await ctx.send(f"While scouring the {select.content.title()} you stumbled across a dead {myWin['name']}!\nEw, it's all rotted though, no good.")
        elif odds <70:
            randMoney = random.randint(1,600)
            y = await adjustMoney(ctx.author.id,randMoney)
            if y[0]:
                await ctx.send(f"You had almost given up on searching the {select.content.title()} when you found a coinpurse with {randMoney} coins!")
            else:
                await ctx.send(f"You had almost given up on searching the {select.content.title()} when you found a coinpurse!\nAw..it's empty though.")
        else:
            await ctx.send(f"You search all around the {select.content.title()}, high and low, but there's nothing to be found.")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fightDoesntWork(self,ctx,user: discord.Member = None):
        if ctx.prefix == '#':
            if user == None:
                await ctx.send("I see you're excited but you have to include who you want to fight.")
                return
            stuff = await db_query(f"""SELECT * FROM adventureData WHERE id in ({ctx.author.id},{user.id})""")
            p1AC = 0
            p2AC = 0
            p1Arm = []
            p2Arm = []
            for each in stuff:
                if each['id'] == ctx.author.id:
                    p1HP = each['hp']
                    p1MaxHP = p1HP
                    p1Weapon = each['right_hand']
                    if p1Weapon == None:
                        p1Weapon = 111
                    p1Damage = idStats[p1Weapon].split('d')
                    p1Acc = each['left_hand']
                    p1Arm.append(each['head'])
                    if each['torso'] != None:
                        p1AC = idArmor[each['torso']]
                    else:
                        p1AC = 10
                    p1Arm.append(each['legs'])
                    p1Arm.append(each['hands'])
                    p1Arm.append(each['feet'])
                else:
                    p2HP = each['hp']
                    p2MaxHP = p2HP
                    p2Weapon = each['right_hand']
                    if p2Weapon == None:
                        p2Weapon = 111
                    p2Damage = idStats[p2Weapon].split('d')
                    p2Acc = each['left_hand']
                    p2Arm.append(each['head'])
                    if each['torso'] != None:
                        p2AC = idArmor[each['torso']]
                    else:
                        p2AC = 10
                    p2Arm.append(each['legs'])
                    p2Arm.append(each['hands'])
                    p2Arm.append(each['feet'])
            for each in p1Arm:
                if each != None:
                    p1AC += idArmor[each]
            for each in p2Arm:
                if each != None:
                    p2AC += idArmor[each]


            await ctx.send(f"Here we go! Looks like we have <@{ctx.author.id}> and <@{user.id}> going at it!")
            embed = discord.Embed(title="Fight!",description=f"A battle to the near death between {ctx.author.name} and {user.name}",color=0x00d13f)
            embed.add_field(name=f"{ctx.author.name}", value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```", inline=True)
            embed.add_field(name=f"{user.name}", value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```", inline=True)
            await ctx.send(embed=embed)
            x=random.randint(1,2)
            if x ==1: turn = True
            else: turn=False
            while True:
                if turn==True:
                    if random.randint(1,20) < p2AC:
                        await ctx.send(f'{ctx.author.name} misses.')
                    else:
                        damage = 0
                        for each in range(int(p1Damage[0])):
                            damage += random.randint(1,int(p1Damage[1]))
                            p2HP -= damage
                            await ctx.send(f'{ctx.author.name} hits {user.name} for {damage}!')
                else:
                    if random.randint(1,20) < p1AC:
                        await ctx.send(f'{user.name} misses.')
                    else:
                        damage = 0
                        for each in range(int(p2Damage[0])):
                            damage += random.randint(1,int(p2Damage[1]))
                            p1HP -= damage
                            await ctx.send(f'{user.name} hits {ctx.author.name} for {damage}!')
                        embed = discord.Embed(title="Fight!",description=f"A battle to the near death between {ctx.author.name} and {user.name}",color=0x00d13f)
                        embed.add_field(name=f"{ctx.author.name}",value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```",inline=True)
                        embed.add_field(name=f"{user.name}",value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",inline=True)
                        await ctx.send(embed=embed)
                turn = not turn
                if p1HP <1:
                    await ctx.send(f"{user.name} wins!")
                    embed = discord.Embed(title="Fight Over!",
                                          description=f"{user.name} wins!",
                                          color=0x00d13f)
                    embed.add_field(name=f"{ctx.author.name}",
                                    value=f"```apache\nHP: 1/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```",
                                    inline=True)
                    embed.add_field(name=f"{user.name}",
                                    value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                                    inline=True)
                    await ctx.send(embed=embed)
                    break
                elif p2HP <1:
                    embed = discord.Embed(title="Fight Over!",
                                          description=f"{ctx.author.name} wins!",
                                          color=0x00d13f)
                    embed.add_field(name=f"{ctx.author.name}",
                                    value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```",
                                    inline=True)
                    embed.add_field(name=f"{user.name}",
                                    value=f"```apache\nHP: 1/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                                    inline=True)
                    await ctx.send(embed=embed)
                    break
                await asyncio.sleep(1)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def highlow(self,ctx,arg=None):
        if arg == None:
            await ctx.send("Alright! Let's play some HighLow. I'm gonna toss a card down, then you tell me if the next one is going to be 'higher' or 'lower'. If they tie, or I pull the same card again, nobody wins. First though, how much do you want to bet?")
            def is_correct(m):
                return m.author == ctx.author and m.content.isdigit()

            try:
                bet = await self.bot.wait_for('message', check=is_correct, timeout=15.0)
                bet = bet.content
            except asyncio.TimeoutError:
                await ctx.send('Sorry, guess you\'re not there anymore.')
        else:
            bet = arg
        currMoney = await db_query(f"""SELECT money FROM adventureData WHERE id = {ctx.author.id}""")
        if int(currMoney[0]['money']) < int(bet):
            await ctx.send("You don't even have that much money, get outta here.")
            return
        await ctx.send(
            f"Sounds good, {bet} coins it is. Now let's see how you do. Keep in mind, aces are high.")
        await asyncio.sleep(2)
        myCard = random.choice(list(cards.keys()))
        suits = ['♠', '♦', '♣', '❤']
        embed = discord.Embed(title="", description="")
        embed.add_field(name="HighLow", value=f"**{myCard}**{random.choice(suits)}", inline=True)
        await ctx.send(embed=embed)

        def is_valid(m):
            return m.author == ctx.author and m.content.lower() in ['higher', 'lower', 'high', 'low']

        try:
            answer = await self.bot.wait_for('message', check=is_valid, timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.send('Sorry, guess you\'re not there anymore. Maybe later then.')
            return
        await ctx.send("Next card!")
        await asyncio.sleep(2)
        newCard = random.choice(list(cards.keys()))
        suits = ['♠', '♦', '♣', '❤']
        embed = discord.Embed(title="", description="")
        embed.add_field(name="HighLow", value=f"**{newCard}**{random.choice(suits)}", inline=True)
        await ctx.send(embed=embed)
        # await message.channel.send(f'Values of {cards[myCard]} and {cards[newCard]}. New card is higher: {cards[myCard] < cards[newCard]}. Value type: {type(cards[myCard])},{type(cards[newCard])}')
        if cards[newCard] == cards[myCard]:
            await ctx.send("Well, guess nobody wins this one.")
            return
        if answer.content.lower() == 'higher' or answer.content.lower() == 'high':
            if int(cards[newCard]) > int(cards[myCard]):
                await ctx.send(f"Nice job, you got it right! You earned {math.ceil(int(bet)/2)} coins.")
                await adjustMoney(ctx.author.id, math.ceil(int(bet)/2))
            else:
                await ctx.send("Aw, that's too bad.")
                await adjustMoney(ctx.author.id, int(bet), "remove")
        else:
            if int(cards[newCard]) < int(cards[myCard]):
                await ctx.send(f"Nice job, you got it right! You earned {math.ceil(int(bet)/2)} coins.")
                await adjustMoney(ctx.author.id, math.ceil(int(bet)/2))
            else:
                await ctx.send("Aw, that's too bad.")
                await adjustMoney(ctx.author.id, int(bet), "remove")

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.id == self.bot.user.id:
            return
        if message.channel.id not in [700082874929381400,752265736386379897]:
            return
        oddsNum = random.randint(1,1000)
        if oddsNum <= 10:
            await message.channel.send("*A small fairy appears and offers a challenge to everyone nearby!*\n\"Quick! Unscramble this word to earn a prize!\"")
            myScramble = random.choice(list(scrambles))
            myQ = await message.channel.send(f"`{myScramble}`")
            def answer(m):
                return m.content.lower() == scrambles[myScramble]
            try:
                ans = await self.bot.wait_for('message', check=answer, timeout=30.0)
            except asyncio.TimeoutError:
                await message.channel.send('"Oh no! I guess nobody can figure it out. I\'ll go try somewhere else then."\n*The fairy zooms off into the distance*')
                await myQ.edit(content="---")
                return
            await message.channel.send(f'"Good job {ans.author.name}! You can keep this as a prize"')
            if random.choice(["Item","Coins"]) == "Coins":
                myWin = random.randint(1,300)
                await adjustMoney(ans.author.id,myWin)
                await message.channel.send(f"*You receive {myWin} coins.*")
                await myQ.edit(content="---")
            else:
                items = await db_query(f'''SELECT * FROM items WHERE rarity IN ('Common','Uncommon')''')
                myWin = random.choice(list(items))
                await adjustItem(ans.author.id,myWin['item_id'])
                await message.channel.send(f"*You receive a {myWin['name']}.*")
                await myQ.edit(content="---")
        elif oddsNum <= 30:
            x = await db_query(f"""SELECT * FROM enemies WHERE difficulty < 7""")
            enemy = random.choice(list(x))
            await message.channel.send(f"A {enemy['name']} is stalking down a nearby path. It looks angry, someone ready to pick a fight?\n'Y' to challenge.")
            def answer(m):
                return m.content.lower() in ['y']
            try:
                ans = await self.bot.wait_for('message', check=answer, timeout=20.0)
            except asyncio.TimeoutError:
                await message.channel.send(f"The {enemy['name']} has left.")
                return
            if ans.content.lower() == 'y':
                x = await battle(self.bot,await self.bot.get_context(ans),ans.author.id,enemy['enemy_id'])

#Functions
async def adjustMoney(id,money,change="add"):
    if change == "add":
        op = '+'
    else:
        op = '-'
        currMoney = await db_query(f"""SELECT money FROM adventureData WHERE id = {id}""")
        if int(currMoney[0]['money']) < int(money):
            return (False,"You don't have that much money")
    x = await db_query(f"""UPDATE adventureData SET money = money {op} {money} WHERE id = {id}""")
    if x:
        return (True,"Success")
    else:
        return (False,"Failed")

async def db_query(args):
    if 'SELECT' in args:
        try:
            async with aiosqlite.connect("hewDB.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(args) as cursor:
                    r = await cursor.fetchall()
                    return r

        except Exception as e:
            print(str(e))
    else:
        try:
            async with aiosqlite.connect("hewDB.db") as db:
                await db.execute(args)
                await db.commit()
            return True

        except Exception as e:
            print(str(e))
            return False

async def db_update(sql_code, values=()):
    try:
        async with aiosqlite.connect("hewDB.db") as db:
            await db.execute(sql_code, values)
            await db.commit()

    except Exception as e:
        print(str(e))

async def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

async def itemInfo(item):
    x = await db_query(f'''SELECT * FROM items WHERE item_id = {item}''')
    return x[0]

async def adjustItem(user,item,newQty=1,change="add"):
    itemQty = 0
    hasItem = False
    if change != "add" and change != "remove":
        return (False,"Invalid operation chosen")
    if item == 0:
        return (False,"Invalid item ID")
    currInv = await db_query(f"""SELECT * FROM inv{user}""")
    for each in currInv:
        if each['id'] == item:
            hasItem = True
            itemQty = each['quantity']
    if hasItem == False and change == "remove":
        return (False,"Item not held")
    if change == "remove":
        if itemQty > int(newQty):
            x = await db_query(f'''UPDATE inv{user} SET quantity = quantity - {newQty} WHERE id = {item}''')
        elif itemQty == int(newQty):
            x = await db_query(f'''DELETE FROM inv{user} WHERE id ={item}''')
        else:
            return (False,"That quantity not held")
        if x:
            return (True,"Success")
        else:
            return (False,"Failed to remove")
    else:
        if hasItem == True:
            try:
                x = await db_query(f'''UPDATE inv{user} SET quantity = quantity + {newQty} WHERE id = {item};''')
            except Exception as e:
                print(str(e))
        else:
            try:
                thisItem = await db_query(f'''SELECT * FROM items WHERE item_id = {item}''')
                x = await db_query(f'''INSERT INTO inv{user} (id,name,desc,stats,quantity) VALUES({item},'{thisItem[0]['name']}','{thisItem[0]['description']}','{thisItem[0]['type']}',{newQty})''')
            except Exception as e:
                print(str(e))
        if x:
            return (True,"Success")
        else:
            return (False,"Failed to add")

async def isValid(itemName):
    item = await db_query(f'''SELECT * FROM items WHERE name = '{itemName.title()}' ''')
    if item:
        return (True,item[0])
    else:
        return (False,0)

async def startQuest(ctx,quest):
    x = await db_query(f"""SELECT * FROM quests WHERE playerID = {ctx.author.id}""")
    if x != None:
        for each in x:
            if int(each['questID']) == quest:
                await ctx.send("You already have this quest. Maybe do the work you were supposed to first?")
                return
        if len(x) > 2:
            await ctx.send("I think that's enough tasks for you. How about you start working on your obligations.")
            return
    myQuest = questList[quest]
    x = await db_query(f"""INSERT INTO quests (playerID,questID,name,desc,type,reward,xp,coins,goal,progress,target,repeatable,completed) VALUES({ctx.author.id},
    {myQuest['questID']},'{myQuest['name']}','{myQuest['desc']}','{myQuest['type']}','{myQuest['reward']}',{myQuest['xp']},{myQuest['coins']},{myQuest['goal']},{myQuest['progress']},
    '{myQuest['target']}',{myQuest['repeatable']},{myQuest['completed']})""")
    await ctx.send(f"Quest accepted! **{myQuest['name']}**")

async def finishQuest(ctx,quest,player = None):
    items = await db_query(f"""SELECT * FROM items""")
    idNames = {}
    for each in items:
        idNames[each['item_id']] = each['name']
    if player == None:
        x = await db_query(f"""SELECT * FROM quests WHERE playerID = {ctx.author.id} AND questID = {quest}""")
        myQuest = x[0]
        await db_query(f'''UPDATE adventureData SET xp = xp + {myQuest['xp']} WHERE id = {ctx.author.id}''')
        await ctx.send(f"**{ctx.author.name} completed the quest {questList[int(quest)]['name']}**")
        response = f'Your reward for this quest is {myQuest["xp"]} XP and '
        rewards = myQuest['reward'].strip('][').split(',')
        payout = []
        for each in rewards:
            if each == '0':
                await adjustMoney(ctx.author.id,questList[int(quest)]['coins'])
                payout.append(str(questList[int(quest)]['coins'])+' coins')
            else:
                await adjustItem(ctx.author.id,int(each))
                payout.append('1 '+idNames[each])
        await ctx.send(response+', '.join(payout))
        if myQuest['repeatable'] == 0:
            x = await db_query(f'''UPDATE quests SET completed = 1 WHERE playerID = {ctx.author.id} AND questID = {quest}''')
            if x:
                return (True, 'Success')
            else:
                return (False, 'Failed')
        else:
            x = await db_query(f'''DELETE FROM quests WHERE playerID = '{ctx.author.id}' AND questID = {quest}''')
            if x:
                return (True,'Success')
            else:
                return (False,'Failed')
    else:
        x = await db_query(f"""SELECT * FROM quests WHERE playerID = {player.user.id} AND questID = {quest}""")
        myQuest = x[0]
        await db_query(f'''UPDATE adventureData SET xp = xp + {myQuest['xp']} WHERE id = {player.user.id}''')
        await ctx.send(f"**{player.user.name} completed the quest {questList[int(quest)]['name']}**")
        response = f'Your reward for this quest is {myQuest["xp"]} XP and '
        rewards = myQuest['reward'].strip('][').split(',')
        payout = []
        for each in rewards:
            if each == '0':
                await adjustMoney(player.user.id, questList[int(quest)]['coins'])
                payout.append(str(questList[int(quest)]['coins']) + ' coins')
            else:
                await adjustItem(player.user.id, int(each))
                payout.append('1 ' + idNames[each])
        await ctx.send(response + ', '.join(payout))
        if myQuest['repeatable'] == 0:
            x = await db_query(
                f'''UPDATE quests SET completed = 1 WHERE playerID = {player.user.id} AND questID = {quest}''')
            if x:
                return (True, 'Success')
            else:
                return (False, 'Failed')
        else:
            x = await db_query(f'''DELETE FROM quests WHERE playerID = '{player.user.id}' AND questID = {quest}''')
            if x:
                return (True, 'Success')
            else:
                return (False, 'Failed')

async def killCheck(ctx,enemy,players = None):
    if players == None:
        x = await db_query(f'''SELECT * FROM quests WHERE playerID = {ctx.author.id}''')
        if x == None:
            return
        for each in x:
            #await ctx.send(each['type'])
            if each['type'] == 'kill' and each['target'] == enemy['name']:
                kills = each['progress']+1
                goal = each['goal']
                if goal <= kills:
                    await finishQuest(ctx,each['questID'])
                    return
                else:
                    x = await db_query(f'''UPDATE quests SET progress = progress + 1 WHERE playerID = {ctx.author.id} AND questID = {each['questID']}''')
                    return
    else:
        for each in players:
            x = await db_query(f'''SELECT * FROM quests WHERE playerID = {each.user.id}''')
            if x == None:
                return
            for every in x:
                # await ctx.send(each['type'])
                if every['type'] == 'kill' and every['target'] == enemy['name']:
                    kills = every['progress'] + 1
                    goal = every['goal']
                    if goal <= kills:
                        await finishQuest(ctx, every['questID'],each)
                        return
                    else:
                        x = await db_query(
                            f'''UPDATE quests SET progress = progress + 1 WHERE playerID = {each.user.id} AND questID = {every['questID']}''')
                        return

async def giveXP(player,xp):
    x = await db_query(f"""UPDATE adventureData SET xp = xp + {xp} WHERE id = {player}""")

async def trivia(bot,ctx):
    if ctx.prefix == '#':
        await ctx.send("Trivia time! You'll only have 15 seconds to answer correctly. All answers are one word/letter/number. First though, what difficulty would you like?\nEasy: 1.5x payout\nMedium: 3x payout\nHard: 5x payout\n\nKeep in mind, only full words for answers. 'Strength' instead of 'str' for example.\nIf your answer is a number, say '6' instead of 'six'")
        def difficulty(m):
            return m.author == ctx.author and m.content.lower() in ['easy', 'medium', 'hard']
        try:
            diff = await self.bot.wait_for('message', check=difficulty, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('Sorry, guess you\'re not there anymore. We can play again later.')
        if diff.content.lower() == 'easy':
            await ctx.send("An easy one huh? Alright then, how much is your bet?")
        elif diff.content.lower() == "medium":
            await ctx.send("One medium question ready to go, but first we need to know your wager.")
        else:
            await ctx.send(
                "Here comes a hard one, I'm not gonna take it easy on you. How much are we risking here?")

        def wager(m):
            return m.author == ctx.author and m.content.isdigit()

        try:
            bet = await self.bot.wait_for('message', check=wager, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send('Sorry, guess you\'re not there anymore. We can play again later.')
        currMoney = await db_query(f"""SELECT money FROM adventureData WHERE id = {ctx.author.id}""")
        if int(currMoney[0]['money']) < int(bet.content):
            await ctx.send("You don't even have that much money, get outta here.")
            return
        await ctx.send("Bet placed! I hope you're ready.")
        await asyncio.sleep(2)
        if diff.content.lower() == "easy":
            question = random.choice(list(easyQuestions.keys()))
            myQ = await ctx.send(question)

            def answer(m):
                return m.author == ctx.author

            try:
                ans = await self.bot.wait_for('message', check=answer, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.send('Time\'s up! Gotta be quicker on the draw there.')
            if ans.content.lower() == easyQuestions[question]:
                await ctx.send("Nice! You got it right.")
                await adjustMoney(ctx.author.id, round(int(bet.content) * 1.5))
            else:
                await ctx.send("Ha, you got that one wrong? Sorry bud.")
                await adjustMoney(ctx.author.id, bet.content, "remove")
        elif diff.content.lower() == "medium":
            question = random.choice(list(mediumQuestions.keys()))
            myQ = await ctx.send(question)

            def answer(m):
                return m.author == ctx.author

            try:
                ans = await self.bot.wait_for('message', check=answer, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.send('Time\'s up! Gotta be quicker on the draw there.')
            if ans.content.lower() == mediumQuestions[question]:
                await ctx.send("Not bad, that's a right answer.")
                await adjustMoney(ctx.author.id, int(bet.content) * 3)
            else:
                await ctx.send("Nope, better luck next time.")
                await adjustMoney(ctx.author.id, bet.content, "remove")
        else:
            question = random.choice(list(hardQuestions.keys()))
            myQ = await ctx.send(question)

            def answer(m):
                return m.author == ctx.author

            try:
                ans = await self.bot.wait_for('message', check=answer, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.send('Time\'s up! Gotta be quicker on the draw there.')
            if ans.content.lower() == hardQuestions[question]:
                await ctx.send("You actually got it right! Wild.")
                await adjustMoney(ctx.author.id, int(bet.content) * 5)
            else:
                await ctx.send("Oof, I don't think I'd have gotten that one either. Sorry pal.")
                await adjustMoney(ctx.author.id, bet.content, "remove")
        await myQ.edit(content="Trivia cleared, so you can't cheat.")

async def raidBattle(bot,ctx,players,enemyID,idDamage,idNames,idLoot,idStats):
    tempEnemy = await db_query(f'''SELECT * FROM enemies WHERE enemy_id = {enemyID}''')
    enemy = tempEnemy[0]
    p2HP = enemy['hp']
    p2AC = enemy['ac']
    p2Dex = enemy['dex']
    p2MaxHP = p2HP
    p2Weapon = enemy['weapon']
    p2Damage = idDamage[p2Weapon].split('d')
    p1Content = '\u200b'
    p2Content = '\u200b'

    embed = discord.Embed(title="Fight!", description=f"Fighting to the death with a {enemy['name']}", color=0x00d13f)
    for each in players:
        embed.add_field(name=f"{each.user.name}",
                    value=f"```apache\nHP: {each.hp}/{each.maxHP}\nAC: {each.ac}\nWeapon: {idNames[each.weapon]}```", inline=True)
    embed.add_field(name=f"{enemy['name']}",
                    value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```", inline=True)
    fightMessage = await ctx.send(embed=embed)
    x = random.randint(1,20)
    if x > random.randint(1,20):
        turn = True
    else:
        turn = False
    while True:
        count = 0
        if turn == True:
            choice = ''
            await fightMessage.add_reaction("⚔️")
            await fightMessage.add_reaction("🏃‍♂️")
            hpotEmoji = bot.get_emoji(746857909358690405)
            await fightMessage.add_reaction(hpotEmoji)
            chosenPlayers = players.copy()
            def check(reaction, user):
                return user in [i.user for i in players] and str(reaction.emoji) in ["⚔️", "🏃‍♂️",'<:orangepotion:746857909358690405>']

            while len(chosenPlayers)> 0:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
                    for each in chosenPlayers:
                        if str(reaction.emoji) == '⚔️' and each.user.name == user.name:
                            each.choice = 'attack'
                            chosenPlayers.remove(each)
                        elif str(reaction.emoji) == '🏃‍♂️' and each.user.name == user.name:
                            each.choice = 'flee'
                            chosenPlayers.remove(each)
                        elif str(reaction.emoji) == '<:orangepotion:746857909358690405>' and each.user.name == user.name:
                            if each.potions <1:
                                await fightMessage.remove_reaction(reaction, user)
                            else:
                                each.choice = 'potion'
                                chosenPlayers.remove(each)
                except asyncio.TimeoutError:
                    for each in players:
                        if each.user.name in chosenPlayers:
                            each.choice = 'flee'
                    break
            for each in players:
                if each.choice == 'attack':
                    if random.randint(1,20)+each.level < p2AC:
                        p1Content +=f'{each.user.name} misses.\n'
                    else:
                        damage = 0
                        for i in range(int(each.damage[0])):
                            damage += random.randint(1,int(each.damage[1]))+round(each.stat/2)
                        p2HP -= damage
                        p1Content+=f'{each.user.name} hits {enemy["name"]} for {damage}!\n'
                elif each.choice == 'flee':
                    attempt = random.randint(1,100)+each.init
                    if attempt > 50+enemy['dex']:
                        players.remove(each)
                        p1Content += f"{each.user.name} has fled!\n"
                    else:
                        p1Content += f"{each.user.name} failed to flee!\n"
                elif each.choice == 'potion':
                    each.potions -=1
                    await adjustItem(each.user.id,38,1,'remove')
                    p1Heal = random.randint(1,4)+random.randint(1,4)+each.con
                    each.hp += p1Heal
                    if each.hp >= each.maxHP:
                        each.hp = each.maxHP
                        p1Content += f'{each.user.name} healed to max HP!\n'
                    else:
                        p1Content += f'{each.user.name} healed for {p1Heal}!\n'
            await fightMessage.clear_reactions()
            if len(players) == 0:
                await ctx.send("**Everyone has fled**")
                await fightMessage.delete()
                return (False, players)
        else:
            target = random.choice(players)
            if random.randint(1,20)+enemy["difficulty"] < target.ac:
                p2Content += f'{enemy["name"]} misses.\n'
            else:
                damage = 0
                for each in range(int(p2Damage[0])):
                    damage += random.randint(1,int(p2Damage[1]))
                target.hp -= damage
                p2Content += f'{enemy["name"]} hits {target.user.name} for {damage}!\n'
        newembed = discord.Embed(title="Fight!",
                                 description=f"Fighting to the death with a {enemy['name']}",
                                 color=0x00d13f)
        for each in players:
            count += 1
            newembed.add_field(name=f"{each.user.name}",
                            value=f"```apache\nHP: {each.hp}/{each.maxHP}\nAC: {each.ac}\nWeapon: {idNames[each.weapon]}```",
                            inline=True)
        newembed.add_field(name=f"{enemy['name']}",
                        value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                        inline=True)
        for each in range(3-((count+1)%3)):
            newembed.add_field(name='\u200b',
                               value='\u200b',
                               inline=True)
        #newembed.add_field(name="\u200b", value=f"\u200b", inline=True)
        newembed.add_field(name=f"Party's Moves",
                           value=f"{p1Content}",
                           inline=True)
        newembed.add_field(name=f"{enemy['name']}'s Moves",
                           value=f"{p2Content}",
                           inline=True)
        await fightMessage.edit(embed=newembed)
        turn = not turn
        for each in players:
            if each.hp < 1:
                players.remove(each)
                if each.gremlin == True:
                    lose = random.randint(1, 4)
                    if lose == 1:
                        lossContent = f"```After a short time, {each.user.name} finds themselves back in town, brought back from the edge of death. Your Security Gremlin died defending your coins.```"
                        await adjustItem(each.user.id, 21, 1, 'remove')
                    else:
                        lossContent = f"```After a short time, {each.user.name} finds themselves back in town, brought back from the edge of death. Thankfully your Security Gremlin defended your coins.```"
                else:
                    lossContent = f"```After a short time, {each.user.name} finds themselves back in town, brought back from the edge of death. Your coins are also a fair bit lighter now.```"
                    x = await db_query(f'''SELECT money FROM adventureData WHERE id = {each.user.id}''')
                    loss = x[0]['money'] / 3
                    await adjustMoney(each.user.id, math.ceil(loss * 2), 'remove')
                    await ctx.send(lossContent)
        if len(players) == 0:
            newembed = discord.Embed(title="Fight Over!",
                                  description=f"{enemy['name']} wins!",
                                  color=0x00d13f)
            for each in players:
                count += 1
                newembed.add_field(name=f"{each.user.name}",
                                value=f"```apache\nHP: {each.hp}/{each.maxHP}\nAC: {each.ac}\nWeapon: {idNames[each.weapon]}```",
                                inline=True)
            newembed.add_field(name=f"{enemy['name']}",
                            value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                            inline=True)
            # newembed.add_field(name="\u200b", value=f"\u200b", inline=True)
            await fightMessage.edit(embed=newembed)
            return (False, 0)
        elif p2HP <1:
            newembed = discord.Embed(title="Fight Over!",
                                  description=f"The Party wins!",
                                  color=0x00d13f)
            for each in players:
                newembed.add_field(name=f"{each.user.name}",
                                   value=f"```apache\nHP: {each.hp}/{each.maxHP}\nAC: {each.ac}\nWeapon: {idNames[each.weapon]}```",
                                   inline=True)
            newembed.add_field(name=f"{enemy['name']}",
                               value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                               inline=True)
            await fightMessage.edit(embed=newembed)
            for each in players:
                pass
                await killCheck(ctx, enemy,players)
            return (True,players)

async def battle(bot,ctx,player,enemyID,startHP = None):
    gremlin = False
    stuff = await db_query(f"""SELECT * FROM adventureData WHERE id = {player}""")
    playerInv = await db_query(f"""SELECT * FROM inv{player}""")
    p1hPots = 0
    for each in playerInv:
        if each['id'] == 21:
            gremlin = True
        elif each['id'] == 38:
            p1hPots = each['quantity']

    p1AC = 0
    p1Arm = []
    idNames = {}
    idDamage = {}
    idArmor = {}
    idLoot = {}
    idStats = {}
    itemData = await db_query(f"""SELECT * FROM items""")
    for each in itemData:
        idNames[each['item_id']] = each['name']
        idDamage[each['item_id']] = each['damage']
        idArmor[each['item_id']] = each['armor']
        idLoot[each['item_id']] = each['loot_table']
        idStats[each['item_id']] = each['attr_bonus']

    each = stuff[0]
    p1HP = each['hp'] if startHP == None else startHP
    p1MaxHP = each['hp']
    p1Con = each['con']
    p1toHit = each['level']
    p1Weapon = each['right_hand'] if each['right_hand'] != None else 111
    p1Stat = idStats[p1Weapon]
    p1Init = each['dex']
    p1Damage = idDamage[p1Weapon].split('d')
    p1Acc = each['left_hand']
    p1Arm.append(each['head'])
    if each['torso'] != None:
        p1AC = idArmor[each['torso']]
    else:
        p1AC = 10
    p1Arm.append(each['legs'])
    p1Arm.append(each['hands'])
    p1Arm.append(each['feet'])
    for each in p1Arm:
        if each != None:
            p1AC += idArmor[each]
    tempEnemy = await db_query(f'''SELECT * FROM enemies WHERE enemy_id = {enemyID}''')
    enemy = tempEnemy[0]
    p2HP = enemy['hp']
    p2AC = enemy['ac']
    p2MaxHP = p2HP
    p2Weapon = enemy['weapon']
    p2Damage = idDamage[p2Weapon].split('d')
    p1Content = '\u200b'
    p2Content = '\u200b'
    embed = discord.Embed(title="Fight!", description=f"Fighting to the death with a {enemy['name']}", color=0x00d13f)
    embed.add_field(name=f"{ctx.author.name}",
                    value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```", inline=True)
    embed.add_field(name=f"{enemy['name']}",
                    value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```", inline=True)
    embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
    fightMessage = await ctx.send(embed=embed)
    x = random.randint(1,20+p1Init)
    if x > random.randint(1,20+enemy['dex']):
        turn = True
    else:
        turn = False
    while True:
        if turn == True:
            choice = ''
            await fightMessage.add_reaction("⚔️")
            await fightMessage.add_reaction("🏃‍♂️")
            if p1hPots > 0:
                hpotEmoji = bot.get_emoji(746857909358690405)
                await fightMessage.add_reaction(hpotEmoji)
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⚔️", "🏃‍♂️",'<:orangepotion:746857909358690405>']

            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == '⚔️':
                    choice = 'attack'
                elif str(reaction.emoji) == '🏃‍♂️':
                    choice = 'flee'
                elif str(reaction.emoji) == '<:orangepotion:746857909358690405>':
                    choice = 'potion'
            except asyncio.TimeoutError:
                choice = 'flee'
            if choice == 'attack':
                if random.randint(1,20)+p1toHit < p2AC:
                    p1Content +=f'{ctx.author.name} misses.\n'
                else:
                    damage = 0
                    for each in range(int(p1Damage[0])):
                        damage += random.randint(1,int(p1Damage[1]))+round(stuff[0][p1Stat]/2)
                    p2HP -= damage
                    p1Content+=f'{ctx.author.name} hits {enemy["name"]} for {damage}!\n'
            elif choice == 'flee':
                attempt = random.randint(1,100)+p1Init
                if attempt > 50+enemy['dex']:
                    await ctx.send("Fled")
                    await fightMessage.delete()
                    return (False,p1HP)
                else:
                    p1Content +=f"{ctx.author.name} failed to flee!\n"
            elif choice == 'potion':
                p1hPots -=1
                await adjustItem(ctx.author.id,38,1,'remove')
                p1Heal = random.randint(1,4)+random.randint(1,4)+p1Con
                p1HP += p1Heal
                if p1HP > p1MaxHP:
                    p1HP = p1MaxHP
                    p1Content += f'{ctx.author.name} healed to max HP!\n'
                else:
                    p1Content += f'{ctx.author.name} healed for {p1Heal}!\n'
            await fightMessage.clear_reactions()
        else:
            if random.randint(1,20)+enemy["difficulty"] < p1AC:
                p2Content += f'{enemy["name"]} misses.\n'
            else:
                damage = 0
                for each in range(int(p2Damage[0])):
                    damage += random.randint(1,int(p2Damage[1]))
                p1HP -= damage
                p2Content += f'{enemy["name"]} hits {ctx.author.name} for {damage}!\n'
        newembed = discord.Embed(title="Fight!",
                                 description=f"Fighting to the death with a {enemy['name']}",
                                 color=0x00d13f)
        newembed.add_field(name=f"{ctx.author.name}",
                           value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```",
                           inline=True)
        newembed.add_field(name=f"{enemy['name']}",
                           value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                           inline=True)
        newembed.add_field(name="\u200b", value=f"\u200b", inline=True)
        newembed.add_field(name=f"{ctx.author.name}'s Moves",
                           value=f"{p1Content}",
                           inline=True)
        newembed.add_field(name=f"{enemy['name']}'s Moves",
                           value=f"{p2Content}",
                           inline=True)
        await fightMessage.edit(embed=newembed)
        turn = not turn
        if p1HP <1:
            if gremlin == True:
                lose = random.randint(1,4)
                if lose == 1:
                    lossContent = f"```After a short time, {ctx.author.name} finds themselves back in town, brought back from the edge of death. Your Security Gremlin died defending your coins.```"
                    await adjustItem(ctx.author.id,21,1,'remove')
                else:
                    lossContent = f"```After a short time, {ctx.author.name} finds themselves back in town, brought back from the edge of death. Thankfully your Security Gremlin defended your coins.```"
            else:
                lossContent = f"```After a short time, {ctx.author.name} finds themselves back in town, brought back from the edge of death. Your coins are also a fair bit lighter now.```"
                x = await db_query(f'''SELECT money FROM adventureData WHERE id = {ctx.author.id}''')
                loss = x[0]['money'] / 3
                await adjustMoney(ctx.author.id, math.ceil(loss * 2), 'remove')
            embed = discord.Embed(title="Fight Over!",
                                  description=f"{enemy['name']} wins!",
                                  color=0x00d13f)
            embed.add_field(name=f"{ctx.author.name}",
                            value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```",
                            inline=True)
            embed.add_field(name=f"{enemy['name']}",
                            value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                            inline=True)
            embed.add_field(name="**YOU ARE DEAD**",value=lossContent,inline=False)
            await fightMessage.edit(embed=embed)
            return (False,0)
        elif p2HP <1:
            embed = discord.Embed(title="Fight Over!",
                                  description=f"{ctx.author.name} wins!",
                                  color=0x00d13f)
            embed.add_field(name=f"{ctx.author.name}",
                            value=f"```apache\nHP: {p1HP}/{p1MaxHP}\nAC: {p1AC}\nWeapon: {idNames[p1Weapon]}```",
                            inline=True)
            embed.add_field(name=f"{enemy['name']}",
                            value=f"```apache\nHP: {p2HP}/{p2MaxHP}\nAC: {p2AC}\nWeapon: {idNames[p2Weapon]}```",
                            inline=True)
            await fightMessage.edit(embed=embed)
            reward = random.choice([0,1])
            if reward == 0:
                rewardCoins = random.randint(1, enemy['max_coins'])
                reward = str(rewardCoins) + ' coins'
                await adjustMoney(ctx.author.id, rewardCoins)
            else:
                while True:
                    reward = random.choice(list(idLoot.keys()))
                    if idLoot[reward] <= enemy['loot_table']:
                        break
                await adjustItem(ctx.author.id, reward)
                reward = 'a ' + idNames[reward]
            await ctx.send(f"You won! After looting the {enemy['name']} you find {reward}!")
            await giveXP(ctx.author.id,enemy['xp'])
            await killCheck(ctx, enemy)
            return (True,p1HP)

async def setup(bot):
    await bot.add_cog(Adventure(bot))