import discord
from discord.ext import commands
import requests
import requests.auth
import random
import math
import json
import datetime
import pytz
import asyncio


mainList=['ability-scores',',classes','conditions','damage-types','equipment-categories','equipment',
'features','languages','magic-schools','monsters','proficiencies','races','skills','spellcasting','spells',
'starting-equipment','subclasses','subraces','traits','weapon-properties']
apiList = {'Spells':'https://www.dnd5eapi.co/api/spells/','Conditions':'https://www.dnd5eapi.co/api/conditions/','Skills':'https://www.dnd5eapi.co/api/skills/',
          'Properties':'https://www.dnd5eapi.co/api/weapon-properties/','Schools':'https://www.dnd5eapi.co/api/magic-schools/'}

class Gaming(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def schedule(self,ctx,*,arg):
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at,
                              description="Please reply with the date and time of the activity.\nRequired format: YYYY-MM-DD H:M TZ\n"
                                          "Time should be in 24 hour format. Current timezones supported are PT, MT, CT, ET, UTC.")
        embed.set_author(name=f"Scheduling for {arg}",icon_url=ctx.author.avatar_url)
        scheduleEmbed = await ctx.send(embed=embed)

        def is_correct(m):
            return m.author == ctx.author

        try:
            tzList = {'PT': 'US/Pacific', 'MT': 'US/Mountain', 'CT': 'US/Central', 'ET': 'US/Eastern', 'UTC': 'UTC'}
            select = await self.bot.wait_for('message', check=is_correct, timeout=90.0)
            dtList = select.content.split(' ')
            dtTime = dtList[1].split(':')
            dtDate = dtList[0].split('-')
            myPing = None
            peepsJoining = []
            print(dtList)
            print(dtTime)
            print(dtDate)
            mySchedule = pytz.timezone(tzList[dtList[2]]).localize(
                datetime.datetime(int(dtDate[0]), int(dtDate[1]), int(dtDate[2]), hour=int(dtTime[0]), minute=int(dtTime[1])))
            print(datetime.datetime.now().astimezone(pytz.timezone(tzList[dtList[2]]))-mySchedule)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at,
                                  description="How do you want to be notified?\n🔴 Ping Me\n🔵 Ping Everyone Joining\nNo Response will default to Ping Everyone")
            embed.set_author(name=f"Scheduling for {arg}", icon_url=ctx.author.avatar_url)
            await scheduleEmbed.edit(embed=embed)
            await scheduleEmbed.add_reaction('🔴')
            await scheduleEmbed.add_reaction('🔵')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["🔴",'🔵']

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if reaction == "🔴":
                    myPing = 1
                else:
                    myPing = 2
            except asyncio.TimeoutError:
                myPing = 1
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at,
                                  description=f"{arg} scheduled for {dtList[1]} {dtList[2]} on {dtList[0]}! React to this if you'd like to be notified!")
            embed.set_author(name=f"{arg}", icon_url=ctx.author.avatar_url)
            await scheduleEmbed.edit(embed=embed)
            await scheduleEmbed.clear_reactions()
            await scheduleEmbed.add_reaction('✅')
            await discord.utils.sleep_until(mySchedule.astimezone(pytz.utc),print("DING!"))
            print("end try")
        except asyncio.TimeoutError:
            await ctx.send('Scheduling timeout, please try again.')
        if myPing == 1:
            await ctx.send(f"It's time for {arg}!{ctx.author.mention}")
        else:
            scheduleEmbed = await ctx.channel.fetch_message(scheduleEmbed.id)
            for reaction in scheduleEmbed.reactions:
                async for user in reaction.users():
                    peepsJoining.append(user)
            peepsJoining.append(ctx.author)
            await ctx.send(f"It's time for {arg}! {','.join(user.mention for user in set(peepsJoining) if user != self.bot.user)}")

    @commands.command()
    async def lookup(self,ctx, *, arg):
        messageStuff = arg
        embedStuff = messageStuff.replace(' ', '%20')
        messageStuff = messageStuff.replace(' ', '-')
        count = 0
        for i in apiList:
            resp = requests.get(apiList[i] + messageStuff.lower())
            if resp.status_code == 200:
                if i == 'Spells':
                    spell = resp.json()
                    content = ''
                    content += 'Level ' + str(spell['level']) + ' ' + spell['school']['name'] + ' spell '
                    if spell['ritual']: content += '(Ritual)'
                    content += '\nCasting Time: ' + spell['casting_time']
                    content += '\nRange: ' + spell['range']
                    content += '\nComponents: '
                    for each in spell['components']:
                        content += each + ' '
                    if 'material' in spell:
                        content += '(' + spell['material'] + ')'
                    content += '\nDuration: '
                    if spell['concentration']: content += 'Concentration, '
                    content += spell['duration']
                    content += '\nClasses: '
                    for each in spell['classes']:
                        content += each['name'] + ' '
                    content += '\n\nDescription:\n*'
                    for each in spell['desc']:
                        content += each
                    content += '*'
                    embed = discord.Embed(title='', url='https://roll20.net/compendium/dnd5e/' + embedStuff,
                                          description=content, color=0xfcba03)
                    embed.set_author(name=spell['name'], url='https://roll20.net/compendium/dnd5e/' + embedStuff)
                    embed.set_thumbnail(
                        url='https://images.discordapp.net/avatars/481910793697493011/84939cb5ee9d5d54c7719e7fdc4fd1fd.png?size=512')
                    # embed.add_field(name=spell['name',value=content,inline=False)
                    await ctx.send(embed=embed)
                elif i == 'Conditions':
                    spell = resp.json()
                    content = ''
                    content += '**' + spell['name'] + '**\n'
                    for each in spell['desc']:
                        content += each + '\n'
                    await ctx.send(content)
                else:
                    spell = resp.json()
                    content = ''
                    content += '**' + spell['name'] + '**\n'
                    for each in spell['desc']:
                        content += each
                    await ctx.send(content)
            else:
                count += 1
                if count == len(apiList):
                    await ctx.send("Aye, you're bad at spelling or I don't have it in my books. Not sure which.")
                    break

    @commands.command()
    async def roll(self,ctx, *, arg):
        nums = arg.strip().split('+')
        dice = []
        adds = 0
        for each in nums:
            if 'd' in each.lower():
                dice.append(each)
            else:
                adds += int(each)
        print(dice)
        rolls = ''
        total = 0
        currentRoll = 0
        for each in dice:
            if each[0].lower() == 'd':
                thisDie = ['1']
                thisDie.append(each.lower().split('d')[1])
                print(each[0])
            else:
                thisDie = each.lower().split('d')
            print("Rolling " + str(thisDie[0]) + " " + str(thisDie[1]))
            for every in range(int(thisDie[0])):
                currentRoll += random.randint(1, int(thisDie[1]))
                rolls += str(currentRoll) + '+'
                print("Got a " + str(currentRoll))
                total += currentRoll
                currentRoll = 0
        if adds != 0: rolls += str(adds) + '+'
        total += adds
        await ctx.send("Rolled: " + rolls[:-1] + "\nTotal: " + str(total))

    @commands.command()
    async def note(self,ctx,*,arg):
        player,roll = arg.split(' ',maxsplit=1)
        with open('drewNotes.txt', 'r') as f:
            notes = json.load(f)
        notes[player] = notes[player].append(roll)
        with open('drewNotes.txt', 'w') as f:
            json.dumps(notes, f, indent=4)

    @commands.command()
    async def teams(self,ctx, *, arg):
        people = arg.split(' ')
        pick = people[0]
        numPeople = len(people)
        content = ''
        print(pick)
        count = 0
        if pick.isnumeric():
            teams = int(pick)
            people.pop(0)
            numPeople = len(people)
            if int(pick) <= 0:
                await ctx.send("You're a funny one eh? Give me a real number to work with here")
            elif int(pick) > numPeople:
                await ctx.send("You want more teams than you have people! Try again.")
        else:
            teams = math.ceil(numPeople / 2)

        while numPeople > 0 and teams > 0:
            count += 1
            try:
                team = random.sample(people, int(numPeople / teams))
            except:
                team = people
            content += 'Team ' + str(count) + ':\n'
            for each in team:
                people.remove(each)
                content += each + ' '
            content += '\n'
            teams -= 1
            numPeople -= len(team)
        await ctx.send(content)

    @commands.command()
    async def add(self,ctx, *, arg):
        with open('rules.txt', 'r') as f:
            rules = json.load(f)

        rules[str(len(rules) + 1)] = arg

        with open('rules.txt', 'w') as f:
            json.dump(rules, f, indent=4)

        await ctx.send(random.choice(remembers))

    @commands.command()
    async def rules(self,ctx):
        with open('rules.txt', 'r') as f:
            rules = json.load(f)
        sayRules = ''
        for each in rules:
            sayRules += str(each) + '. ' + rules[each] + '\n'
        await ctx.send("Here are all the rules so far:\n" + sayRules)


async def setup(bot):
    await bot.add_cog(Gaming(bot))