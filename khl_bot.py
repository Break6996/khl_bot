from distutils.cmd import Command
from khl import Bot, EventTypes, Event, Message, MessageTypes
from khl.card import CardMessage, Card, Module, Element, Types
from khl.command import Rule
import requests
import json
import random
import re
import time
from requests.models import Response
from datetime import datetime, timedelta

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

TEST = False

def get_dog():
    response = requests.get('https://api.thedogapi.com/v1/images/search')
    json_data = json.loads(response.text)
    image = json_data[0]['url']
    return image

def get_cat():
    headers = {'x-api-key':config["x-api-key"]}
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    json_data = json.loads(response.text)
    image = json_data[0]['url']
    return image

def get_image(key):
    headers = {'Authorization':config["Authorization"]}
    random.seed(time.time())
    page = random.randint(1, 20)
    response = requests.get(('https://api.pexels.com/v1/search?locale=zh-CN&query='+str(key)+'&per_page=10&page='+str(page)), headers=headers)
    json_data = json.loads(response.text)
    if json_data["total_results"] == 0:
        return ('未查到图片！请更换关键词再次尝试！',"","")
    image = random.choice(json_data["photos"])
    image_url = image["src"]["large2x"]
    photographer = image["photographer"]
    url = image["url"]

    return (image_url,photographer,url)

def get_hso():
    random.seed(time.time())
    page = random.randint(1, 50)
    params = "limit=20&page={}".format(page)
    api_url = "https://konachan.com/post.json?{}".format(params)
    r = requests.get(api_url)
    img_json = r.json()
    if not img_json:
        img = "未能找到所需图片"
    else:
        img = random.choice(img_json)['sample_url']
        print(img)
    return img
    # content = requests.get(img).content
    # # print(content)
    # # print("\n===============================================")
    # with open('demo.jpg', 'wb') as fp:
    #     fp.write(content)
    # # 关闭文件
    # fp.close()
    # return 'demo.jpg'

def get_chat(key):
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg="+str(key)
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data['content']

# init Bot
if (TEST):
    bot = Bot(token=config['token-test'])
    Channel_ID = config['Channel_ID_Test']
else:
    bot = Bot(token=config['token'])
    Channel_ID = config['Channel_ID']

#bot启动
@bot.task.add_date()
async def hey():
    channel = await bot.fetch_public_channel(Channel_ID)
    await channel.send('爷上线啦')

@bot.command(name = 'roll')
async def roll(msg: Message, t_min: int = 0, t_max: int = 6, n: int = 1):
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'傻逼roll点为： {result}')

@bot.command()
async def help(msg: Message):
    cm = CardMessage()
    c = Card(Module.Header('嘴很脏的bot'), color='#5A3BD7')  # color=(90,59,215) is another available form
    c.append(Module.Divider())
    c.append(Module.Section('/dog:云吸狗'))
    c.append(Module.Section('/cat:云吸猫'))
    c.append(Module.Section('/image [key word]:获取超高清无敌画质图片'))
    c.append(Module.Section('/roll [min] [max]:roll点 无参数默认1~6'))
    c.append(Module.Section('/hso:返回色图，能不能打开随缘'))
    c.append(Module.Section('/music [key word]:点歌 （还没做呢）'))
    c.append(Module.Section('/ban @用户:禁言 （还没做呢）'))
    c.append(Module.Section('@机器人可以进行友好交流'))
    cm.append(c)
    await msg.reply(cm)

@bot.command(name = 'dog')
async def dog(msg: Message):
    image = get_dog()
    cm = CardMessage()
    c = Card()
    c.append(Module.Container(Element.Image(image)))
    c.append(Module.Section('我也不知道这是什么品种的狗狗，总之快给老子喊可爱'))
    cm.append(c)
    await msg.reply(cm)

@bot.command(name = 'cat')
async def cat(msg: Message):
    image = get_cat()
    cm = CardMessage()
    c = Card()
    c.append(Module.Container(Element.Image(image)))
    c.append(Module.Section('我也不知道这是什么品种的猫猫，总之快给老子喊可爱'))
    cm.append(c)
    await msg.reply(cm)
    
@bot.command(name = 'image')
async def image(msg: Message,*key: str):
    [image, photographer, url] = get_image(key)
    print(image)
    print(photographer)
    print(url)
    if(url==""):
        await msg.reply(image)
    else:
        cm = CardMessage()
        c = Card()
        c.append(Module.Container(Element.Image(image)))
        c.append(Module.Divider())
        c.append(Module.Context(Element.Text("photographer:"+photographer)))
        c.append(Module.Context(Element.Text("url:"+url)))
        cm.append(c)
        await msg.reply(cm)

@bot.command(name = 'Break')
async def Break(msg: Message):
        await msg.reply("nb!")

# register command and add a rule
# invoke this via saying `/hello @{bot_name}` in channel
@bot.command(regex = r'/music\W+(.+)')
async def music(msg: Message, name: str):
    await msg.reply(f'点歌：{name}')

# register command and add a rule
# invoke this via saying `/hello @{bot_name}` in channel
@bot.command(regex = r'/ban\W+(.+)')
async def ban(msg: Message, name: str):
    await msg.reply(f'ban：{name}')

@bot.command(regex = r'(.+)', rules=[Rule.is_bot_mentioned(bot)])
async def chat(msg: Message, name: str):
    name=re.sub(r'\(met\)[0-9]+\(met\)','',name) # 删除@信息
    name = ' '.join(name.split()) # 多个空格合并
    if(name==''): # 若消息为空
        name = "我是你爹"
    else:
        name = get_chat(name)
    name = name.replace('{br}','\n')
    print(name.strip())
    await msg.reply(name.strip()) # 回复

@bot.command()
async def hso(msg: Message):
    image = get_hso()
    await msg.reply(image)


# @bot.task.add_cron(second=1)
# async def clocking():
#     print(datetime.now())

# everything done, go ahead now!
bot.run()