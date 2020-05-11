from django.db import models
from datetime import datetime

class SysConfig(models.Model):
    param = models.CharField(default="", max_length=20)
    value = models.CharField(default="", max_length=20)
    _type = models.CharField(default="", max_length=3)


class User(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)
    reg_date = models.DateTimeField(default=datetime.now)
    status = models.IntegerField(default=0)
    tester = models.BooleanField(default=False)


class Attachment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    data = models.TextField(max_length="")
    typeAttachment = models.CharField(default="", max_length=100)
    mess = models.ForeignKey('Message', on_delete=models.CASCADE, related_name="attachments")
    def __str__(self):
        return self.typeAttachment


class Message(models.Model):
    author = models.ForeignKey('ChatUser', on_delete=models.CASCADE, related_name="messages")
    date = models.DateTimeField(default=datetime.now)
    length = models.IntegerField(default=0)
    words = models.IntegerField(default=0)
    message = models.CharField(default="", max_length=4096)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="messages")
    def __str__(self):
        return str(self.date) + " " +str(self.author)


class Permission(models.Model):
    kickAccess = models.IntegerField(default=10)                #1
    unKickAccess = models.IntegerField(default=10)              #2
    setStatusAccess = models.IntegerField(default=10)           #3
    seeAllStatisticAccess = models.IntegerField(default=0)      #4
    seeStatisticAccess = models.IntegerField(default=1)         #5
    seeTopChatAccess = models.IntegerField(default=0)           #6
    sendLinkAccess = models.IntegerField(default=0)             #7
    getPermsAccess = models.IntegerField(default=10)            #8
    sayAccess = models.IntegerField(default=0)                  #9
    setPermsAccess = models.IntegerField(default=10)            #10
    getListStatusAccess = models.IntegerField(default=10)       #11
    getActivityAccess = models.IntegerField(default=10)         #12
    kickAuroListAccess = models.IntegerField(default=10)        #13
    callAutoListAccess = models.IntegerField(default=10)        #14
    changeInviteMessageAccess = models.IntegerField(default=10) #15
    getOnlineAccess = models.IntegerField(default=10)           #16
    addFriendsAccess = models.IntegerField(default=0)           #17
    sendSpamAccess = models.IntegerField(default=0)             #18
    brakAccess = models.IntegerField(default=0)                 #19
    whoAccess = models.IntegerField(default=0)                  #20
    ignoreAccess = models.IntegerField(default=10)              #21
    unLeaveAutoKickAccess = models.IntegerField(default=0)      #22
    sendAllAccess = models.IntegerField(default=0)              #23
    sendOnlineAccess = models.IntegerField(default=0)           #24
    warnAccess = models.IntegerField(default=10)                #25
    def getAccess(self, nameAccess):
        try:
            return self.__getattribute__(nameAccess)
        except:
            return False
    def getAccesses(self):
        return {
            'kickAccess': "Возможность исключить пользователя из беседы",
            'unKickAccess': "Запрет на исключение пользователя из беседы в автоисключениях",
            'setStatusAccess': "Право устанавливать статусы",
            'seeAllStatisticAccess': "Просмотр активности других пользователей",
            'seeStatisticAccess': "Просмотр активности пользователя",
            'seeTopChatAccess': "Просмотр топа беседы",
            'sendLinkAccess': "Возможность отправлять ссылки",
            'getPermsAccess': "Получение списка доступов",
            'sayAccess': "Возможность написать что-то от имени Раи",
            'setPermsAccess': "Настройка доступов к командам",
            'getListStatusAccess': "Получение списка статусов беседы",
            'getActivityAccess': "Получение информации об активности беседы",
            'kickAuroListAccess': "Доступ к действию \"кик\" для автосписков",
            'callAutoListAccess': "Доступ к действию \"позвать\" для автосписков",
            'changeInviteMessageAccess': "Возможность поменять приветствие беседы",
            'getOnlineAccess': "Получение списка пользователей онлайн",
            'addFriendsAccess': "Возможность добавлять друзей в беседу",
            'sendSpamAccess': "Возможность рассылки спама (подробнее о системе vk.com/wall...)",
            'brakAccess': "Возможность заключать брак в беседе",
            'whoAccess': "Развлекателькая команда \"Кто\"",
            'ignoreAccess': "Настройка игнорирования пользователей",
            'unLeaveAutoKickAccess': "Отмена действия \"кик\" при выходе из беседы",
            'sendAllAccess': "Разрешение отправлять упоминания типа @all",
            'sendOnlineAccess': "Разрешение отправлять упоминания типа @online",
            'warnAccess': "Возможность выдавать предупреждения",
        }
    def getAccessById(self, id):
        accesses = self.getAccesses()
        for number, key in enumerate(accesses.keys()):
            if number+1 == id:
                return {
                    'flag': True,
                    'key': key
                }
        return {
            'flag': False
        }
    def setAccess(self, name, count):
        if count>=0 and count <= 10:
            self.__setattr__(name, count)
            self.save()
            return True
        return False


