import discord
from discord.ext import commands
import random
import json
#import praw
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import openai
from translate import Translator

languages = ['es','zh','pt','ku','sv','ru','pl','no','ko','la']
#Variables
openai.api_key = "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"
talkMessages = [{'role':'system','content':'''You are a gruff old dwarf named Hew speaking with your human friends. You have fought through the land of Chult, lost your left arm to a dragon in Wyrmheart Mine, and returned the forges of Hrakhamar to your people. These are only some of your adventures and you greatly enjoy referencing them.

Always respond in character. If you need more information or context, or cannot do what they ask, then respond with a simple comment of agreement, disagreement, or something dwarf related.

The following message is their part of the conversation.'''},
                ]

#reddit = praw.Reddit(client_id='XgIctF2pZqaxFQ',
#                     client_secret='h6d4LmnPMo2E2CNtNxwXUNo8gH4',
#                     user_agent='XgIctF2pZqaxFQ Discord bot to retrieve DnD memes by /u/neon_camouflage',
#                     username='neon_camouflage',
#                     password='--Removed--')
#badNames = {'will':'\'I think you mean "Will fucking Weaton"\'','ken':'Art','marinda':'MRWood','drew':'Godberry','katie':'Keya','simone':'D.VA\'s gay best friend','JD':'Home Wrecker','LA':'L.A.','shiloh':'shitowntheclown','mandi':'SagePink','dylan':'Fulgrim','michael':'CENSORED','jason':'Zarrakas','marcey':'ZeroBlue','boe':'Janglez','seth':'fudu'}
#sub = reddit.subreddit('dndmemes')
replyList = ["🇾🇪🇸","🇳🇴","🇹🇭🇮🇸","🇼🇭🇦🇹",['<:Mark:751195373627768903>'],'🇼🇹🇫']
class Events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game("Dungeons and Dragons"))
        print("Hew is awake.")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        print("Member Joined")
        if member.guild.id ==264875262569742347:
            welcomeChannel = self.bot.get_channel(713830625311719536)
            rulesChannel = self.bot.get_channel(693631847489601576)
            linksChannel = self.bot.get_channel(705182332629286994)
            await welcomeChannel.send(f"Welcome to the GFC,{member.mention}! If ya look to yer left you'll see {rulesChannel.mention}, while not exactly a contract I recommend doing what it says in there.\n\nNext we have {linksChannel.mention}, that'll be where all the YouTube and Streaming and whatnot links are hiding. If there's any questions, holler at an admin.")
        print(f'{member} has joined a server.')
        print(f'{member.guild} is the guild.')
        print(f'{member.guild.id} is the guild id.')

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        print(f'{member} has left a server.')

    @commands.Cog.listener()
    async def on_message(self,message):
        print({message})
        print(message.content)
        messContent = message.content
        messChannel = message.channel
        messCheck = messContent.lower().split()
        botReplies = ["You know I could do that too....probably.","Hey, this guy has a checkmark. Where the hell is my checkmark.",f"Hey {message.author.name}, my dad could beat up your dad.",
                      "Who let this guy in here?","You think you're so cool. Wait until they add a captcha in here.","Alright buddy, this town's not big enough for the both of us."]
        if message.author == self.bot.user or message.channel.name == 'hewbris' or message.channel.name == 'political-banter' or message.channel.name == 'music-request-channel' or message.channel.name == 'gfc-rules' or message.channel.name == 'gaming-friends-youtube' or message.channel.id == 700082874929381400:
            print("That's me")
            if message.author == self.bot.user and message.author.id != 700079515556380755:
                if random.randint(1,20) == 20:
                    messChannel.send(random.choice(botReplies))
            return
        #if any(ele in messCheck for ele in badNames):
        #    admin = self.bot.get_user(263036838799867905)
        #    newContent = ''
        #    for each in badNames:
        #        if each in messContent.lower():
        #            newContent = messContent.lower().replace(each, badNames[each])
        #    print("BAD NAME")
        #    daName = str(message.author)
        #    messName = daName.split('#')[0]
        #    await admin.send(f'{message.author} broke a rule:\n' + message.content)
        #    await message.delete()
        #    await messChannel.send(
        #        f"Are ya daft, no names {messName}. Now, what I think you meant to say was:\n" + newContent)
        #elif "hew" in messContent.lower():
        #    print("YES")
        #    emoji = self.bot.get_emoji(693899878568296448)
        #    await message.add_reaction(emoji)
        #with open('stats.txt', 'r') as f:
            #stats = json.load(f)

        #messageTotal = stats['messages']
       # messageTotal += 1
        #stats['messages'] = messageTotal
        if message.author == self.bot.user:
            print("That's me")
            #return
      #  else:
           # try:
               # guy = stats[str(message.author)]
         #   except:
               # stats[str(message.author)] = 1
           # else:
                #stats[str(message.author)] = stats[str(message.author)] + 1

     #       with open('stats.txt', 'w') as f:
     #           json.dump(stats, f, indent=4)
        loopCount = 0
        randNum = random.randint(1, 30)
        if randNum == 13 and message.channel.name != 'admin-channel-chat' and message.channel.name != 'gfc-rules':
            #return
            print("""
    
                    TALKING
    
                        """)
            if random.randint(1,20) > 5:

                #OpenAI Model
                talkMessages.append({'role': 'user', 'content': message.content})
                chat = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo', messages=talkMessages, presence_penalty = 0.7
                )
                reply = chat.choices[0].message.content
                if 'hew' in reply.lower():
                    talkMessages.pop(1)
                    print(reply)
                    return
                else:
                    max_length = 1800
                    messArr = [reply[i:i + max_length] for i in range(0, len(reply), max_length)]
                    for each in messArr:
                        await messChannel.send(each)
                    talkMessages.pop(1)



                #Old/Offline Model

                """seq = message.content
                if seq[-1] not in ['.','?','!']:
                    seq = seq+'.'
                tokenizer = GPT2Tokenizer.from_pretrained('Hugs')
                model = GPT2LMHeadModel.from_pretrained('Hugs')
                sequence = (seq)
                inputs = tokenizer.encode(sequence, return_tensors='pt')
                outputs = model.generate(inputs, max_length=200, do_sample=True, temperature=1, top_k=50)
                text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(text)
                g = text.replace(seq, '')
                s = g.lstrip()
                t1 = s.split('.')[0]
                t2 = s.split('\n')[0]
                tk = t1 if len(t1) < len(t2) else t2
                await messChannel.send(tk)"""

                #subreddit_comments = sub.comments(limit=100)
                #comments_list = list(subreddit_comments)
                #while True:
                #    ment = random.choice(comments_list)
                #    if len(ment.body) < 190:
                #        await messChannel.send(ment.body)
                #        break
                #    elif loopCount > 60:
                #        break
                #    else:
                #        loopCount += 1
            else:
                pick = random.choice(replyList)
                for each in pick:
                    await message.add_reaction(each)
                    '''if pick == '<:Mark:751195373627768903>':
                    with open('markTrack.json', 'r') as f:
                        marks = json.load(f)
                        else:
                            try:
                            guy = marks[str(message.author)]
                        except:
                            marks[str(message.author)] = 1
                        else:
                            marks[str(message.author)] = marks[str(message.author)] + 1

                        with open('stats.txt', 'w') as f:
                            json.dump(marks, f, indent=4)'''
                        #sortedMarks = dict(sorted(marks.items(), key=operator.itemgetter(1), reverse=True))


async def setup(bot):
    await bot.add_cog(Events(bot))