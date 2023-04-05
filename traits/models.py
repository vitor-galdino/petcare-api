from django.db import models


class Trait(models.Model):
    name = models.CharField(max_length=20, unique=True)
    pets = models.ManyToManyField('pets.Pet', related_name='traits')
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self) -> str:
        return f'<[{self.id}] Trait - {self.name}>'
