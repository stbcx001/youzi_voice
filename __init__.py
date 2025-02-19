from hoshino import Service, priv
from nonebot import MessageSegment
from .create_img import image_draw
from .youdaotranslate import translate
from .getvoiece import voiceApi, GenshinAPI, XcwAPI, Error, chinese2katakana, getvoice
from PIL import Image, ImageDraw, ImageFont
import os
sv_help = '''
【柚子/常轨脱离/缘之空/美少女万华镜/galgame】【中配/日配】+ （角色id） + 文本
（中配将中文翻译为片假名，日配翻译为日语，日配会输出翻译内容供检查）
不填默id认为0，加号替换为空格
例：柚子日配 0 我爱宁宁 
柚子中配 我爱宁宁 
柚子日配 私は綾地寧々を愛している（应该是这样，日语不好）
特殊：
xcw日配+日语/中文（自动翻译）
xcw中配+中文
派蒙说中文+中文（更新到鹿野院平藏）
【角色id列表】查看支持角色和分类
'''.strip()

speaker_dict = {
    '柚子': ["綾地寧々", "因幡めぐる", "朝武芳乃", "常陸茉子", "ムラサメ", "鞍馬小春", "在原七海", "四季ナツメ", "明月栞那", "墨染希", "火打谷愛衣", "汐山涼音"],
    '常轨脱离': ["和泉妃愛", "常盤華乃", "錦あすみ", "鎌倉詩桜", "竜閑天梨", "和泉里", "新川広夢", "聖莉々子"],
    '缘之空': ["春日野穹", "天女目瑛", "依媛奈緒", "渚一葉"],
    '美少女万華鏡': ["蓮華", "篝ノ霧枝", "沢渡雫", "亜璃子", "灯露椎", "覡夕莉"],
    'galgame': ["鷹倉杏璃", "鷹倉杏鈴", "アペイリア", "倉科明日香", "ATRI", "アイラ", "新堂彩音", "姫野星奏", "小鞠ゆい", "聖代橋氷織", "有坂真白", "白咲美絵瑠", "二階堂真紅"]
}

XCW = ['xcw', '小仓唯', '镜华']

genshin = ['派蒙', '凯亚', '安柏', '丽莎', '琴', '香菱', '枫原万叶', '迪卢克', '温迪', '可莉', '早柚', '托马', '芭芭拉',
           '优菈', '云堇', '钟离', '魈', '凝光', '雷电将军', '北斗', '甘雨', '七七', '刻晴', '神里绫华', '雷泽', '神里绫人',
           '罗莎莉亚', '阿贝多', '八重神子', '宵宫', '荒泷一斗', '九条裟罗', '夜兰', '珊瑚宫心海', '五郎', '达达利亚', '莫娜',
           '班尼特', '申鹤', '行秋', '烟绯', '久岐忍', '辛焱', '砂糖', '胡桃', '重云', '菲谢尔', '诺艾尔', '迪奥娜', '鹿野院平藏']

speaker_id = '''
类别:==柚子===========常轨脱离=======缘之空=========
id: 0： 绫地宁宁   |0：和泉妃爱   |0：春日野穹     
    1： 因幡爱瑠   |1：常磐华乃   |1：天女目瑛    
    2： 朝武芳乃   |2：锦亚澄     |2：依媛奈绪    
    3： 常陸茉子   |3：镰仓诗樱   |3：渚一叶       
    4： 丛雨       |4：龙闲天梨   |               
    5： 鞍马小春   |5：和泉里     |== 美少女万華鏡==
    6： 在原七海   |6：新川广梦   |0：莲华         
    7： 四季夏目   |7：圣莉莉子   |1：篝之雾枝    
    8： 明月栞那   |              |2：沢渡雫       
    9： 墨染希     |              |3：亚璃子      
    10：火打谷爱衣 |              |4：灯露椎       
    11：汐山凉音   |              |5：覡夕莉      
类别:==galgame====================================            
id: 0： 鹰仓杏璃   《Clover Day's》
    1： 鹰仓杏铃   《Clover Day's》
    2： 艾佩莉娅   《景之海的艾佩莉娅》
    3： 仓科明日香 《苍之彼方的四重奏》
    4： ATRI       《ATRI》 
    5： 艾拉       《可塑性记忆》 
    6： 新堂彩音   《想要传达给你的爱恋》
    7： 姫野星奏   《想要传达给你的爱恋》
    8： 小鞠由依   《想要传达给你的爱恋》
    9： 圣代桥冰织 《糖调！-sugarfull tempering-》
    10：有坂真白   《苍之彼方的四重奏》
    11：白咲美绘瑠 《与你相恋的恋爱Recette》
    12：二阶堂真红 《五彩斑斓的世界》
'''.strip()


def get_speakers(choose, num=0):
    if choose == '常轨脱离':
        speakers, model = speaker_dict["常轨脱离"][num], 5
    elif choose == '缘之空':
        speakers, model = speaker_dict["缘之空"][num], 13
    elif choose == '美少女万華鏡':
        speakers, model = speaker_dict["美少女万華鏡"][num], 17
    elif choose == "galgame":
        speakers, model = speaker_dict["galgame"][num], 29
    else:
        speakers = speaker_dict["柚子"][num]
        if num >= 7:
            model = 9
        else:
            model = 1
    return speakers, model


