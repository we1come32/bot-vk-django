import re
from .simple_function import *
from .models import *
from django.conf import settings as DjangoSettings
from django.db.models import Q
import vk
import locale
from datetime import datetime, timedelta, time
from django.db.models import Sum
from random import randint, choice
import json


def help(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    return {
        'types': ['message'],
        'message': 
        {
            "text" :(
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
        message = "У вас нет доступа отправлять сообщения от моего имени ({user}<{chat})".format(
            user = tmp['user'],
            chat = tmp['chat'],
        )

def statuses(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "getListStatusAccess")
    if tmp['flag']:
        message = "Статусы пользователей в беседе\n"
        try:
            users = peer_id.users.filter(leaved=False, kicked=False).order_by('-status')
            if True:
                count = 0
                for _user in users:
                    status = _user.getStatus()
                    if status > 0:
                        count += 1
                        message += "\n{name} - {status}".format(
                            name = _user,
                            status = status
                        )
                if count == 0:
                    message = "Пользоватлей со статусом больше 0 в беседе нет"
            else:
                message = str(users)
        except Exception as e:
            message = str(fixError(e))
    else:
        message = "У вас нет доступа для просмотра статусов беседы ({user}<{chat})".format(
            user = tmp['user'],
            chat = tmp['chat'],
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
            status = user.getStatus()
        )
    else:
        tmp = checkAccess(user, peer_id, "getListStatusAccess")
        if tmp['flag']:
            match = re.findall(r'\[id([0-9]{1,})\|[a-zA-Z0-9а-яА-Я @*._]{1,}\]', args[1])
            if match:
                message = "Статусы запрашиваемых пользователей:"
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
                message = "Мы не нашли в вашем запросе упоминаний пользователей"
        else:
            message = "У вас нет доступа для просмотра чужого статуса ({user}<{chat})".format(
                user = tmp['user'],
                chat = tmp['chat'],
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
            message = "Приветствие не установлено"
        else:
            message = "Приветствие: \n\n" + tmp
    else:
        tmp = checkAccess(user, peer_id, "changeInviteMessageAccess")
        if tmp['flag']:
            peer_id.settings.inviteMessage = args[1][1:]
            peer_id.settings.save()
            message = "Приветствие установлено. Новое приветствие: \n\n" + peer_id.settings.inviteMessage
        else:
            message = "У вас нет доступа для просмотра чужого статуса ({user}<{chat})".format(
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

def delInviteMessage(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "changeInviteMessageAccess")
    if tmp['flag']:
        peer_id.settings.inviteMessage = ""
        peer_id.settings.save()
        message = "Приветствие удалено"
    else:
        message = "У вас нет доступа для удаления приветствия беседы ({user}<{chat})".format(
            user = tmp['user'],
            chat = tmp['chat'],
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
                    message = "У вас нет права менять данный доступ."
                    key = key['key']
                    tmp = perms.getAccess(key)
                    if user.getStatus() >= tmp and user.getStatus()>=args[1]:
                        if type(tmp) == int:
                            tmp = args[1]
                            if tmp>=0 and tmp <=10:
                                perms.setAccess(key, tmp)
                                perms.save()
                                message = "Доступ №{number} изменен.\n\n{number}) {description} - {status}".format(
                                    number=args[0],
                                    description = perms.getAccesses()[key],
                                    status = tmp,
                                )
                            else:
                                message = "Ошибка установки доступа"
                        else:
                            message = "Ошибка установки доступа"
                else:
                    message = "Запрашиваемый доступ №{number}: \n\nДоступ не найден".format(
                        number=args[0]
                    )
            elif l_args == 1:
                key = perms.getAccessById(args[0])
                if key['flag']:
                    message = "Запрашиваемый доступ №{number}:\n\n{number}) {description} - {status}".format(
                        number=args[0],
                        description = perms.getAccesses()[key['key']],
                        status = perms.getAccess(key['key']),
                    )
                else:
                    message = "Запрашиваемый доступ №{number}: \n\nДоступ не найден".format(
                        number=args[0]
                    )
            else:
                message = "Неверное использование команды.\nОбратитесь за помощью на страницу помощи (Рая помощь) или в личные сообщения мне."
        except Exception as e:
            message = "Неверное использование команды.\nОбратитесь за помощью на страницу помощи (Рая помощь) или в личные сообщения мне."
    else:
        message = "У вас нет доступа менять доступы ({user}<{chat})".format(
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

def getListPerms(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "getPermsAccess")
    if tmp['flag']:
        perms = peer_id.perms
        Accesses = perms.getAccesses()
        message = "Список доступов и их значения в этой беседе:\n\n"
        for number, key in enumerate(Accesses.keys()):
            message += "{number:3} {description} - {value}\n".format(
                number = str(number+1) + ")",
                description = Accesses[key],
                value = perms.getAccess(key) 
            )
        message += "\n\nДля изменения доступа используйте команду \"Рая доступ [номер_доступа] [необходимый статус]\""
    else:
        message = "У вас нет доступа для просмотра списка доступов ({user}<{chat})".format(
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

def setStatus(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "setStatusAccess")
    if tmp['flag']:
        import re
        pattern = r'\[id([0-9]{1,})\|[A-Za-zа-яА-Я0-9 @*._]{1,}\] ([0-9]{1,})'
        data = re.findall(pattern, args[1])
        message = "Измененые статусы:\n\n"
        changed = []
        for elem in data:
            _user = get_user(int(elem[0]), peer_id)
            if type(_user) != Bot:
                if _user.user.id not in changed:
                    a = user.getStatus()
                    if int(elem[1]) < a and a > _user.getStatus():
                        if _user == user:
                            message += "{id} - нельзя менять статус себе\n".format(
                                id = _user
                            )
                            changed.append(_user.user.id)
                        else:
                            a = int(elem[1])
                            _user.status = a
                            _user.save()
                            message += "{id} - установлен статус {status}\n".format(
                                id = _user,
                                status = a
                            )
                            changed.append(_user.user.id)
                    else:
                        message += "{id} - нет права изменить статус\n".format(
                            id = _user
                        )
                        changed.append(_user.user.id)
        if len(data) == 0:
            message = "Извини, я не нашла упоминаний о пользователях и статусу для них."
    else:
        message = "У вас нет доступа для установки статусов другим ({user}<{chat})".format(
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
                    id = user.user.id
                )
    else:
        message = "Извини, друг мой, но ботам ставить никнеймы нельзя("
    return {
        'types': [
            'message'
        ],
        'message': {
            'text': message
        }
    }

def UpdateChat(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    session = vk.Session(access_token = DjangoSettings.ACCESS_TOKEN)
    api = vk.API(session, v="5.103")
    try:
        members = api.messages.getConversationMembers(
            peer_id = peer_id.id
        )
        if peer_id.worked:
            message = ""
        else:
            message = "Спасибо за обновление, я начала работу в этой беседе)\n\n"
        peer_id.worked = True
        peer_id.save()
        updates = ""
        flag_updates = False
        changed = []
        for item in members['items']:
            _user = get_user(item['member_id'], peer_id, here=True)
            if item['member_id']>0:
                flag = item.get('is_admin', False)
                if flag:
                    changed.append(_user.user.id)
                    if _user.status != 10:
                        _user.status = 10
                        _user.save()
                        updates += "Пользователю {user} установила статус {status}\n".format(
                            user = _user,
                            status = _user.status
                        )
            flag = item.get('invited_by', 0)
            if flag != 0:
                _user.invited_by = get_user(flag, peer_id)
                flag_updates = True
        tmp = peer_id.users.filter(~Q(user__id__in=changed) & Q(status=10))
        for _user in tmp:
            updates += "С пользователя {user} снят {status} статус\n".format(
                user = _user,
                status = _user.status,
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
        message = fixError(e)
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
            users = re.findall(r'\[id([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
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
            for _user in users:
                if _user.status < my_status:
                    kickList.append(_user)
            groups = re.findall(r'\[club([0-9]{1,})\|[a-zA-Zа-яА-Я @*._0-9]{1,}\]', args[1])
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
                'message': {
                    'text': fixError(e),
                    'reply_message': message_id,
                },
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
                if _user.status < my_status:
                    _user.warns += 1
                    _user.save()
                    message += "У {user} теперь {count}/{all} предов\n".format(
                        user = _user,
                        count = _user.warns,
                        all = peer_id.settings.countWarn
                    )
                    if _user.warns >= peer_id.settings.countWarn:
                        kickList.append(_user)
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
                message = "Не найдено пользователей для выдачи предов\n"
            else:
                message = "Предупреждения:\n\n" + message
            if kickList != []:
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
                'message': {
                    'text': fixError(e),
                    'reply_message': message_id,
                },
            }
    else:
        message = "У вас нет доступа для выдачи предупреждений пользователям ({user}<{chat})".format(
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

def predList(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    message = ""
    users = peer_id.users.filter(kicked=False, leaved=False, warns__gte=1)
    for _ in users:
        message += "{user} - {warns}/{all}\n".format(
            user = _,
            warns = _.warns,
            all = peer_id.settings.countWarn
        )
    if message == "":
        message = "Пользователей с предупреждениями нет"
    else:
        message = "Пользователи с предупреждениями:\n\n" + message
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
    if type(user) == ChatUser:
        message = "{user}, ваш профиль:\n\n".format(
            user = user
        )
        if user.name:
            message += "Ваш никнейм - {nickname}\n".format(
                nickname = user.name
            )
        if user.invite_by:
            message += "Вас пригласил - {user}\n".format(
                user = user.invite_by
            )
        message += "Предупреждений: {warns}/{all}\n".format(
            warns = user.warns,
            all = peer_id.settings.countWarn
        )
        message += "Используете бота с {date} (UTC)\n".format(
            date = user.user.reg_date.strftime("%H:%M:%S %d.%m.%Y")
        )
        message += "В этой беседе с {date} (UTC)\n".format(
            date = user.reg_date.strftime("%H:%M:%S %d.%m.%Y")
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
                date__gte = (
                    datetime.combine(
                        datetime.today(), 
                        time(0,0)
                    ) - timedelta(days=_time)
                )
            ).values('author').annotate(Sum('words'),Sum('length')).order_by('-length__sum')
            if _tmp.count() == 0:
                message = "Топ сообщений за {count} пустой".format(count=_time)
            else:
                message = "Топ беседы за {days} дней: \n\n".format(
                    days = _time+1
                )
                ids = {}
                for data in _tmp:
                    ids[data['author']] = False
                    message += "{user} - {chars} симв. ({count} сообщ.)\n".format(
                        chars = data['length__sum'],
                        user = ChatUser.objects.get(pk=data['author']),
                        count = data['words__sum']
                    )
                c = 0
                for _user in users:
                    if ids.get(_user.pk, True):
                        c += 1
                        #message += "{user} - 0 симв. (0 сообщ.)\n".format(
                        #    user = _user
                        #)
                if c>0:
                    message += "И ещё {count} человек с нулевой статистикой".format(
                        count=c
                    )
        except Exception as e:
            message = "Неверный параметр времени"
            #message = fixError(e)
    else:
        message = "У вас нет доступа для просмотра топа беседы ({user}<{chat})".format(
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

def who(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    tmp = checkAccess(user, peer_id, "whoAccess")
    if tmp['flag']:
        users = peer_id.users.filter(kicked = False, leaved = False)
        message = "Я думаю, это {user}".format(
            user = choice(users)
        )
    else:
        message = "У вас нет доступа для доступа к команде \"кто\" ({user}<{chat})".format(
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

def peer_id_number(user, peer_id, args, reply_message="", fwd_messages=[], message_id=0, payload=""):
    return {
        'types': [
            'message'
        ],
        'message': {
            'text': "Номер вашей беседы - {number}".format(
                number = peer_id.id
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
                            api = vk.API(session, v="5.103")
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
    if user.getStatus()>10:
        message = "Статистика бота:\n\n"
        c = Chat.objects.filter(worked=True).count()
        message += "Рая работает в {count} беседах\n".format(
            count=c,
        )
        return {
            'types': ['message'],
            'message': {
                'text': message
            }
        }
    return {
        'types':[]
    }