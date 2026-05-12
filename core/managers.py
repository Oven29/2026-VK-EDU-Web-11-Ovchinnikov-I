from django.db import models


class ProfileManager(models.Manager):
    def best(self):
        return self.select_related('user').annotate(
            answers_count=models.Count('user__answers')
        ).order_by('-answers_count')[:10]