sv = Service(
    name='角色语音模仿',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    help_=sv_help
)


@sv.on_prefix([i + '中配' for i in speaker_dict.keys()])
async def youzi_voice_cn(bot, ev):
    text = ev.raw_message
    content = text.split()
    category=content[0].split('中配')
    if category[1]!='':
       content=[category[0]+'中配',category[1],content[-1]]
    if len(content) == 2:
        speaker, model = get_speakers(content[0][:-2])
        text_chjp = await chinese2katakana(content[1])
        A = getvoice(speaker, model)
    elif content[1].isdigit():
        speaker, model = get_speakers(content[0][:-2], int(content[1]))
        text_chjp = await chinese2katakana(content[2])
        A = getvoice(speaker, model)
    else:
        await bot.send(ev, sv_help)
        return
    try:
        voice = await A.gethash(text_chjp)
        final_send = MessageSegment.record(voice)
        await bot.send(ev, final_send)
    except:
        await bot.send(ev, "生成失败，红豆泥斯密马赛~")


@sv.on_prefix([i + '日配' for i in speaker_dict.keys()])
async def youzi_voice_ja(bot, ev):
    text = ev.raw_message
    content = text.split()
    category=content[0].split('日配')
    if category[1]!='':
       content=[category[0]+'日配',category[1],content[-1]]
    if len(content) == 2:
        speaker, model = get_speakers(content[0][:-2])
        text_chjp = await translate(content[1])
        A = getvoice(speaker, model)
    elif content[1].isdigit():
        speaker, model = get_speakers(content[0][:-2], int(content[1]))
        text_chjp = await translate(content[2])
        A = getvoice(speaker, model)
    else:
        await bot.send(ev, sv_help)
        return
    await bot.send(ev, text_chjp)
    try:
        voice = await A.gethash(text_chjp)
        final_send = MessageSegment.record(voice)
        await bot.send(ev, final_send)
    except:
        await bot.send(ev, "生成失败，红豆泥斯密马赛~")

@sv.on_prefix(['#'+i + '日配' for i in XCW])
@sv.on_prefix(['#'+i + '中配' for i in genshin])
@sv.on_prefix(['#'+i + '中配' for i in XCW])
async def voice(bot, ev):
    try:
        text: str = ev.message.extract_plain_text().strip()
        if not text:
            await bot.send(ev, '请输入需要合成语音的文本', at_sender=True)
            return
        preid: str = ev.prefix[1:-2]
        prelang: str = ev.prefix[-2:]
        if prelang == '中配':
            if preid in XCW:
                text = await chinese2katakana(text)
                voice = await voiceApi(XcwAPI + text)
            else:
                text = replace_text(text)
                voice = await voiceApi(GenshinAPI, {'speaker': preid, 'text': text, 'length': 1.0})
        else:
            text = await translate(text)
            voice = await voiceApi(XcwAPI + text)
        data = MessageSegment.record(voice)
    except Error as e:
        data = f'发生错误：{e.error}'
        sv.logger.error(data)
    except Exception as e:
        data = f'发生错误：{e}'
        sv.logger.error(data)
    await bot.send(ev, data)


@sv.on_fullmatch("角色id列表")
async def speaker_list(bot, ev):
    img = image_draw(speaker_id)
    await bot.send(ev, f'[CQ:image,file={img}]')

   
@sv.on_rex(r'^(语音|配音)(帮助)?$')
async def voicehelp(bot, ev):
    image = Image.open(os.path.join(os.path.dirname(__file__),f"help.jpg"))
    draw= ImageDraw.Draw(image) #建立一个绘图的对象
    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__),f"SIMYOU.ttf"), 40)
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__),f"SIMYOU.ttf"), 30)
    text1=speaker_id                     
    text=''
    textcn=''
    textxcw='[小仓唯/镜华]指令:#小仓唯[中配/日配] + 文本,如#小仓唯日配 你好'
    text2='以下角色无需填写类别,指令#[名字][中配(无日配)] + 文本,如#派蒙中配 你好'
    for prime in genshin:
        text3=text
        text+=prime+" " 
        if len(text)>30:
           if len(text)<33:
              textcn+=text+'\n'
              text=''
           else:
              textcn+=text3+'\n'
              text=''
              text+=prime+" "
    textcn+=text+'\n'    
    draw.text((84,827), text1, font=font, fill="#2e59a7") 
    draw.text((84,2080), textxcw, font=font2, fill="#531dab")
    draw.text((84,2120), text2, font=font2, fill="#531dab")
    draw.text((84,2160), textcn, font=font, fill="#2e59a7") 
    image.save(os.path.join(os.path.dirname(__file__),f"help2.jpg"))
    help2=os.path.join(os.path.dirname(__file__),f"help2.jpg")
    await bot.send(ev, MessageSegment.image(f'file:///{help2}'))


Genshin_list = (
    (',', '，'), ('.', '。'), ('!', '！'), ('?', '？'),(':', '：'),('(', '（'),('<', '《'),('>', '》'), ('0', '零'), ('1', '一'), ('2', '二'), ('3', '三'), ('4', '四'),
    ('5', '五'), ('6', '六'), ('7', '七'), ('8', '八'), ('9', '九'),)

def replace_text(text):
    for en, cn in Genshin_list:
        text = text.replace(en, cn)
    print(text)
    return text
