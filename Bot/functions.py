import re
from .simple_function import *
from .models import *
from django.conf import settings as DjangoSettings
from django.db.models import Q
import vk
import locale
from datetime import datetime, timedelta, time
from django.db.models import Sum, Count
from random import randint, choice
import json
from django.utils import timezone


def get_type_of_media_object(name):
    if name == "photo":
        name = "&#128248; Фотография"
    elif name == "audio_message":
        name = "&#127908; Аудиосообщения"
    elif name == "video":
        name = "&#127916; Видеозапись"
    elif name == "audio":
        name = "&#127925; Аудиозапись"
    elif name == "doc":
        name = "&#128196; Документ"
    elif name == "graffiti":
        name = "&#127912; Граффити"
    elif name == "story":
        name = "&#128250; История"
    elif name == "link":
        name = "&#128206; Ссылка"
    elif name == "call":
        name = "&#128222; Звонок"
    elif name == "sticker":
        name = "&#129313; Стикер"
    elif name == "poll":
        name = "&#10067; Опрос"
    elif name == "wall_reply":
        name = "&#128172; Комментарий к записи"
    elif name == "wall":
        name = "&#128221; Запись"
    return name


def help(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    return {
        'types': ['message'],
        'message': 
        {
            "text": (
                "Для просмотра списка команд, достаточно написать \"Рая помощь\".\n" #+
                "К любой из этих команд надо добавлять обращение \"Рая\"\n\n"
                "Доступные/основные команды:\n"
                "• Статус [Имя и фамилия пользователя] [Статус] - статус пользователя\n"
                "• Стат [пользователь] [дни] - статистика пользователя\n"
                "• Кик - исключение пользователя из беседы\n"
                "• Пред - предупреждение пользователю\n"
                "• Преды - список пользователей беседы с предупреждениями\n"
                "• Топ [дни] - топ беседы по символам\n"
                "• Доступы - список доступов с возможностью настройки\n"
                "• Доступ - просмотр разрешений пользователю\n"
                "• Онлайн - список пользователей онлайн\n"
                "• Приветствие [текст] - установление приветствия\n"
                "• Приветствие удалить - удаление приветствия\n"
                "• Приветствие - просмотр приветствия\n"
                "• Автосписок [список] [действие] - выполнение действия для автосписка\n"
                "• Автосписки - список возможных автосписков\n"
                "• Игнор [пользователь] - игнорирование пользователя\n"
                "• Отменить игнор [пользователь] - отмена игнорирования пользователя\n"
                "• Номер беседы - номер этой беседы\n"
                "• Инфа [событие] - вероятность события\n"
                "• Скажи [фраза] - я скажу фразу, которую ты напишешь:)\n"
                "• Никнейм [никнейм] - я буду обращаться к тебе по этому никнейму\n"
            ),
        }
    }


def say(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "sayAccess")
    if tmp['flag']:
        if len(args[1])>0:
            return {
                'types': [
                    'message',
                ],
                'message': {
                    'text': args[1],
                }
            }
        return {
            'types': [
                'message',
            ],
            'message': {
                'text': "Вы не отправили текст(",
            }
        }
    else:
        message = "{profile}, у вас нет доступа отправлять сообщения от моего имени ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )


def statuses(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "getListStatusAccess")
    if tmp['flag']:
        message = "{profile}, статусы пользователей в беседе\n".format(
            profile=user
        )
        try:
            users = peer_id.users.filter(leaved=False, kicked=False).order_by('-status')
            if True:
                count = 0
                for _user in users:
                    status = _user.getStatus()
                    if status > 0:
                        count += 1
                        message += "\n{name} - {status}".format(
                            name=_user,
                            status=status
                        )
                if count == 0:
                    message = "{profile}, пользоватлей со статусом больше 0 в беседе нет".format(
                        profile=user
                    )
            else:
                message = str(users)
        except Exception as e:
            return {
                "types": [
                    'message',
                ],
                'message': [
                    {
                        'text': "{profile}, извините, произошла неизвестная ошибка. Попробуйте позже".format(
                            profile=user
                        ),
                        'reply_message': message_id,
                    },
                    {
                        'text': fixError(e),
                        'peer_id': DjangoSettings.LOG_CHAT
                    },
                ]
            }
    else:
        message = "{profile}, у вас нет доступа для просмотра статусов беседы ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        'types': [
            'message',
        ],
        'message': {
            'text': message
        }
    }


