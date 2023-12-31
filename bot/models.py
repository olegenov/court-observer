from django.db import models


class Entity(models.Model):
    name = models.CharField(verbose_name="Name", max_length=64, unique=True)

    def __str__(self):
        return self.name


class Observation(models.Model):
    tg = models.IntegerField(verbose_name="Telegram id")
    entity = models.ForeignKey(
        verbose_name="Name",
        to=Entity,
        on_delete=models.CASCADE,
        related_name="observations",
    )


class Case(models.Model):
    number = models.CharField(verbose_name="Number", max_length=64)
    entity = models.ForeignKey(verbose_name="Name",
        to=Entity,
        on_delete=models.CASCADE,
        related_name="cases",
    )
    court = models.CharField(max_length=40, verbose_name="Court", null=True, blank=True)
    link = models.CharField(verbose_name="Name", max_length=200)

    def as_dict(self):
        return {'entity': self.entity.name, 'court': self.court, 'number': self.number, 'link': self.link}