class ChatUser(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="chatUser")
    status = models.IntegerField(default=0)
    name = models.CharField(default="", max_length=4000, null=True)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="users")
    warns = models.IntegerField(default=0)
    leaved = models.BooleanField(default=False)
    reg_date = models.DateTimeField(default=datetime.now)
    kicked = models.BooleanField(default=False)
    invite_by = models.ForeignKey('ChatUser', on_delete=models.CASCADE, null=True, related_name="invited_users")
    ban = models.BooleanField(default=False)
    def getStatus(self):
        return max(self.status, self.user.status)
    def equial(self, data):
        if type(data) == type(self):
            return self.user.id == data.user.id
        return False
    def __str__(self):
        if self.name == "":
            return "@id{id}".format(
                id = self.user.id,
            )
        return "[id{id}|{name}]".format(
            id = self.user.id,
            name = self.name,
        )
    def get_id(self):
        return self.user.id
    def get_type(self):
        return "User"


class ChatSettings(models.Model):
    countWarn = models.IntegerField(default=3)
    inviteMessage = models.CharField(default="", max_length=4096)
    adds = models.BooleanField(default=True)


class Actions(models.Model):
    user = models.ForeignKey('ChatUser', on_delete=models.CASCADE, null=True)
    action = models.CharField(default="", max_length=100)
    date = models.DateTimeField(default=datetime.now)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="actions")


class Chat(models.Model):
    id = models.BigIntegerField(default=0, primary_key=True)
    perms = models.ForeignKey('Permission', on_delete=models.CASCADE)
    settings = models.ForeignKey('ChatSettings', on_delete=models.CASCADE)
    worked = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id)


class ChatBot(models.Model):
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, related_name="bots")
    status = models.IntegerField(default=0)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="bots")
    invite_by = models.ForeignKey('ChatUser', on_delete=models.CASCADE, default="", null=True, related_name="invited_bots")
    leaved = models.BooleanField(default=False)
    reg_date = models.DateTimeField(default=datetime.now)
    kicked = models.BooleanField(default=False)
    def equial(self, data):
        if type(data) == type(self):
            return self.id == data.id
        return False
    def get_id(self):
        return self.bot.id
    def get_type(self):
        return "bot"
    def getStatus(self):
        return self.status
    def __str__(self):
        return str(self.bot)


class Bot(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)
    verifery = models.BooleanField(default=False)
    name = models.CharField(default="", max_length=40)
    def __str__(self):
        if self.name == "":
            return "@club{id}".format(
                id = self.id,
            )
        else:
            return "[club{id}|{name}]".format(
                id = self.id,
                name = self.name
            )
    
"""
class QueryBrak(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user1 = models.ForeignKey('User', on_delete=models.CASCADE, related_name="braks")
    user2 = models.ForeignKey('User', on_delete=models.CASCADE, related_name="braks")
    accepted = models.BooleanField(default=False)
    date = models.DateField(default=datetime.now)
    def accept(self, user):
        if self.accepted == False:
            if user == self.user2:
                self.accepted = True
                self.date = datetime.now()
                self.save()
                return True
        return False
    def deny(self, user):
        if (user == self.user1) or (user == self.user2):
            self.delete()
"""