def status(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if args[1] == "":
        message = "[id{id}|Ваш] статус: {status}".format(
            id=user.get_id(),
            status=user.getStatus()
        )
    else:
        tmp = checkAccess(user, peer_id, "getListStatusAccess")
        if tmp['flag']:
            match = re.findall(r'\[id([0-9]{1,})\|[a-zA-Z0-9а-яА-Я @*._]{1,}\]', args[1])
            if match:
                message = "{profile}, статусы запрашиваемых пользователей:".format(
                    profile=user
                )
                selected = {}
                for one in match:
                    if selected.get(one, True):
                        selected[one] = False
                        checked_user = get_user(int(one), peer_id)
                        message += "\n{name} - {status}".format(
                            name = checked_user,
                            status = checked_user.getStatus(),
                        )
            else:
                message = "{profile}, мы не нашли в вашем запросе упоминаний пользователей".format(
                    profile=user
                )
        else:
            message = "{profile}, у вас нет доступа для просмотра чужого статуса ({user}<{chat})".format(
                user=tmp['user'],
                chat=tmp['chat'],
                profile=user
            )
    return {
            'types': [
                'message', 
            ],
            'message': {
                'text': message,
            }
        }


def getInviteMessage(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if len(args[1]) == 0:
        tmp = peer_id.settings.inviteMessage
        if tmp == "":
            message = "{profile}, Приветствие не установлено".format(
                    profile=user
                )
        else:
            message = "{profile}, приветствие: \n\n".format(
                    profile=user
                ) + tmp
    else:
        tmp = checkAccess(user, peer_id, "changeInviteMessageAccess")
        if tmp['flag']:
            peer_id.settings.inviteMessage = args[1][1:]
            peer_id.settings.save()
            message = "{profile}, приветствие установлено. Новое приветствие: \n\n".format(
                    profile=user
                ) + peer_id.settings.inviteMessage
        else:
            message = "{profile}, у вас нет доступа для изменения приветствия ({user}<{chat})".format(
                user=tmp['user'],
                chat=tmp['chat'],
                profile=user
            )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def delInviteMessage(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "changeInviteMessageAccess")
    if tmp['flag']:
        peer_id.settings.inviteMessage = ""
        peer_id.settings.save()
        message = "{profile}, приветствие удалено".format(
            profile=user
        )
    else:
        message = "{profile}, у вас нет доступа для удаления приветствия беседы ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
            "types": [
                'message'
            ],
            'message': {
                'text': message,
                'reply_message': message_id
            }
        }


def setPermsChat(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "setPermsAccess")
    if tmp['flag']:
        perms = peer_id.perms
        args = args[1].split()
        l_args = len(args)
        try:
            args = list(map(int, args))
            if l_args == 2:
                key = perms.getAccessById(args[0])
                if key['flag']:
                    message = "{profile}, у вас нет права менять данный доступ.".format(profile=user)
                    key = key['key']
                    tmp = perms.getAccess(key)
                    if user.getStatus() >= tmp and user.getStatus()>=args[1]:
                        if type(tmp) == int:
                            tmp = args[1]
                            if (tmp >= 0) and (tmp <= 10):
                                perms.setAccess(key, tmp)
                                perms.save()
                                message = "{profile}, доступ №{number} изменен.\n\n{number}) {description} - {status}".format(
                                    number=args[0],
                                    description=perms.getAccesses()[key],
                                    status=tmp,
                                    profile=user
                                )
                            else:
                                message = "Ошибка установки доступа".format(profile=user)
                        else:
                            message = "Ошибка установки доступа".format(profile=user)
                else:
                    message = "{profile}, запрашиваемый доступ №{number} не найден".format(
                        number=args[0],
                        profile=user
                    )
            elif l_args == 1:
                key = perms.getAccessById(args[0])
                if key['flag']:
                    message = "{profile}, запрашиваемый доступ №{number}:\n\n{number}) {description} - {status}".format(
                        number=args[0],
                        description=perms.getAccesses()[key['key']],
                        status=perms.getAccess(key['key']),
                        profile=user
                    )
                else:
                    message = "{profile}, запрашиваемый доступ №{number}: \n\nДоступ не найден".format(
                        number=args[0],
                        profile=user
                    )
            else:
                message = "{profile}, неверное использование команды.\nОбратитесь за помощью на страницу помощи (Рая помощь) или в личные сообщения мне.".format(profile=user)
        except Exception as e:
            message = "{profile}, неверное использование команды.\nОбратитесь за помощью на страницу помощи (Рая помощь) или в личные сообщения мне.".format(profile=user)
    else:
        message = "{profile}, у вас нет доступа менять доступы ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def getListPerms(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "getPermsAccess")
    if tmp['flag']:
        perms = peer_id.perms
        Accesses = perms.getAccesses()
        message = "{profile}, список доступов и их значения в этой беседе:\n\n".format(profile=user)
        for number, key in enumerate(Accesses.keys()):
            message += "{number:3} {description} - {value}\n".format(
                number=str(number+1) + ")",
                description=Accesses[key],
                value=perms.getAccess(key)
            )
        _tmp = checkAccess(user, peer_id, "setPermsAccess")
        if _tmp['flag']:
            message += "\n\nДля изменения доступа используйте команду \"Рая доступ [номер_доступа] [необходимый статус]\""
    else:
        message = "{profile}, у вас нет доступа для просмотра списка доступов ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def setStatus(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "setStatusAccess")
    if tmp['flag']:
        import re
        pattern = r'\[id([0-9]{1,})\|[A-Za-zа-яА-Я0-9 @*._]{1,}\] ([0-9]{1,})'
        data = re.findall(pattern, args[1])
        message = "{profile}, измененые статусы:\n\n".format(profile=user)
        changed = []
        for elem in data:
            _user = get_user(int(elem[0]), peer_id)
            if type(_user) != Bot:
                if _user.user.id not in changed:
                    a = user.getStatus()
                    if int(elem[1]) < a and a > _user.getStatus():
                        if _user == user:
                            message += "{id} - нельзя менять статус себе\n".format(
                                id=_user
                            )
                            changed.append(_user.user.id)
                        else:
                            a = int(elem[1])
                            _user.status = a
                            _user.save()
                            message += "{id} - установлен статус {status}\n".format(
                                id=_user,
                                status=a
                            )
                            changed.append(_user.user.id)
                    else:
                        message += "{id} - нет права изменить статус\n".format(
                            id=_user
                        )
                        changed.append(_user.user.id)
        if len(data) == 0:
            message = "{profile}, извини, я не нашла упоминаний о пользователях и статусу для них.".format(profile=user)
    else:
        message = "{profile}, у вас нет доступа для установки статусов другим ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def Nickname(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if type(user) != Bot:
        if args[1] == "":
            if user.name == "":
                message = "У [id{id}|вас] не установлен никнейм".format(
                    id = user.user.id
                )
            else:
                message = "[id{id}|Ваш] никнейм: {nickname}".format(
                    id = user.user.id,
                    nickname = user.name
                )
        elif args[1][0] == " ":
            if args[1].lower() == " удалить":
                user.name = ""
                user.save()
                message = "[id{id}|Ваш] никнейм удален.".format(
                    id = user.user.id
                )
            elif len(args[1]) <= 21:
                tmp = args[1]
                try:
                    flag = True
                    if re.fullmatch(r'^[а-яА-Я a-zA-Z0-9_]{1,}$', tmp):
                        user.name = args[1][1:]
                        user.save()
                        message = "Теперь [id{id}|ваш] никнейм - {nickname}".format(
                            id = user.user.id,
                            nickname = args[1][1:]
                        )
                        flag = False
                        
                    else:
                        flag = True
                except:
                    flag = True
                if flag:
                    message = "В [id{id}|вашем] никнейме содержатся запрещенные символы.".format(
                        id = user.user.id,
                    ) 
            else:
                message = "[id{id}|Ваш] никнейм должен быть не длиннее 20 символов.".format(
                    id=user.user.id
                )
    else:
        message = "{profile}, извини, но группам ставить никнеймы нельзя(".format(profile=user)
    return {
        'types': [
            'message'
        ],
        'message': {
            'text': message
        }
    }


def UpdateChat(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    session = vk.Session(access_token=DjangoSettings.ACCESS_TOKEN)
    api = vk.API(session, v=DjangoSettings.VK_VERSION)
    try:
        members = api.messages.getConversationMembers(
            peer_id=peer_id.id
        )
        if peer_id.worked:
            message = ""
        else:
            message = "{profile}, спасибо за обновление, я начала работу в этой беседе)\n\n".format(profile=user)
        peer_id.worked = True
        peer_id.save()
        updates = ""
        flag_updates = False
        changed = []
        for item in members['items']:
            _user = get_user(item['member_id'], peer_id, here=True)
            if item['member_id'] > 0:
                flag = item.get('is_admin', False)
                if flag:
                    changed.append(_user.user.id)
                    if _user.status != 10:
                        _user.status = 10
                        _user.save()
                        updates += "Пользователю {user} установила статус {status}\n".format(
                            user=_user,
                            status=_user.status
                        )
            flag = item.get('invited_by', 0)
            if flag != 0:
                _user.invited_by = get_user(flag, peer_id)
                flag_updates = True
        tmp = peer_id.users.filter(~Q(user__id__in=changed) & Q(status=10))
        for _user in tmp:
            updates += "С пользователя {user} снят {status} статус\n".format(
                user=_user,
                status=_user.status,
            )
            _user.status = 0
            _user.save()
        if flag_updates:
            updates = "Я узнала кто кого пригласил.\n" + updates
        if updates != "":
            message += "Обновления в этой беседе:\n"
            message += updates
        keyboard = ""
    except Exception as e:
        message = "Извините, я здесь все ещё не администратор."
        keyboard = {
            "one_time": False,
            "inline": True,
            'buttons': [
                [
                    {
                        "color": "positive",
                        'action': {
                            "type": "text",
                            "payload": "",
                            "label": "Обновить чат"
                        }
                    },
                ],
            ]
        }   
    return {
        'types': [
            'message'
        ],
        'message': {
            'text': message,
            'keyboard': keyboard,
        }
    }


def kickChat(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "kickAccess")
    if tmp['flag']:
        try:
            ids = []
            ids_dict = {}
            try:
                users = re.findall(r'\[id([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
            except:
                users = []
            try:
                groups = re.findall(r'\[club([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
            except:
                groups = []
            for _user in users:
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            kick_groups = []
            if reply_message:
                _user = reply_message['from_id']
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    if _user < 0:
                        kick_groups += [_user]
                    ids.append(_user)
                ids_dict[_user] = False
            for mess in fwd_messages:
                _user = mess['from_id']
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    if _user < 0:
                        kick_groups += [_user]
                    ids.append(_user)
                ids_dict[_user] = False
            users = peer_id.users.filter(kicked=False, user__id__in=ids)
            my_status = user.getStatus()
            max_status = min(my_status, peer_id.perms.getAccess('unKickAccess'))
            kickList = []
            kickList += kick_groups
            for _user in users:
                if _user.status < my_status:
                    kickList.append(_user)
            groups_dict = {}
            for _group in groups:
                _group = -int(_group)
                if groups_dict.get(_group, True):
                    group = get_user(_group, peer_id)
                    if group.status != 0:
                        kickList += [group]
                groups_dict[_group] = False
            if kickList == []:
                return {
                    "types": [
                        'message'
                    ],
                    'message': {
                        'text': 'Не найдено пользователей для исключения'
                    }
                }
            else:
                return {
                    "types": [
                        'kick_user'
                    ],
                    'kick_user': kickList
                }
        except Exception as e:
            return {
                "types": [
                    'message',
                ],
                'message': [
                    {
                        'text': "{profile}, извините, произошла неизвестная ошибка. Попробуйте позже".format(
                            profile=user
                        ),
                        'reply_message': message_id,
                    },
                    {
                        'text': fixError(e),
                        'peer_id': DjangoSettings.LOG_CHAT
                    },
                ]
            }
    else:
        message = "У вас нет доступа для исключения пользователей ({user}<{chat})".format(
            user = tmp['user'],
            chat = tmp['chat'],
        )
        return {
            "types": [
                'message'
            ],
            'message': {
                'text': message,
                'reply_message': message_id,
            }
        }


def warnChat(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "warnAccess")
    if tmp['flag']:
        try:
            ids = []
            ids_dict = {}
            try:
                users = re.findall(r'\[id([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
            except:
                users = []
            try:
                groups = re.findall(r'\[club([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
            except:
                groups = []
            for _user in users:
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            if reply_message:
                _user = reply_message['from_id']
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            for mess in fwd_messages:
                _user = mess['from_id']
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            users = peer_id.users.filter(kicked=False, user__id__in=ids)
            my_status = user.getStatus()
            max_status = min(my_status, peer_id.perms.getAccess('unKickAccess'))
            kickList = []
            message = ""
            for _user in users:
                if _user.getStatus() < my_status:
                    _user.warns += 1
                    _user.save()
                    message += "У {user} теперь {count}/{all} предов\n".format(
                        user=_user,
                        count=_user.warns,
                        all=peer_id.settings.countWarn
                    )
                    if _user.warns >= peer_id.settings.countWarn:
                        kickList.append(_user)
                else:
                    message += "Пользователю {user} выдавать преды нельзя\n".format(
                        user=_user
                    )
            groups_dict = {}
            for _group in groups:
                _group = -int(_group)
                if groups_dict.get(_group, True):
                    group = get_user(_group, peer_id)
                    message += "Нельзя выдавать предупреждение группе {group}\n".format(
                        group=group
                    )
                groups_dict[_group] = False
            if message == "":
                message = "{profile}, не найдено пользователей для выдачи предов\n".format(profile=user)
            else:
                message = "{profile}, предупреждения:\n\n".format(profile=user) + message
            if not(kickList is []):
                return {
                    "types": [
                        'message',
                        'kick_user'
                    ],
                    'message': {
                        'text': message,
                        'reply_message': message_id,
                    },
                    'kick_user': kickList
                }
        except Exception as e:
            return {
                "types": [
                    'message',
                ],
                'message': [
                    {
                        'text': "{profile}, извините, произошла неизвестная ошибка. Попробуйте позже".format(
                            profile=user
                        ),
                        'reply_message': message_id,
                    },
                    {
                        'text': fixError(e),
                        'peer_id': DjangoSettings.LOG_CHAT
                    },
                ]
            }
    else:
        message = "{profile}, у вас нет доступа для выдачи предупреждений пользователям ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def predList(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    message = ""
    users = peer_id.users.filter(kicked=False, leaved=False, warns__gte=1)
    for _ in users:
        message += "{user} - {warns}/{all}\n".format(
            user=_,
            warns=_.warns,
            all=peer_id.settings.countWarn
        )
    if message == "":
        message = "{profile}, пользователей с предупреждениями нет".format(profile=user)
    else:
        message = "{profile}, пользователи с предупреждениями:\n\n".format(profile=user) + message
    return {
        'types': [
            'message'
        ],
        'message': {
            'text': message
        }
    }


def profile(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8') # the ru locale is installed
    try:
        if type(user) == ChatUser:
            message = "{user}, ваш профиль:\n\n".format(
                user=user
            )
            if user.name:
                message += "Ваш никнейм - {nickname}\n".format(
                    nickname=user.name
                )
            if user.invite_by:
                message += "Вас пригласил - {user}\n".format(
                    user=user.invite_by
                )
            if user.warns > 0:
                message += "Предупреждений: {warns}/{all}\n".format(
                    warns=user.warns,
                    all=peer_id.settings.countWarn
                )
            boosts = user.get_boosts()
            if boosts > 1:
                message += "Множитель опыта (бустеры): х{count}\n".format(
                    count=boosts
                )
            _tmp = Attachment.objects.filter(
                mess__author__user=user.user,
                mess__date__gte=(
                    datetime.combine(
                        datetime.today(),
                        time(0, 0)
                    ) - timedelta(days=99)
                )
            ).values('data').annotate(Count('data')).order_by('-data__count')
            for _ in _tmp:
                message += "{type} - {count}\n".format(
                    type=get_type_of_media_object(_['data']),
                    count=_['data__count']
                )
            message += "\nИспользуете бота с {date} (UTC)\n".format(
                date=user.user.reg_date.strftime("%H:%M:%S %d.%m.%Y")
            )
            message += "В этой беседе с {date} (UTC)\n".format(
                date=user.reg_date.strftime("%H:%M:%S %d.%m.%Y")
            )
            return {
                'types': [
                    'message'
                ],
                'message': {
                    'text': message
                }
            }
        return {
            'types': []
        }
    except Exception as e:
        return {
                "types": [
                    'message',
                ],
                'message': [
                    {
                        'text': "{profile}, извините, произошла неизвестная ошибка. Попробуйте позже".format(
                            profile=user
                        ),
                        'reply_message': message_id,
                    },
                    {
                        'text': fixError(e),
                        'peer_id': DjangoSettings.LOG_CHAT
                    },
                ]
            }


def top(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "seeTopChatAccess")
    if tmp['flag']:
        message = ""
        try:
            if args[1] == "":
                _time = 7
            else:
                _time = int(args[1])
            _time = min(98,max(0, _time-1))
            users = peer_id.users.filter(kicked=False, leaved=False)
            _tmp = Message.objects.filter(
                author__in=users, 
                date__gte=(
                    datetime.combine(
                        datetime.today(), 
                        time(0,0)
                    ) - timedelta(days=_time)
                )
            ).values('author').annotate(Sum('words'), Sum('length')).order_by('-length__sum')
            if _tmp.count() == 0:
                message = "Топ сообщений за {count} пустой".format(count=_time)
            else:
                message = "Топ беседы за {days} дней: \n\n".format(
                    days=_time+1
                )
                ids = {}
                c = 0
                for data in _tmp:
                    ids[data['author']] = False
                    if data['length__sum'] + data['words__sum'] == 0:
                        c += 1
                        continue
                    message += "{user} - {chars} симв. ({count} сообщ.)\n".format(
                        chars=data['length__sum'],
                        user=ChatUser.objects.get(pk=data['author']),
                        count=data['words__sum']
                    )
                for _user in users:
                    if ids.get(_user.pk, True):
                        c += 1
                        #message += "{user} - 0 симв. (0 сообщ.)\n".format(
                        #    user = _user
                        #)
                if c:
                    message += "И ещё {count} человек с нулевой статистикой".format(
                        count=c
                    )
        except Exception as e:
            message = "{profile}, неверный параметр времени".format(profile=user)
    else:
        message = "{profile}, у вас нет доступа для просмотра топа беседы ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def who(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "whoAccess")
    if tmp['flag']:
        users = peer_id.users.filter(kicked = False, leaved = False)
        message = "{profile}, я думаю, это {user}".format(
            user=choice(users),
            profile=user
        )
    else:
        message = "{profile}, у вас нет доступа для доступа к команде \"кто\" ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def peer_id_number(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    return {
        'types': [
            'message'
        ],
        'message': {
            'text': "{profile}, номер вашей беседы - {number}".format(
                number=peer_id.id,
                profile=user
            )
        }
    }


def kickSpecial(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if checkAccess(user, peer_id, "kickAccess")['flag']:
        if payload != "":
            try:
                payload = json.loads(payload)
                kick_id = int(payload.get('kick_id', False))
                group_id = -int(payload.get('group_id', -kick_id))
                if kick_id:
                    kick_id = int(kick_id)
                    try:
                        kick_id = get_user(kick_id, peer_id)
                        if kick_id.leaved:
                            session = vk.Session(access_token = DjangoSettings.ACCESS_TOKEN)
                            api = vk.API(session, v=DjangoSettings.VK_VERSION)
                            api.messages.removeChatUser(chat_id=peer_id.id-2000000000, member_id=kick_id.get_id())
                            kick_id.leaved = False
                            kick_id.kicked = True
                            kick_id.save()
                    except Exception as e:
                        pass
            except:
                pass
    return {
        'types': [],
    }


def getStatisticBot(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if user.getStatus() > 10:
        message = "Статистика бота{name}:\n\n"
        if args[0].lower() == " эко":
            message = message.format(name=" \"Экономика\"")
            message += "Выдано опыта: {count}\n".format(
                count=Experience.objects.all().aggregate(
                    total=Sum('count', field="count")
                )['total']/1000
            )
            message += "Выдано опыта за сегодня: {count}\n".format(
                count=Experience.objects.filter(
                        date__gte=datetime.combine(
                            datetime.today(),
                            time(0, 0)
                        ) - timedelta(days=0),
                        date__lte=datetime.now()
                    ).aggregate(
                    total=Sum('count', field="count")
                )['total']/1000
            )
            message += "Выдано опыта за месяц: {count}\n\n".format(
                count=Experience.objects.filter(
                        date__gte=datetime.combine(
                            datetime.today(),
                            time(0, 0)
                        ) - timedelta(days=31),
                        date__lte=datetime.now()
                    ).aggregate(
                    total=Sum('count', field="count")
                )['total']/1000
            )
            message += "В обороте {count} единиц монет\n\n".format(
                count=Money.objects.all().aggregate(
                    total=Sum('count', field="count")
                )['total']
            )
            message += "В обороте:\n"
            message += "• бустеров: {count}\n".format(
                count=InventoryItem.objects.filter(item___type=1).count()
            )
            message += "• кейсов: {count}\n".format(
                count=InventoryItem.objects.filter(item___type=2).count()
            )
            message += "• предметов: {count}\n".format(
                count=InventoryItem.objects.filter(item___type=3).count()
            )
            message += "- Всего: {count}\n\n".format(
                count=InventoryItem.objects.all().count()
            )
            message += "Всего создано:\n"
            message += "• бустеров: {count}\n".format(
                count=Item.objects.filter(_type=1).count()
            )
            message += "• кейсов: {count}\n".format(
                count=Item.objects.filter(_type=2).count()
            )
            message += "• предметов: {count}\n".format(
                count=Item.objects.filter(_type=3).count()
            )
            message += "- Всего: {count}\n".format(
                count=Item.objects.all().count()
            )
        elif args[0].lower() == " сообщения":
            message = message.format(name=" \"Сообщения\"")
            message += "За сегодня обработано {count} сообщений\n".format(
                count=Message.objects.filter(
                    date__gte=datetime.combine(
                        datetime.today(),
                        time(0, 0)
                    )
                ).count()
            )
            message += "За вчера обработано {count} сообщений\n".format(
                count=Message.objects.filter(
                    date__lte = (
                        datetime.combine(
                            datetime.today(),
                            time(0, 0)
                        )
                    ),
                    date__gte = (
                        datetime.combine(
                            datetime.today(),
                            time(0, 0)
                        ) - timedelta(days=1)
                    )
                ).count()
            )
            message += "В базе данных сохранено {count} сообщений\n".format(
                count=Message.objects.all().count()
            )
        elif args[0].lower() == " вложения":
            message = message.format(name=" \"Вложения\"")
            _tmp = Attachment.objects.filter(
                mess__date__gte=(
                    datetime.combine(
                        datetime.today(),
                        time(0, 0)
                    ) - timedelta(days=99)
                )
            ).values('data').annotate(Count('data')).order_by('-data__count')
            for data in _tmp:
                message += "{type} - {count}\n".format(
                    type=get_type_of_media_object(data['data']),
                    count=data['data__count']
                )
        elif args[0].lower() == " общие":
            message = message.format(name="")
            message += "Выдано опыта: {count}\n".format(
                count=Experience.objects.all().aggregate(
                    total=Sum('count', field="count")
                )['total']/1000
            )
            message += "В обороте {count} единиц монет\n".format(
                count=Money.objects.all().aggregate(
                    total=Sum('count', field="count")
                )['total']
            )
            message += "В обороте {count} предметов\n".format(
                count=InventoryItem.objects.all().count()
            )
            message += "Всего предметов: {count}\n\n".format(
                count=Item.objects.all().count()
            )
            message += "В базе данных сохранено {count} сообщений\n".format(
                count=Message.objects.all().count()
            )
            message += "Я работаю в {count} беседах\n".format(
                count=Chat.objects.filter(worked=True).count(),
            )
            message += "Я была в {count} беседах\n".format(
                count=Chat.objects.filter().count(),
            )
            message += "Я уже работаю {date}\n".format(
                date=(datetime.now() - DjangoSettings.START_WORK_TIME)
            )
        else:
            message = message.format(name="")
            if args[0] != "":
                message += "Нет такого типа статистики.\n\n"
            message += (
                "Доступные типы статистики:\n"
                "1) Эко\n"
                "2) Сообщения\n"
                "3) Вложения\n"
                "4) Общие\n"
            )
        return {
            'types': ['message'],
            'message': {
                'text': message
            }
        }
    return {
        'types': []
    }


def getBotList(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    if user.getStatus() > 10:
        try:
            args = args[0]
            if args.lower() == " группы":
                message = "Список групп:\n\n"
                tmp = Bot.objects.all()
                count = 0
                for _ in tmp:
                    if count:
                        message += ", "
                    count += 1
                    message += "{group}".format(group=_)
            elif args.lower() == " тестеры":
                message = "Список тестировщиков:\n\n"
                tmp = User.objects.filter(tester=True)
                count = 0
                for _ in tmp:
                    if count:
                        message += ", "
                    count += 1
                    message += "{group}".format(group=_)
            elif args == "":
                message = ("Возможные списки:\n\n"
                           "Группы\n"
                           "Тестеры\n")
            else:
                message = "Такого списка нет"
            return {
                'types': [
                    'message'
                ],
                'message': {
                    'text': message
                }
            }
        except Exception as e:
            return {
                "types": [
                    'message',
                ],
                'message': [
                    {
                        'text': "{profile}, извините, произошла неизвестная ошибка. Попробуйте позже".format(
                            profile=user
                        ),
                        'reply_message': message_id,
                    },
                    {
                        'text': fixError(e),
                        'peer_id': DjangoSettings.LOG_CHAT
                    },
                ]
            }
    return {
        'types':
            []
    }


def unWarnChat(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "warnAccess")
    if tmp['flag']:
        try:
            ids = []
            ids_dict = {}
            users = re.findall(r'\[id([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
            groups = re.findall(r'\[club([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
            for _user in users:
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            if reply_message:
                _user = reply_message['from_id']
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            for mess in fwd_messages:
                _user = mess['from_id']
                _tmp = ids_dict.get(_user, True)
                if _tmp:
                    ids.append(_user)
                ids_dict[_user] = False
            users = peer_id.users.filter(kicked=False, user__id__in=ids)
            my_status = user.getStatus()
            max_status = min(my_status, peer_id.perms.getAccess('unKickAccess'))
            kickList = []
            message = ""
            for _user in users:
                if _user.getStatus() < my_status:
                    _user.warns -= 1
                    _user.save()
                    if _user.warns < 0:
                        _user.warns = 0
                    message += "У {user} теперь {count}/{all} предов\n".format(
                        user = _user,
                        count = _user.warns,
                        all = peer_id.settings.countWarn
                    )
                else:
                    message += "Пользователю {user} выдавать преды нельзя\n".format(
                        user = _user
                    )
            groups_dict = {}
            for _group in groups:
                _group = -int(_group)
                if groups_dict.get(_group, True):
                    group = get_user(_group, peer_id)
                    message += "Нельзя выдавать предупреждение группе {group}\n".format(
                        group = group
                    )
                groups_dict[_group] = False
            if message == "":
                message = "{profile}, не найдено пользователей для выдачи предов\n".format(profile=user)
            else:
                message = "{profile}, предупреждения:\n\n".format(profile=user) + message
            if not(kickList is []):
                return {
                    "types": [
                        'message',
                        'kick_user'
                    ],
                    'message': {
                        'text': message,
                        'reply_message': message_id,
                    },
                    'kick_user': kickList
                }
        except Exception as e:
            return {
                "types": [
                    'message',
                ],
                'message': [
                    {
                        'text': "{profile}, извините, произошла неизвестная ошибка. Попробуйте позже".format(profile=user),
                        'reply_message': message_id,
                    },
                    {
                        'text': fixError(e),
                        'peer_id': DjangoSettings.LOG_CHAT
                    },
                ]
            }
    else:
        message = "{profile}, у вас нет доступа для выдачи предупреждений пользователям ({user}<{chat})".format(
            user=tmp['user'],
            chat=tmp['chat'],
            profile=user
        )
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }


def get_balance(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload="", _type="str"):
    money = user.user.money.all().aggregate(
        total=Sum('count', field="count")
    ).get('total', 0)
    if money is None:
        money = 0
    if _type == "money":
        return money
    exp = user.user.exp.all().aggregate(
        total=Sum('count', field="count")
    )['total']
    if exp is None:
        exp = 0
    else:
        exp /= 100
    if _type == "exp":
        return exp
    return {
        'types': ['message'],
        'message': [
            {
                'text': 'Ваш баланс - {money}\nВаш опыт - {exp}'.format(
                    exp=exp,
                    money=money
                ),
                "peer_id": user.get_id()
            },
            {
                'text': '{nickname}, информация о балансе отправлена Вам личным сообщением.'.format(
                    nickname=user
                )
            }
        ]
    }


def shop(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    items = Item.objects.filter(
        can_buy=True, price__gte=0
    ).order_by('_type')
    if items.count():
        message = (
            "{profile}, магазин:\n\n".format(profile=user)
        )
        for item in items:
            message += "{number}) {simv}{name} - {price} монет\n".format(
                number=item.pk,
                simv=("&#127765;" if (item._type in [1, 2, 3]) else "&#127761;"),
                name=item.name.capitalize(),
                price=item.price
            )
        message += "\n&#127765; - Предмет, применяющийся на пользователя\n"
        message += "&#127761; - Предмет, применяющийся на чат\n"
        message += "\nЧтобы купить предмет, напиши команду \"!купить [номер предмета]\""
    else:
        message = "Магазин пустой, приходи попозже"
    return {
        'types': ['message'],
        'message': {
            'text': message
        }
    }


def buy(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    _type = args[1]
    try:
        _type = int(_type)
    except:
        return {
            'types': ['message'],
            'message': {
                'text': '{profile}, неправильный параметр предмета'.format(profile=user)
            }
        }
    try:
        item = Item.objects.get(pk=_type)
    except:
        return {
            'types': ['message'],
            'message': {
                'text': '{profile}, акого предмета не существует'.format(profile=user)
            }
        }
    money = get_balance(user, peer_id, [], _type="money")
    message = "{user}, извините, невозможно купить данный предмет".format(
        user=user
    )
    if item.can_buy:
        if item.price:
            if money >= item.price:
                tmp = Money.objects.create(
                    user=user.user,
                    count=-item.price,
                    description="Покупка предмета {product}".format(
                        product=item
                    )
                )
                tmp.save()
                invItem = item.newItem(user.user)
                invItem.save()
                message = "{user}, Вы купили предмет {item} за {price} монет.\n" \
                          "В Вашем инвентаре он находится под номером {number}".format(
                    user=user,
                    item=item,
                    price=item.price,
                    number=user.user.inv.filter(uses=0).count()
                )
            else:
                message = "{user}, у Вас нет необходимого для покупки количества монет ({price} монет)".format(
                    user=user,
                    price=item.price
                )
    return {
        'types': ['message'],
        'message': {
            'text': message
        }
    }


def inventory(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    inv = user.user.inv.filter(uses=0)
    if inv.count():
        count = int(inv.count()/10)+int(bool(inv.count() % 10))
        if args[1] != "":
            try:
                page = int(args[1])
            except:
                return {
                    'types': ['message'],
                    'message': {
                        'text': "{user}, я не поняла на какую страницу инвентаря Вы хотите перейти, повторите ещё раз".format(
                            user=user
                        )
                    }
                }
            if not((page > 0) and (page <= count)):
                return {
                    'types': ['message'],
                    'message': {
                        'text': "{user}, у вас не так много предметов чтобы перейти на эту страницу инвентаря".format(
                            user=user
                        )
                    }
                }
        else:
            page = 1
        message = "{user}, Ваш инвентарь (страница {page}/{count}):\n\n".format(
            user=user,
            page=page,
            count=count
        )
        for number, _ in enumerate(inv[(page-1)*10:page*10]):
            message += "{number}) {simv}{name}\n".format(
                number=number+1,
                simv=("&#127765;" if (_.item._type in [1, 2, 3]) else "&#127761;"),
                name=_.item.name.capitalize()
            )
        message += "\n&#127765; - Предмет, применяющийся на пользователя\n"
        message += "&#127761; - Предмет, применяющийся на чат\n"
        message += "\nЧтобы использовать предмет, напишите \"!использовать [номер предмета]\""
    else:
        message = "{user}, у вас пустой инвентарь".format(
            user=user
        )
    return {
        'types': ['message'],
        'message': {
            'text': message
        }
    }


def use(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    try:
        _id = args[1]
        try:
            _id = int(_id)
        except:
            return {
                'types': ['message'],
                'message': {
                    'text': '{user}, неправильный параметр предмета'.format(
                        user=user
                    )
                }
            }
        try:
            item = user.user.inv.filter(uses=0)[_id-1]
        except:
            return {
                'types': ['message'],
                'message': {
                    'text': '{user}, такого предмета не существует в вашем инвентаре'.format(
                        user=user
                    )
                }
            }
        if item.item._type == 1:
            if item.uses == 1:
                message = '{user}, такого предмета не существует в вашем инвентаре'.format(
                    user=user
                )
            else:
                value = float(item.item.action[1:])
                if user.activate_booster(value):
                    message = "{user}, Вы активировали {item} на 30 дней".format(
                        user=user,
                        item=item.item.name.capitalize()
                    )
                    item.uses += 1
                    item.save()
                else:
                    message = "{user}, у Вас уже активировано максимально возможное количество бустеров".format(
                        user=user
                    )
        elif item.item._type == 4:
            if item.uses == 1:
                message = '{user}, такого предмета не существует в вашем инвентаре'.format(
                    user=user
                )
            else:
                if peer_id.activate_premium():
                    message = "{user}, Вы активировали премиум беседы на 30 дней. Премиум действителен до {date}".format(
                        user=user,
                        item=item.item.name.capitalize(),
                        date=peer_id.settings.premium
                    )
                    item.uses += 1
                    item.save()
                else:
                    message = "{user}, произошла неизвестная ошибка. Попробуйте позже".format(
                        user=user
                    )
        elif item.item._type == 5:
            if item.uses == 1:
                message = '{user}, такого предмета не существует в вашем инвентаре'.format(
                    user=user
                )
            else:
                if peer_id.is_premium():
                    if user.activate_booster_chat():
                        message = "{user}, Вы активировали буст беседе на 30 дней. Теперь буст чата составляет x{chat_boost}".format(
                            user=user,
                            item=item.item.name.capitalize(),
                            chat_boost=peer_id.get_boosts()
                        )
                        item.uses += 1
                        item.save()
                    else:
                        message = "{user}, у беседы уже активировано максимально возможное количество бустеров".format(
                            user=user
                        )
                else:
                    message = "{user}, эта беседа не имеет премиум статуса. Бустить беседы можно только с премиум статусом".format(
                        user=user
                    )
        else:
            message = "{user}, F".format(
                user=user
            )
    except Exception as e:
        return {
            'types': ['message'],
            'message': [
                {
                    'text': "{user}, извини, произошла неизвестная ошибка"
                },
                {
                    'text': fixError(e),
                    'peer_id': DjangoSettings.LOG_CHAT
                }
            ]
        }
    return {
        'types': ['message'],
        'message': {
            'text': message
        }
    }


def getChatSettings(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    settings = peer_id.settings
    message = "{user}, настройки беседы:\n\n".format(
        user=user
    )
    message += "Неизменяемые параметры:\nПриветствие {string}установлено\n".format(
        string=("не " if (settings.inviteMessage == "") else "")
    )
    message += "Умножение опыта: х{count}\n".format(
        count=peer_id.get_boosts()
    )
    message += "Максимальное количество опыта в час: {count}\n".format(
        count=int(settings.limit_message/100)
    )
    if timezone.now() < settings.premium:
        message += "Премиум в этой беседе до {date}\n".format(
            date=settings.premium
        )
    message += "\nИзменяемые параметры:\n1) Максимальное количество предупреждений для исключения: {count}\n".format(
        count=settings.countWarn
    )
    tmp = checkAccess(user, peer_id, "setPermsAccess")
    if tmp['flag']:
        message += "\n\nДля изменения настройки используйте команду " \
                   "\"Рая настройки установить [номер_настройки] [значение параметра]\""
    return {
        "types": [
            'message'
        ],
        'message': {
            'text': message,
            'reply_message': message_id,
        }
    }
