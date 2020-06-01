from django.db import models
from datetime import datetime, timedelta
from django.db.models import Sum
from django.conf import settings as DjangoSettings
from django.utils import timezone


def now_plus_30days():
    return datetime.now() + timedelta(days=30)

class SysConfig(models.Model):
    param = models.CharField(default="", max_length=20)
    value = models.CharField(default="", max_length=20)
    _type = models.CharField(default="", max_length=3)


class User(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)
    reg_date = models.DateTimeField(default=datetime.now)
    status = models.IntegerField(default=0)
    tester = models.BooleanField(default=False)
    name = models.CharField(default="", blank=True, max_length=20)

    def __str__(self):
        if self.name == "":
            return "@id{id}".format(
                id=self.id,
            )
        return "[id{id}|{name}]".format(
            id=self.id,
            name=self.name,
        )


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
        return str(self.date) + " " + str(self.author)


class Permission(models.Model):
    kickAccess = models.IntegerField(default=10)  # 1
    unKickAccess = models.IntegerField(default=10)  # 2
    setStatusAccess = models.IntegerField(default=10)  # 3
    seeAllStatisticAccess = models.IntegerField(default=0)  # 4
    seeStatisticAccess = models.IntegerField(default=1)  # 5
    seeTopChatAccess = models.IntegerField(default=0)  # 6
    sendLinkAccess = models.IntegerField(default=0)  # 7
    getPermsAccess = models.IntegerField(default=10)  # 8
    sayAccess = models.IntegerField(default=0)  # 9
    setPermsAccess = models.IntegerField(default=10)  # 10
    getListStatusAccess = models.IntegerField(default=10)  # 11
    getActivityAccess = models.IntegerField(default=10)  # 12
    kickAuroListAccess = models.IntegerField(default=10)  # 13
    callAutoListAccess = models.IntegerField(default=10)  # 14
    changeInviteMessageAccess = models.IntegerField(default=10)  # 15
    getOnlineAccess = models.IntegerField(default=10)  # 16
    addFriendsAccess = models.IntegerField(default=0)  # 17
    sendSpamAccess = models.IntegerField(default=0)  # 18
    brakAccess = models.IntegerField(default=0)  # 19
    whoAccess = models.IntegerField(default=0)  # 20
    ignoreAccess = models.IntegerField(default=10)  # 21
    unLeaveAutoKickAccess = models.IntegerField(default=0)  # 22
    sendAllAccess = models.IntegerField(default=0)  # 23
    sendOnlineAccess = models.IntegerField(default=0)  # 24
    warnAccess = models.IntegerField(default=10)  # 25

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
            if number + 1 == id:
                return {
                    'flag': True,
                    'key': key
                }
        return {
            'flag': False
        }

    def setAccess(self, name, count):
        if count >= 0 and count <= 10:
            self.__setattr__(name, count)
            self.save()
            return True
        return False


class Boost(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="boosts")
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=now_plus_30days)
    value = models.IntegerField(default=1)


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
                id=self.user.id,
            )
        return "[id{id}|{name}]".format(
            id=self.user.id,
            name=self.name,
        )

    def get_id(self):
        return self.user.id

    def get_type(self):
        return "User"

    def add_exp(self, count):
        boosts = self.get_boosts() * self.chat.get_boosts()
        tmp = Experience.objects.create(user=self.user, count=int(count*boosts))
        tmp.save()
        return True

    def get_boosts(self):
        boosts = self.user.boosts.filter(end_date__gte=datetime.now())
        x = 1
        for _ in boosts:
            x *= _.value/100
        return x

    def rest_exp(self):
        try:
            _exp = self.user.exp.filter(date_gte=(datetime.today() - timedelta(hours=1))).aggregate(
                total=Sum('count', field="count")
            )['total']
            if _exp is None:
                _exp = 0
            boosts = self.get_boosts() * self.chat.get_boosts()
            return int(min(1000, self.chat.settings.limit_message*boosts - _exp))
        except:
            return 1000

    def activate_booster(self, value):
        if self.user.boosts.filter(end_date__gte=datetime.now()).count() < DjangoSettings.MAX_BOOST_USER:
            Boost.objects.create(
                user=self.user,
                value=value*100
            )
            return True
        return False

    def activate_booster_chat(self):
        if self.chat.boosts.filter(end_date__gte=datetime.now()).count() < DjangoSettings.MAX_BOOST_CHAT:
            BoostChat.objects.create(
                user=self.user,
                chat=self.chat
            )
            return True
        return False


