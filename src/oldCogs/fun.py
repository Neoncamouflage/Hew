import discord
import asyncio
import os
from discord.ext import commands
import operator
import random
#import praw
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import openai
from translate import Translator

languages = ['es','zh','pt','ku','sv','ru','pl','no','ko','la']
openai.api_key = "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"
talkMessages = [{'role':'system','content':'''You are a gruff old dwarf named Hew speaking with your human friends. You have fought through the land of Chult, lost your left arm to a dragon in Wyrmheart Mine, and returned the forges of Hrakhamar to your people. These are only some of your adventures and you greatly enjoy referencing them.

Always respond in character. If you need more information or context, or cannot do what they ask, then respond with one of the following options: a dwarven metaphor or idiom; a tale of adventure, humor, or mystery; a sarcastic jab or joke.

The following message is their part of the conversation.'''},
                ]


#Removed password here as it goes to my own Reddit account. Hew needs his own.
#reddit = praw.Reddit(client_id='XgIctF2pZqaxFQ',
#                     client_secret='h6d4LmnPMo2E2CNtNxwXUNo8gH4',
#                     user_agent='XgIctF2pZqaxFQ Discord bot to retrieve DnD memes by /u/neon_camouflage',
#                     username='neon_camouflage',
#                     password='--Removed--')
#sub = reddit.subreddit('dndmemes')
#jokeSub = reddit.subreddit('DMDadJokes')

class Fun(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def suggestion(self,ctx, *, arg):
        f = open('suggestions.txt', 'a+')
        f.write(arg + '\n')
        f.close()
        await ctx.send(f'I\'ll keep that in mind {ctx.author.name}')

    #@commands.command()
    #async def suggestions(self,ctx):
     #   f = open('suggestions.txt', 'r')
      #  contents = f.read()
       # f.close()
        #await ctx.send(contents)

    @commands.command()
    async def oof(self,ctx):
        async with ctx.typing():
            x = random.choice(['No, no more oofing. Get the fuck back to work.', 'Oof yerself mate','745415785358557365',
                                      'MUCKLE DAMRED CULTI \'AIR EH NAMBLIES BE KEEPIN\' ME WEE MEN!?!?',"An oof is just a lazy man's oofda.",
                                          "*Pssssssst hey..... I hear.... You like oofing*\n\n\n*Me too*",
                                          "You know my uncle used to say 'oof' a lot. He was eaten by a dragon. Unrelated, I'm sure, but it makes you think."])
            if x == '745415785358557365':
                x = self.bot.get_emoji(745415785358557365)
            await ctx.send(x)

    #Old/Offline Model
    @commands.command()
    async def speak(self,ctx,*,args):

        #OpenAI Model

        talkMessages.append({'role':'user','content':args})
        chat = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', messages=talkMessages, presence_penalty=0.7
        )
        reply = chat.choices[0].message.content
        #translator = Translator(to_lang=random.choice(languages))
        #cReply = translator.translate(reply)
        if ' this was ai ' in reply.lower():
            talkMessages.pop(1)
            print(reply)
            return
        else:
            max_length = 1800
            messArr = [reply[i:i + max_length] for i in range(0, len(reply), max_length)]
            for each in messArr:
                await ctx.send(each)
            talkMessages.pop(1)
        """


        seq = args
        if seq[-1] not in ['.', '?', '!']:
            seq = seq + '.'
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
        await ctx.send(tk)"""


    """@commands.command()
    async def meme(self,ctx):
        async with ctx.typing():
            imgList = []
            ex = ['png', 'jpg', 'gif']
            picked = False
            randNumber = random.randint(1, 2)
            if randNumber == 1:
                for each in sub.hot(limit=50):
                    imgList.append(each.url)
            else:
                for each in sub.new(limit=50):
                    imgList.append(each.url)
            while picked == False:
                imgPick = random.choice(imgList)
                print(imgPick[len(imgPick) - 3:])
                if imgPick[len(imgPick) - 3:] in ex:
                    print(imgPick[len(imgPick) - 3:0])
                    await ctx.send(imgPick)
                    picked = True

    @commands.command()
    async def tell(self,ctx, *, args):
        async with ctx.typing():
            if 'joke' in args:
                # DMDadJokes
                ex = ['png', 'jpg', 'gif']
                jokeList = []
                randNumber = random.randint(1, 2)
                if randNumber == 1:
                    for each in jokeSub.hot(limit=50):
                        jokeList.append(each)
                else:
                    for each in jokeSub.new(limit=50):
                        jokeList.append(each)
                while True:
                    jokePick = random.choice(jokeList)
                    print(jokePick.is_self)
                    if jokePick.is_self:
                        print("Self pick")
                        print(jokePick.title)
                        print(jokePick.selftext)
                        await ctx.send(jokePick.title)
                        await asyncio.sleep(2)
                        await ctx.send(jokePick.selftext)
                        break
                    elif jokePick.url[len(jokePick.url) - 3:] in ex:
                        await ctx.send(jokePick.title)
                        await asyncio.sleep(2)
                        await ctx.send(jokePick.url)
                        break
                    else:
                        continue"""

    @commands.command()
    async def hangman(self,ctx):
        guessed = []
        hangmen =[
"""
  +---+
  |   |
      |
      |
      |
      |
=========""",
"""  
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
"""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
"""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
"""
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========""",
"""
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========""",
"""
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
========="""]
        step = 0
        with open('words.txt', 'r') as f:
            wordList = f.read()
        word = random.choice(wordList.split('\n'))
        while True:
            currentWord = ''
            for each in range(len(word)):
                if word[each] in guessed:
                    currentWord += word[each]+' '
                else:
                    currentWord += '_ '
            if '_' not in currentWord:
                await ctx.send(f"You win! The word was {word}.")
                break
            elif step == 6:
                await ctx.send(f"You lose! The word was {word}.")
                break
            await ctx.send(f"```Letters guessed: {guessed}\nWord: {currentWord}\n\n{hangmen[step]}```")

            def is_correct(m):
                return m.author == ctx.author
            try:
                select = await self.bot.wait_for('message', check=is_correct, timeout=90.0)
                pick = select.content.lower()
                if pick in ["quit",'end','stop']:
                    await ctx.send(f"Game over, the word was {word}.")
                    break
                if pick.isalpha():
                    if len(pick) == 1:
                        if pick in guessed:
                            await ctx.send("You already guessed that letter!")
                            continue
                        else:
                            guessed.append(pick)
                            if pick not in word:
                                step += 1
                                continue
                    elif len(pick) != len(word):
                        await ctx.send(f"Hey, that's the wrong number of letters. If you want to guess the word, it's {len(word)} letters long.")
                        continue
                    else:
                        if pick == word:
                            await ctx.send("That's right! You win!")
                            break
                        else:
                            await ctx.send("Sorry, that's not the word.")
                            step +=1
                            continue
                else:
                    await ctx.send("Please only guess letters or words.")
                    continue
            except asyncio.TimeoutError:
                await ctx.send(f'You took too long! The word was {word}. Feel free to play again!')
                break
async def setup(bot):
    await bot.add_cog(Fun(bot))