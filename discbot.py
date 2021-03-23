import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import requests
import time
import json


Keyfile = open("Key.txt")
Key = Keyfile.read()
MappingFile = open("allmappingitems.txt")
Thumbnailurl = 'https://secure.runescape.com/m=itemdb_oldschool/1615980608799_obj_big.gif?id='
PriceURL = 'https://prices.runescape.wiki/api/v1/osrs/latest?'
VolumeURL = 'https://prices.runescape.wiki/api/v1/osrs/volumes'
headers = {
    'User-Agent':'@Pseudechis#7807'
}
Prefix = ("!")
bot = commands.Bot(command_prefix=Prefix, description='flipping bot')
Mappeditems = json.load(MappingFile)
ItemJson = requests.get(PriceURL,json={'key':'value'},headers=headers)
itemprices= ItemJson.json()['data']
ItemVolJson = requests.get(VolumeURL,json={'key':'value'},headers=headers)
itemVolumes = ItemVolJson.json()['data']

@bot.event
async def on_ready():
    Activity = discord.Game(name ="Finding Flips")
    await bot.change_presence(activity = Activity)
    print("Bot is Running")
    bot.loop.create_task(getprices())
    bot.loop.create_task(getvolume())


async def getprices():
    while True:
        await asyncio.sleep(60)
        print("Updating Prices")
        ItemJson = requests.get(PriceURL,json={'key':'value'},headers=headers)
        global itemprices
        itemprices= ItemJson.json()['data']

async def getvolume():
    while True:
        await asyncio.sleep(86400)
        print("Updating Volumes")
        ItemVolJson = requests.get(VolumeURL,json={'key':'value'},headers=headers)
        global itemVolumes
        itemVolumes= ItemVolJson.json()['data']

@bot.command()
async def price(ctx,*,arg):
    ItemNameInput = arg.lower()
    if ItemNameInput == "tbow".lower():
        ItemNameInput = "Twisted Bow".lower()
    elif "Scythe".lower() in ItemNameInput:
        ItemNameInput = "Scythe of Vitur (Uncharged)".lower()
    elif "Blowpipe".lower() in ItemNameInput:
        ItemNameInput = "Toxic Blowpipe (empty)".lower()
    MapObj = next(filter((lambda m: m['name'].lower() == ItemNameInput), Mappeditems), None)
    ItemId = MapObj['id']
    ItemName = MapObj['name']
    ItemLimit = "Unknown"
    if (('limit' in MapObj.keys())):
        ItemLimit = MapObj['limit']
    strid = str(ItemId)
    ItemThumbnail = Thumbnailurl+strid
    Individual = itemprices.get(strid)
    ItemHigh = Individual.get('high')
    ItemLow = Individual.get('low')
    Margin = ItemHigh - ItemLow
    ROI = (Margin/ItemHigh)*100
    ItemVolume = itemVolumes.get(strid)
    embed=discord.Embed(title = ItemName, color = discord.Color.red())
    embed.add_field(name = "Buy Price", value = "{:,}".format(ItemLow), inline = True)
    embed.add_field(name = "Sell Price", value = "{:,}".format(ItemHigh), inline = True)
    embed.add_field(name = "Margin", value = "{:,}".format(Margin), inline = True)
    embed.add_field(name = "ROI", value = str(round(ROI,3))+"%", inline = True)
    if (('limit' in MapObj.keys())):
        embed.add_field(name = "Buy Limit", value = "{:,}".format(ItemLimit), inline = True)
    else:
        embed.add_field(name = "Buy Limit", value = ItemLimit, inline = True)
    embed.add_field(name = "Daily Volume", value = "{:,}".format(ItemVolume), inline = True)
    embed.set_thumbnail(url=ItemThumbnail)
    embed.set_footer(text="This price check is completed using the Real Time Pricing Data API Provided by the OSRS Wiki Team")
    await ctx.send(embed=embed)

bot.run(Key)
