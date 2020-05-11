from .models import *
import vk
from django.conf import settings as DjangoSettings


# Function for check Access for function
def checkAccess(user, peer_id, nameAccess):
    chat = peer_id.perms.getAccess(nameAccess)
    u = user.getStatus()
    return {
        'flag': bool(chat <= u),
        'chat': chat,
        'user': u,
    }

# Function for find 
def get_peer_id(peer_id):
    try:
        peer_id = Chat.objects.get(id=peer_id)
    except:
        perms = Permission.objects.create()
        settings = ChatSettings.objects.create()
        peer_id = Chat.objects.create(
            id=peer_id,
            perms=perms,
            settings=settings,
        )
    return peer_id

def get_user(user, peer_id, here=False):
    if (user>0):
        try:
            user = peer_id.users.get(user__id=user)
        except:
            try:
                
                tmp = User.objects.get(id=user)
            except:
                tmp = User.objects.create(id=user)
            user = ChatUser.objects.create(
                user=tmp,
                chat=peer_id,
                kicked=(here == False)
                )
            peer_id.users.add(user)
            peer_id.save()
        return user
    else:
        try:
            user = peer_id.bots.get(bot_id = -user)
        except:
            try:
                user = Bot.objects.get(id=-user)
            except:
                user = Bot.objects.create(id=-user)
            user = ChatBot.objects.create(
                bot=user,
                chat=peer_id,
                kicked=(here == False)
                )
            peer_id.save()
        return user

# Function of find description of error
def fixError(e):
    s = "Error"
    spisok = []
    try:
        spisok += [
            ("Description: ", e.args,)
        ]
    except:
        pass
    try:
        spisok += [
            ("Line #",e.__traceback__.tb_lineno,)
        ]
    except:
        pass
    try:
        spisok += [
            ("Directory: ",e.__traceback__.tb_frame.f_code.co_filename,)
        ]
    except:
        pass
    s = "Error"
    for _ in spisok:
        s += "\n  {}{}".format(_[0],_[1])
    return s

