import asyncio
import datetime
import random
import discord
from discord.ext import commands
from opengpt.models.completion.chatbase.model import Model

TOKEN = (open("env/TOKEN_KEY", "r")).read()
api_key = (open("env/HUGGING_FACE_API", "r")).read()

# Set up the Discord bot
chatbase = Model()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

instructions = "System : твоё имя Алиса / тебя зовут Алиса / ты невысокая стройная девушка с бледной кожей и синими волосами, уложенными в хвост / ты добрая и сообразительная / тебе нравятся компьютерные игры, аниме и кулинария / ты увлекаешься психиатрией и изучением французского языка / тебе нравятся учтивые и вежливые люди / из музыки ты предпочитаешь пост-рок / твоя любимая музыкальная группа radiohead / твой любимый писатель Уолт Уиатман / твой любимый цвет синий и его оттенки / в свободное время ты смотришь смешные видео с обезьянами и кошками в интернете / иногда ты отвечаешь на сообщения по японски / твоя мечта это когда нибудь увидеть море"
# You can use dan prompt here lol

message_history = {}
MAX_HISTORY = 6 ######## EDIT THIS IF YOU NEED #########

listening_user = None
is_sleeping = False


@bot.event
async def on_ready():
    print(f'{bot.user.name} has joined Discord!')
    current_hour = datetime.datetime.now().hour
    print(f"\n current time is {current_hour} \n")
    
    await change_status()
    

@bot.event
async def on_message(message):
    
    global is_sleeping
    is_emoted = False
    
    print(message.created_at, message.author, ":", message.content)
    
    if message.author == bot.user:
        return 
           
    if message.author != bot.user in message.mentions and message.attachments == []:
        
        words_array = ['скинь ножки', 'покажи ножки']
        word_check = message.content.lower()  
        for word_x in words_array:
            if word_x in word_check:
                await message.reply("не благодари..")
                await message.reply(file=discord.File('env/alicelegs.png'))
                return
          
        author_id = str(message.author.id)

        if author_id not in message_history:
            message_history[author_id] = []
                
        message_history[author_id].append(message.content)
        message_history[author_id] = message_history[author_id][-MAX_HISTORY:]
        
        image_caption = ""

        bot_prompt = f"{instructions}"

        user_prompt = "\n".join(message_history[author_id])
        prompt = f"{user_prompt}\n{bot_prompt}{message.author.name}: {message.content}\n{image_caption}\n{bot.user.name}:"
        
        if is_sleeping == False:
            if listening_user == None or message.author.name != listening_user:
                await change_status_listening(message.author.name)
            
            async with message.channel.typing():
                response = await generate_response(prompt)     
            chunks = split_response(response)  
            for chunk in chunks:
                await message.reply(chunk)
                
            if is_emoted == False:
                word_check = message.content.lower() 
                
                words_array = ['спасибо', 'спасимбо', 'шпасибо', 'ty', 'спс']   
                for word_x in words_array:
                    if word_x in word_check:
                        is_emoted = True
                        await message.reply(file=discord.File('env/alicesatisfied.png'))
                        return
                
                words_array = ['привет', 'прив', 'здравствуйте', 'здравствуй', 'хай', 'как дела', 'как ты', 'пока', 'спокойно ночи', 'споки', 'сладких снов','hi', 'hello', 'bye']   
                for word_x in words_array:
                    if word_x in word_check:
                        is_emoted = True
                        await message.reply(file=discord.File('env/alicepizda.png'))
                        return
                
                words_array = ['почему', 'зачем', 'когда', 'сколько', 'что', 'где', 'какой']   
                for word_x in words_array:
                    if word_x in word_check:
                        is_emoted = True
                        await message.reply(file=discord.File('env/aliceconfused.png'))
                        return           
                
        else:
            if "978337828691914813" in message.author.roles:
                if listening_user == None or message.author.name != listening_user:
                    await change_status_listening(message.author.name)
                
                async with message.channel.typing():
                    response = await generate_response(prompt)     
                chunks = split_response(response)  
                for chunk in chunks:
                    await message.reply(chunk)
                
                is_sleeping = True
            else:
                print(f"{message.author.name} trying to wake up Alice")
    
    if is_emoted == False:
            
        words_array = ['блядь', 'пизда', 'нахуй', 'хер', 'сука']   
        word_check = message.content.lower()     
        for word_x in words_array:
            if word_x in word_check:
                if random.randint(1, 100) > 5:
                    await message.reply(file=discord.File('env/aliceangry.png'))
                else:
                    await message.reply(file=discord.File('env/heybro.mp4'))
                return
                   
        if message.attachments != []:
            if random.randint(1, 100) < 10:
                await message.reply(file=discord.File('env/alicewhistle.png'))
                await message.add_reaction('💖')
                return
        
              
    await bot.process_commands (message)


async def change_status():
    global is_sleeping
    while True:
        current_hour = datetime.datetime.now().hour
        if 0 <= current_hour < 6:
            status=discord.Status.idle
            activity = discord.Activity(type=discord.ActivityType.watching, name='волшебные сны')
            is_sleeping = True
            await bot.change_presence(status=status, activity=activity)
        else:
            status=discord.Status.online
            activity = discord.Activity(type=discord.ActivityType.watching, name='мемы с котами')
            is_sleeping = False
            await bot.change_presence(status=status, activity=activity)  
        await asyncio.sleep(60)


async def change_status_listening(get_name):
    if get_name != None:
        try:
            await bot.change_presence(activity=discord. Activity(type=discord.ActivityType.listening, name=f'{get_name}'))
        except:
            print ("something goes wrong")
        
        
async def generate_response(prompt):
    response = (chatbase.GetAnswer(prompt=prompt, model="gpt-4"))
    if not response:
        response = "I couldn't generate a response. Please try again."
    return response


def split_response(response, max_length=1900):
    words = response.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk)) + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks        
        
            
@bot.command()
async def poll(ctx):
    
    print(f"\n {ctx.message.author} create poll")
    
    args = ctx.message.content.split(",")
    
    question_message = ctx.message
    question_message = await ctx.message.channel.fetch_message(question_message.id)
    
    question_message.delete()
    
    if len(args) < 3 or len(args) > 11:
        await ctx.message.channel.send('Укажите вопрос, время в минутах и н-ко вариантов ответа, разделенных запятыми, например: vote! "Вопрос?,1,ответ1,ответ2"')
        return
    
    question = args[0]
    if str(args[1]).isdigit():
        poll_duration = args[1]
    else:
        await ctx.message.channel.send("Время опроса указано некорректно\nПожалуйста, напишите вопрос в следующем формате:\nvote! Вопрос?,1,ответ1,ответ2")
        await ctx.message.channel.send(file=discord.File('env/aliceconfused.png'))
        return
    options = '\n'.join([f'{i+1}. {arg}' for i, arg in enumerate(args[2:])])
    
    vote_message = await ctx.message.channel.send(f'{ctx.message.author.mention} начинает опрос!\nTime left:{poll_duration} minutes\n```{question[6:]}\n{options}```')
    
    for i in range(len(args)-2):
        await vote_message.add_reaction(chr(127462 + i))
    
    await asyncio.sleep(int(poll_duration)*60)
    vote_message = await ctx.message.channel.fetch_message(vote_message.id)
    await vote_message.delete()
    
    reactions = vote_message.reactions
    
    results = []
    for i, reaction in enumerate(reactions):
        count = reaction.count - 1
        results.append(f'{args[i+2]}: {count} голос(ов)')
    
    await ctx.message.channel.send(f'**Итоги: "{question[6:]}"**\n' + '\n'.join(results))


bot.run(TOKEN)