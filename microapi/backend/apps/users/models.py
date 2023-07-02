from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinValueValidator

from core.abstract_models import AbstractBaseModel


class User(AbstractBaseModel):
    username = fields.CharField(max_length=32, unique=True, null=False, index=True)
    balance = fields.IntField(default=0, null=False, validators=[MinValueValidator(min_value=0)])
    xp = fields.IntField(default=0, null=False, validators=[MinValueValidator(min_value=0)])
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)

    def __str__(self):
        return self.username


User_Pydantic = pydantic_model_creator(User, name="User")
