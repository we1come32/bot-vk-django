from __future__ import unicode_literals
from django.shortcuts import render
import json
from django.conf import settings as DjangoSettings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .simple_function import *
from .standart_functions import *
import vk
from random import randint, choice
import time
import re


# import logging


@csrf_exempt
def index(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        # logging.getLogger(__name__)
        if (data['secret'] == DjangoSettings.SECRET_KEY) or (data['group_id'] == DjangoSettings.GROUP_ID):
            if (data['type'] == 'confirmation'):
                return HttpResponse(DjangoSettings.CONFIRMATION_TOKEN, content_type="text/plain", status=200)
            session = vk.Session(access_token=DjangoSettings.ACCESS_TOKEN)
            api = vk.API(session, v=DjangoSettings.VK_VERSION)
            if (data['type'] == 'message_new'):
                try:
                    start_time = time.time()
                    message = data['object']['message']
                    peer_id = message['peer_id']
                    user = message['from_id']
                    if peer_id > 2000000000:
                        peer_id = get_peer_id(peer_id)
                        user = get_user(user, peer_id, here=True)
                        action = message.get('action', False)
                        if type(user) == ChatUser:
                            length = len(message['text'])
                            words = len(re.findall(r'[a-zA-Zа-яА-Я]{1,}', message['text']))
                            msg = Message.objects.create(
                                author=user,
                                length=length,
                                words=words,
                                message=message['text'],
                                chat=peer_id
                            )
                            for attach in message['attachments']:
                                _type = attach['type']
                                if _type != 'call':
                                    att = Attachment.objects.create(
                                        mess=msg,
                                        data=_type
                                    )
                                    att.typeAttachment = _type
                                    owner_id = attach[_type].get('owner_id', '')
                                    if owner_id != "":
                                        att.typeAttachment += "{owner_id}".format(
                                            owner_id=owner_id
                                        )
                                    id = attach[_type].get('id', '')
                                    if id != "":
                                        att.typeAttachment += "{id}".format(
                                            id=id
                                        )
                                    sk = attach[_type].get('secret_key', '')
                                    if sk != "":
                                        att.typeAttachment += "_{sk}".format(
                                            sk=sk
                                        )
                                    att.save()
                                elif _type == 'call':
                                    att = Attachment.objects.create(
                                        mess=msg,
                                        data=_type
                                    )
                                    att.typeAttachment = _type
                                    sk = attach[_type].get('secret_key', '')
                                    if sk != "":
                                        att.typeAttachment += "_{sk}".format(
                                            sk=sk
                                        )
                                    att.save()
                        if action:
                            if action['type'] == "chat_invite_user":
                                invmess = peer_id.settings.inviteMessage
                                new_user = get_user(action['member_id'], peer_id, here=True)
                                if new_user.get_id() == DjangoSettings.GROUP_ID:
                                    message_send(
                                        api,
                                        peer_id.id,
                                        message="Привет!\nДля того чтобы я здесь начала свою работу, прошу выдать мне администратора и написать \"Рая обновить чат\". \nО моем функционале можно узнать по ссылке vk.com/wall....",
                                        keyboard={
                                            "one_time": False,
                                            "inline": True,
                                            'buttons': [
                                                [
                                                    {
                                                        "color": "positive",
                                                        'action': {
                                                            "type": "text",
                                                            "payload": "",
                                                            "label": "Обновить чат",
                                                        },
                                                    },
                                                ],
                                            ]
                                        },
                                    )
                                    peer_id.save()
                                elif not (user.equial(new_user)) and peer_id.worked:
                                    new_user.warns = 0
                                    new_user.kicked = False
                                    new_user.save()
                                    Actions.objects.create(
                                        action="{user1} invite {user2}".format(
                                            user1=user,
                                            user2=new_user,
                                        ),
                                        chat=peer_id
                                    )
                                    if type(new_user) == ChatBot:
                                        if new_user.bot.verifery:
                                            message_send(
                                                api,
                                                peer_id.id,
                                                message="Был добавлен новый бот {bot}. Я его знаю.\n"
                                                        "Выберите что надо сделать с ним.".format(
                                                    bot=new_user
                                                ),
                                                keyboard={
                                                    "one_time": False,
                                                    "inline": True,
                                                    'buttons': [
                                                        [{
                                                            "color": "negative",
                                                            'action': {
                                                                "type": "text",
                                                                "payload": "{\"group_id\": \"" + str(
                                                                    new_user.get_id()) + "\"}",
                                                                "label": "Исключить"
                                                            }
                                                        }]
                                                    ]
                                                }
                                            )
                                        else:
                                            message_send(
                                                api,
                                                peer_id.id,
                                                message="Был добавлен новый бот {bot}.\n"
                                                        "Выберите действие, которое будет применено к нему.".format(
                                                    bot=new_user
                                                ),
                                                keyboard={
                                                    "one_time": False,
                                                    "inline": True,
                                                    'buttons': [
                                                        [{
                                                            "color": "negative",
                                                            'action': {
                                                                "type": "text",
                                                                "payload": "{\"group_id\": \"" + str(
                                                                    new_user.get_id()) + "\"}",
                                                                "label": "Оставить"
                                                            }
                                                        },
                                                        {
                                                            "color": "positive",
                                                            'action': {
                                                                "type": "text",
                                                                "payload": "{\"group_id\": \"" + str(
                                                                    new_user.get_id()) + "\"}",
                                                                "label": "Исключить"
                                                            }
                                                        }]
                                                    ]
                                                }
                                            )
                                    elif invmess != "":
                                        new_user.kicked = False
                                        message_send(
                                            api,
                                            peer_id.id,
                                            message="{user}, {invmess}".format(
                                                user=new_user,
                                                invmess=invmess
                                            )
                                        )
                                elif peer_id.worked:
                                    new_user.kicked = False
                                    new_user.leaved = False
                                    if type(new_user) == ChatUser:
                                        message_send(
                                            api,
                                            peer_id.id,
                                            message="{user}, {invmess}\nНужно ли наказывать за добавление в беседу?".format(
                                                user=new_user,
                                                invmess=invmess
                                            ),
                                            keyboard={
                                                "one_time": False,
                                                "inline": True,
                                                'buttons': [
                                                    [{
                                                        "color": "negative",
                                                        'action': {
                                                            "type": "text",
                                                            "payload": "{\"kick_id\": \"" + str(
                                                                new_user.get_id()) + "\"}",
                                                            "label": "Исключить"
                                                        }
                                                    }]
                                                ]
                                            }
                                        )
                                    new_user.save()
                            elif action['type'] == "chat_kick_user":
                                new_user = get_user(action['member_id'], peer_id, here=True)
                                if new_user.get_id() == DjangoSettings.GROUP_ID and peer_id.worked:
                                    peer_id.worked = False
                                    peer_id.save()
                                elif not (user.equial(new_user)) and peer_id.worked:
                                    new_user.kicked = True
                                    new_user.warns = 0
                                    new_user.status = 0
                                    new_user.save()
                                elif type(new_user) != Bot and peer_id.worked:
                                    if new_user.status < peer_id.perms.unLeaveAutoKickAccess:
                                        api.messages.removeChatUser(chat_id=peer_id.id - 2000000000,
                                                                    user_id=new_user.get_id())
                                        new_user.kicked = True
                                        new_user.save()
                                    else:
                                        new_user.leaved = True
                                        new_user.status = 0
                                        new_user.save()
                                        message_send(
                                            api,
                                            peer_id.id,
                                            message="Пользователь {user} вышел из беседы.\nВыберите действие, которое надо с ним сделать".format(
                                                user=new_user
                                            ),
                                            keyboard={
                                                "one_time": False,
                                                "inline": True,
                                                'buttons': [
                                                    [{
                                                        "color": "negative",
                                                        'action': {
                                                            "type": "text",
                                                            "payload": "{\"kick_id\": \"" + str(
                                                                new_user.get_id()) + "\"}",
                                                            "label": "Исключить"
                                                        }
                                                    }]
                                                ]
                                            }
                                        )
                                elif type(new_user) == Bot and peer_id.worked:
                                    new_user.status = 0
                                    new_user.save()
                            elif action['type'] == "chat_invite_user_by_link":
                                Actions.objects.create(
                                    action="{user} invite by link".format(
                                        user=user
                                    ),
                                    chat=peer_id
                                )
                                invmess = peer_id.settings.inviteMessage
                                if invmess != "":
                                    message_send(
                                        api,
                                        peer_id.id,
                                        message="{user}, {invmess}".format(
                                            user=user,
                                            invmess=invmess
                                        )
                                    )
                            else:
                                message_send(
                                    api,
                                    DjangoSettings.LOG_CHAT,
                                    message="У нас новый тип \"action\": {action}\n\nJSON:\n{json}".format(
                                        action=action['type'],
                                        json=message
                                    )
                                )
                        reply_message = message.get('reply_message', False)
                        forward_messages = message.get('fwd_messages', [])
                        payload = message.get('payload', '')
                        if re.fullmatch(
                                r"^([Рр][Аа][Яя]|\[club167676095\|[[a-zA-Z0-9 а-яА-Я@*]{1,}\])$",
                                message['text']):
                            a = message_send(
                                api,
                                peer_id.id,
                                sticker_id=choice(
                                    [19412, 163, 15250, 15259, 15252, 19425, 11238, 11244, 11246, 11257, 11269, 11277,
                                     12319, 19419, 19418, 19431, 19431, 18463, 4290, 14092, 14124]),
                            )
                            return HttpResponse('ok', content_type="text/plain", status=200)
                        cmd = checkMessage(user, peer_id, message['text'])
                        if cmd['flag']:
                            result = findCommand(
                                user,
                                peer_id,
                                cmd['command'],
                                cmd['args'],
                                fwd_messages=forward_messages,
                                reply_message=reply_message,
                                message_id=message['id'],
                                payload=payload
                            )
                            for tmp in result['types']:
                                if tmp == "message":
                                    if type(result['message']) == dict:
                                        result['message'] = [result['message']]
                                    for message in result['message']:
                                        mess = message.get("text", "") + "\n\nTime: {time}cек.".format(
                                            time=time.time() - start_time,
                                        )
                                        chat = message.get("peer_id", peer_id.id)
                                        keyboard = message.get("keyboard", "")
                                        try:
                                            message_send(
                                                api,
                                                chat,
                                                message=mess,
                                                attachments=message.get("attachments", ""),
                                                disable_mentions=message.get("disable_mentions", True),
                                                keyboard=keyboard
                                                # reply_to=result['message'].get("reply_message",""),
                                            )
                                        except:
                                            if chat != peer_id.id:
                                                message_send(
                                                    api,
                                                    peer_id.id,
                                                    message="{user}, я вам не могу отправить эту информацию приватно. Напишите мне в личные сообщения хотя бы одно сообщение, тогда смогу)".format(
                                                        user=user
                                                    ),
                                                    attachments=message.get("attachments", ""),
                                                    disable_mentions=message.get("disable_mentions", True),
                                                    keyboard=keyboard
                                                    # reply_to=result['message'].get("reply_message",""),
                                                )
                                                break
                                elif tmp == "kick_user":
                                    try:
                                        users = result['kick_user']
                                        if len(users) > 0:
                                            chat_info = api.messages.getConversationMembers(peer_id=peer_id.id)
                                            chat_users = chat_info['items']
                                            kicked_users = []
                                            c = 0
                                            message = "Исключены: "
                                            code = []
                                            for _user in users:
                                                for chat_user in chat_users:
                                                    if (chat_user.get('member_id') == _user.get_id()):
                                                        if chat_user.get('can_kick', False):
                                                            _user.kicked = True
                                                            _user.status = 0
                                                            _user.save()
                                                            if type(_user) == ChatUser:
                                                                code += [
                                                                    "API.messages.removeChatUser({\"chat_id\": " + str(
                                                                        peer_id.id - 2000000000) + ", 'member_id': " + str(
                                                                        _user.get_id()) + "});\n"]
                                                            else:
                                                                code += [
                                                                    "API.messages.removeChatUser({\"chat_id\": " + str(
                                                                        peer_id.id - 2000000000) + ", 'member_id': -" + str(
                                                                        _user.get_id()) + "});\n"]
                                                            c += 1
                                                            message += str(_user) + ", "
                                            if c == 0:
                                                message = "Пользователи не исключены"
                                            else:
                                                message = message[:-2]
                                            message_send(
                                                api,
                                                peer_id.id,
                                                message=message
                                            )
                                            max_count = 24
                                            if c != 0:
                                                for _ in range(c // max_count + int(c % max_count > 0)):
                                                    __ = "".join(_ for _ in code[_ * max_count:min(c, (
                                                                _ + 1) * max_count)]) + "return 1;"
                                                    api.execute(code=__)
                                    except Exception as e:
                                        message = "{profile}, извините, я не являюсь администратором в этой беседе".\
                                            format(profile=user)
                                        message = fixError(e)
                                        message_send(
                                            api,
                                            peer_id=peer_id.id,
                                            message=message
                                        )
                        else:
                            exp = min(
                                len(
                                    re.findall(r"[a-zA-Zа-яА-Я]",
                                               message['text']
                                               )
                                ),
                                user.rest_exp()
                            )
                            user.add_exp(exp)
                    elif peer_id < 2000000000:
                        message_send(
                            api,
                            peer_id,
                            message="Извините, бот работает только в беседах."
                        )
                # """
                except Exception as e:
                    message_send(
                        api,
                        DjangoSettings.LOG_CHAT,
                        message="Илья, ты где блять ходишь? У нас АШИБКА: \n\n{error_description} \n\n{json}".format(
                            error_description=fixError(e),
                            json=data,
                        )
                    )
                # """
                return HttpResponse('ok', content_type="text/plain", status=200)
            else:
                session = vk.Session()
                api = vk.API(session, v=DjangoSettings.VK_VERSION)
                message_send(
                    api,
                    DjangoSettings.ADMIN_ID,
                    message="Илья, кароче, новый нипаддерживаемый абъект \n\n{json}".format(
                        json=data,
                    )
                )
            return HttpResponse('ok', content_type="text/plain", status=200)
    else:
        return HttpResponse('see you :)')
