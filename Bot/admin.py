from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(Permission)
admin.site.register(ChatUser)
admin.site.register(ChatSettings)
admin.site.register(Actions)
admin.site.register(Chat)
admin.site.register(Bot)
admin.site.register(ChatBot)
admin.site.register(SysConfig)
admin.site.register(Experience)
admin.site.register(Money)
admin.site.register(InventoryItem)
admin.site.register(Item)
admin.site.register(ItemParameter)
admin.site.register(Boost)