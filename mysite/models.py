from django.db import models
import django.utils.timezone as timezone

class Search(models.Model):
    id = models.AutoField(primary_key=True)
    search_date = models.DateTimeField('查詢時間',default = timezone.now)
    project_id=models.TextField(verbose_name = "項目名稱")
    country_id=models.TextField(verbose_name = "國家名稱")

    def __str__(self):
        return self.name



