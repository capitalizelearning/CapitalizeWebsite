from django.contrib import admin

from .models import (Class, Enrollment, Institution, Preferences, Profile,
                     WaitingList)

admin.site.register(Class)
admin.site.register(Profile)
admin.site.register(Enrollment)
admin.site.register(Institution)
admin.site.register(Preferences)
admin.site.register(WaitingList)
