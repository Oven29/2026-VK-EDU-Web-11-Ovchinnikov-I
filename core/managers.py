from django.db import models


class ProfileManager(models.Manager):
    def best(self):
        return self.select_related('user').order_by('-answer_cnt')[:10]
