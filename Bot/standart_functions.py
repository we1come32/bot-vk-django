from .models import *
from random import randint
from copy import copy
from .simple_function import *
from . import functions
from django.conf import settings as DjangoSettings
import json
import vk

# Function to send message
def message_send(api, peer_id, message="", attachments="", keyboard="", reply_to="",forward_messages="", disable_mentions=True, sticker_id=""):
    if keyboard != "":
        keyboard = json.dumps(keyboard)
    if (message != "") or (attachments != "") or (sticker_id != ""):
        data = {
            'v': DjangoSettings.VK_VERSION,
            'random_id': randint(0, 9999), 
            'peer_id': peer_id, 
            'message': message, 
            'keyboard': keyboard,
            'disable_mentions': disable_mentions,
        }
        if forward_messages != "":
            data['fwd_messages'] = forward_messages
        if reply_to != "":
            data['reply_to'] = reply_to
        if sticker_id != "":
            data['sticker_id'] = sticker_id
        return api.messages.send(**data)
        #api.messages.send(v=DjangoSettings.VK_VERSION,access_token = DjangoSettings.ACCESS_TOKEN, random_id = randint(0, 9999), peer_id = DjangoSettings.LOG_USER_ID, message = result)

def checkMessage(user, peer_id, message):
    import re
    commands = [
        ("скажи",               r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][кК][аА][жЖ][иИ]([\S ]{0,})$',),
        ("помощь",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[пП][оО][мМ][оО][щЩ][ьЬ]([\S ]{0,})$',),
        ("помощь",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[кК][оО][мМ][аА][нН][дД][ыЫ]([\S ]{0,})$',),
        ("профиль",             r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[пП][рР][оО][фФ][иИ][лЛ][ьЬ]([\S ]{0,})$',),
        ("исключить",           r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[иИ][сС][кК][лЛ][юЮ][чЧ][иИ][тТ][ьЬ]([\S ]{0,})$',),
        ("кто",                 r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[кК][тТ][оО]([\S ]{0,})$',),
        ("кик",                 r'^[кК][иИ][кК]$',),
        ("кик",                 r'^[кК][иИ][кК] ([\S ]{0,})$',),
        ("кик",                 r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[кК][иИ][кК]([\S ]{0,})$',),
        ("преды",               r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[пП][рР][еЕ][дД][ыЫ]([\S ]{0,})$',),
        ("анпред",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] |)[аА][нН][пП][рР][еЕ][дД]([\S ]{0,})$',),
        ("анпред",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][нН][яЯ][тТ][ьЬ] [пП][рР][еЕ][дД]([\S ]{0,})$',),
        ("пред",                r'^[пП][рР][еЕ][дД]$',),
        ("пред",                r'^[пП][рР][еЕ][дД] ([\S ]{0,})$',),
        ("пред",                r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[пП][рР][еЕ][дД]([\S ]{0,})$',),
        ("статусы",             r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][тТ][аА][тТ][уУ][сС][ыЫ]([\S ]{0,})$',),
        ("статус установить",   r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][тТ][аА][тТ][уУ][сС] [уУ][сС][тТ][аА][нН][оО][вВ][иИ][тТ][ьЬ]([\S ]{0,})$',),
        ("статус",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][тТ][аА][тТ][уУ][сС]([\S ]{0,})$',),
        ("доступы",             r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[дД][оО][сС][тТ][уУ][пП][ыЫ]([\S ]{0,})$',),
        ("доступ",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[дД][оО][сС][тТ][уУ][пП]([\S ]{0,})$',),
        ("стат",                r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][тТ][аА][тТ][аА]([\S ]{0,})$',),
        ("стат",                r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[сС][тТ][аА][тТ]([\S ]{0,})$',),
        ("инфа",                r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[иИ][нН][фФ][аА]([\S ]{0,})$',),
        ("автосписок",          r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[аА][вВ][тТ][оО][сС][пП][иИ][сС][оО][кК]([\S ]{0,})[дД][еЕ][иИйЙ][сС][тТ][вВ][иИ][еЕ]([\S ]{0,})$',),
        ("автосписок",          r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[аА][вВ][тТ][оО][сС][пП][иИ][сС][оО][кК]([\S ]{0,})$',),
        ("автосписки",          r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[аА][вВ][тТ][оО][сС][пП][иИ][сС][кК][иИ]([\S ]{0,})$',),
        ("топ",                 r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[тТ][оО][пП]([\S ]{0,})$',),
        ("онлайн",              r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[оО][нН][лЛ][аА][иИйЙ][нН]([\S ]{0,})$',),
        ("приветствие удалить", r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[пП][рР][Ии][Вв][Ее][Тт][Сс][Тт][Вв][Ии][Ее] [Уу][Дд][Аа][Лл][Ии][Тт][Ьь]([\S ]{0,})$',),
        ("приветствие",         r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[пП][рР][Ии][Вв][Ее][Тт][Сс][Тт][Вв][Ии][Ее]([\S ]{0,})$',),
        ("номер беседы",        r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[нН][оО][мМ][еЕ][рР] [бБ][еЕ][сС][еЕ][дД][ыЫ]([\S ]{0,})$',),
        ("игнор",               r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[иИ][гГ][нН][оО][рР]([\S ]{0,})$',),
        ("никнейм",             r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[нН][иИ][кК][нН][еЕ][иИйЙ][мМ]([\S ]{0,})$',),
        ("обновить чат",        r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[оО][бБ][нН][оО][вВ][иИ][тТ][ьЬ] [чЧ][аА][тТ]([\S ]{0,})$',),
        ("браки",               r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[бБ][рР][аА][кК][иИ]([\S ]{0,})$',),
        ("брак",                r'^(! |!|[Рр][Аа][Яя][,]{0,1} |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[бБ][рР][аА][кК]([\S ]{0,})$',),
        ("баланс",              r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[бБ][аА][лЛ][аА][нН][сС]([\S ]{0,})$',),
        ("купить",              r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[кК][уУ][пП][иИ][тТ][ьЬ]([\S ]{0,})$',),
        ("инвентарь",           r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[иИ][нН][вВ][еЕ][нН][тТ][аА][рР][ьЬ]([\S ]{0,})$',),
        ("использовать",        r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[иИ][сС][пП][оО][лЛ][ьЬ][зЗ][оО][вВ][аА][тТ][ьЬ]([\S ]{0,})$',),
        ("магазин",             r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[мМ][аА][гГ][аА][зЗ][иИ][нН]([\S ]{0,})$',),
        ("настройки установить",r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[нН][аА][сС][тТ][рР][оО][йЙиИ][кК][иИ] [уУ][сС][тТ][аА][нН][оО][вВ][иИ][тТ][ьЬ]([\S ]{0,})$',),
        ("настройки",           r'^(! |!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] )[нН][аА][сС][тТ][рР][оО][йЙиИ][кК][иИ]([\S ]{0,})$',),
        ("бот_стат",            r'^[бБ][оО][тТ] [сС][тТ][аА][тТ]([\S ]{0,})$',),
        ("бот_список",          r'^[бБ][оО][тТ] [сС][пП][иИ][сС][оО][кК]([\S ]{0,})$',),
        #    ("", r'^(!|[Рр][Аа][Яя] |\[club167676095\|[a-zA-Z0-9 а-яА-Я@*]{1,}\] ) ([\S ]{0,})$',),
    ]
    try:
        accepted = []
        values = {}
        count = 0
        session = vk.Session(access_token=DjangoSettings.ACCESS_TOKEN)
        api = vk.API(session, v=DjangoSettings.VK_VERSION)
        return_message = ""
        for number, command in enumerate(commands):
            match = re.fullmatch(command[1], message)
            if match:
                accepted.append(number)
                values[number] = match.groups()
                count += 1
            return_message += "{result} {command} {text}\n".format(
                result=match,
                command=command[1],
                text=message
            )
        if count > 0:
            return {
                'flag': True,
                'command': commands[accepted[0]][0],
                'args': values[accepted[0]]
            }
        else:
            return {
                'flag': False
            }
    except Exception as e:
        return {
            'flag': True,
            'command': "ERROR BLYAD",
            'args': fixError(e)
        }

def findCommand(user, peer_id, command, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if command == "помощь":
        return functions.help(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    #elif command == "скажи":
    #    return functions.say(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "статусы":
        return functions.statuses(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "статус":
        return functions.status(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "приветствие":
        return functions.getInviteMessage(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "приветствие удалить":
        return functions.delInviteMessage(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "доступ":
        return functions.setPermsChat(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "доступы":
        return functions.getListPerms(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "статус установить":
        return functions.setStatus(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "никнейм":
        return functions.Nickname(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "обновить чат":
        return functions.UpdateChat(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "кик":
        return functions.kickChat(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "пред":
        return functions.warnChat(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "анпред":
        return functions.unWarnChat(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "профиль":
        return functions.profile(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "преды":
        return functions.predList(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "топ":
        return functions.top(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "кто":
        return functions.who(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "номер беседы":
        return functions.peer_id_number(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "исключить":
        return functions.kickSpecial(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "бот_стат":
        return functions.getStatisticBot(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif command == "бот_список":
        return functions.getBotList(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif (command == "баланс") and user.user.tester:
        return functions.get_balance(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif (command == "магазин") and user.user.tester:
        return functions.shop(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif (command == "купить") and user.user.tester:
        return functions.buy(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif (command == "инвентарь") and user.user.tester:
        return functions.inventory(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif (command == "использовать") and user.user.tester:
        return functions.use(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    elif (command == "настройки") and user.user.tester:
        return functions.getChatSettings(user, peer_id, args, reply_message=reply_message, fwd_messages=fwd_messages, message_id=message_id, payload=payload)
    else:
        return {
            "types": ["message"],
            "message": {
                "text": "Команда \"{cmd}\" пока что ещё не доступна".format(
                    cmd=command
                ),
            }
        }