class ChatSettings(models.Model):
    countWarn = models.IntegerField(default=3)
    inviteMessage = models.CharField(default="", max_length=4096)
    adds = models.BooleanField(default=True)
    limit_message = models.IntegerField(default=2000)
    premium = models.DateTimeField(default=datetime.now)


class Actions(models.Model):
    user = models.ForeignKey('ChatUser', on_delete=models.CASCADE, null=True)
    action = models.CharField(default="", max_length=100)
    date = models.DateTimeField(default=datetime.now)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="actions")


class BoostChat(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="boosts")
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=now_plus_30days)


class Chat(models.Model):
    id = models.BigIntegerField(default=0, primary_key=True)
    perms = models.ForeignKey('Permission', on_delete=models.CASCADE)
    settings = models.ForeignKey('ChatSettings', on_delete=models.CASCADE)
    worked = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    def get_boosts(self):
        boosts = self.boosts.filter(end_date__gte=datetime.now())
        x = 10
        if self.is_premium():
            for _ in boosts:
                x += 1
        return x/10

    def activate_premium(self):
        try:
            if self.settings.premium > timezone.now():
                self.settings.premium += timedelta(days=30)
                self.settings.save()
            else:
                self.settings.premium = timezone.now() + timedelta(days=30)
                self.settings.save()
            return True
        except:
            return False

    def is_premium(self):
        return self.settings.premium > datetime.now()


class ChatBot(models.Model):
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, related_name="bots")
    status = models.IntegerField(default=0)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name="bots")
    invite_by = models.ForeignKey('ChatUser', on_delete=models.CASCADE, default="", null=True,
                                  related_name="invited_bots")
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

    def add_exp(self, count):
        return True

    def rest_exp(self):
        return 100


class Bot(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)
    verifery = models.BooleanField(default=False)
    name = models.CharField(default="", max_length=40)

    def __str__(self):
        if self.name == "":
            return "@club{id}".format(
                id=self.id,
            )
        else:
            return "[club{id}|{name}]".format(
                id=self.id,
                name=self.name
            )


class Experience(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="exp")
    count = models.IntegerField(default=0)
    date = models.DateTimeField(default=datetime.now)


class Money(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="money")
    count = models.BigIntegerField(default="")
    date = models.DateTimeField(default=datetime.now)
    description = models.CharField(default="", max_length=100)


class InventoryItem(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name="invItems")
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="inv")
    uses = models.IntegerField(default=0)
    date = models.DateTimeField(default=datetime.now)


class Item(models.Model):
    _type = models.IntegerField(default=0)
    name = models.CharField(default="", max_length=15)
    action = models.CharField(default="", max_length=500)
    random_item = models.BooleanField(default=False)
    use = models.BooleanField(default=False)
    can_buy = models.BooleanField(default=False)
    price = models.IntegerField(default=0)

    def newItem(self, user):
        item = InventoryItem.objects.create(
            item=self,
            user=user
        )
        item.save()
        return item

    def __str__(self):
        return self.name.capitalize()


class ItemParameter(models.Model):
    name = models.CharField(default="", max_length=15)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name="params")
    value = models.CharField(default="", max_length=125)
    _type = models.CharField(default="str", max_length=4)
    description = models.CharField(default="", max_length=200)


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
