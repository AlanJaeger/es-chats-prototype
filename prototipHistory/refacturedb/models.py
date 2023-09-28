from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils import timezone

# Create your models here.
class BaseSoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(_("is deleted?"), default=False)

    class Meta:
        abstract = True

    def deleted_sufix(self):
        name_sufix = "_is_deleted_"
        return name_sufix

    def delete(self):
        self.is_deleted = True
        self.name += self.deleted_sufix()
        self.save()


class BaseConfigurableModel(models.Model):
    config = models.JSONField(_("config"), blank=True, null=True)

    class Meta:
        abstract = True

class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_on = models.DateTimeField(
        _("Created on"), editable=False, auto_now_add=True
    )
    modified_on = models.DateTimeField(_("Modified on"), auto_now=True)

    class Meta:
        abstract = True

    @property
    def edited(self) -> bool:
        return bool(self.modified_by)


class Project(BaseConfigurableModel, BaseModel):
    DATE_FORMAT_DAY_FIRST = "D"
    DATE_FORMAT_MONTH_FIRST = "M"
    DATE_FORMATS = (
        (DATE_FORMAT_DAY_FIRST, "DD-MM-YYYY"),
        (DATE_FORMAT_MONTH_FIRST, "MM-DD-YYYY"),
    )

    name = models.CharField(_("name"), max_length=50)
    flows_authorization = models.CharField(
        _("Flows Authorization Token"), max_length=50, null=True, blank=True
    )
    date_format = models.CharField(
        verbose_name=_("Date Format"),
        max_length=1,
        choices=DATE_FORMATS,
        default=DATE_FORMAT_DAY_FIRST,
        help_text=_("Whether day comes first or month comes first in dates"),
    )
    is_template = models.BooleanField(_("is template?"), default=False)

    def __str__(self):
        return self.name
    
class Sector(BaseSoftDeleteModel, BaseConfigurableModel, BaseModel):
    name = models.CharField(_("name"), max_length=120)
    project = models.ForeignKey(
        "refacturedb.Project",
        verbose_name=_("Project"),
        related_name="sectors",
        on_delete=models.CASCADE,
    )
    rooms_limit = models.PositiveIntegerField(_("Rooms limit per employee"))
    work_start = models.TimeField(_("work start"), auto_now=False, auto_now_add=False)
    work_end = models.TimeField(_("work end"), auto_now=False, auto_now_add=False)
    can_trigger_flows = models.BooleanField(
        _("Can trigger flows?"),
        help_text=_(
            "Is it possible to trigger flows(weni flows integration) from this sector?"
        ),
        default=False,
    )
    sign_messages = models.BooleanField(_("Sign messages?"), default=False)
    is_deleted = models.BooleanField(_("is deleted?"), default=False)
    open_offline = models.BooleanField(
        _("Open room when all agents are offline?"), default=True
    )
    can_edit_custom_fields = models.BooleanField(
        _("Can edit custom fields?"), default=False
    )

class Queue(BaseSoftDeleteModel, BaseConfigurableModel, BaseModel):
    sector = models.ForeignKey(
        "refacturedb.Sector",
        verbose_name=_("sector"),
        related_name="queues",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("Name"), max_length=150, blank=True)
    default_message = models.TextField(
        _("Default queue message"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Sector Queue")
        verbose_name_plural = _("Sector Queues")

        constraints = [
            models.UniqueConstraint(fields=["sector", "name"], name="unique_queue_name")
        ]

    def __str__(self):
        return self.name

class Contact(BaseModel):
    external_id = models.CharField(
        _("External ID"), max_length=200, blank=True, null=True
    )
    name = models.CharField(_("first name"), max_length=200, blank=True)
    email = models.EmailField(
        _("email"), unique=False, help_text=_("Contact email"), blank=True, null=True
    )
    status = models.CharField(_("status"), max_length=30, blank=True)
    phone = models.CharField(_("phone"), max_length=30, blank=True)

    custom_fields = models.JSONField(
        _("custom fields"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self):
        return str(self.name)
    
class Room(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_is_active = self.is_active

    user = models.ForeignKey(
        "refacturedb.User",
        related_name="rooms",
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        "refacturedb.Contact",
        related_name="rooms",
        verbose_name=_("contact"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    queue = models.ForeignKey(
        "refacturedb.Queue",
        related_name="rooms",
        verbose_name=_("Queue"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    custom_fields = models.JSONField(
        _("custom fields"),
        blank=True,
        null=True,
    )
    urn = models.CharField(_("urn"), null=True, blank=True, max_length=100, default="")

    callback_url = models.TextField(_("Callback URL"), null=True, blank=True)

    ended_at = models.DateTimeField(
        _("Ended at"), auto_now_add=False, null=True, blank=True
    )

    ended_by = models.CharField(_("Ended by"), max_length=50, null=True, blank=True)

    is_active = models.BooleanField(_("is active?"), default=True)
    is_waiting = models.BooleanField(_("is waiting for answer?"), default=False)

    transfer_history = models.JSONField(_("Transfer History"), null=True, blank=True)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email"), unique=True, help_text=_("User email"))

    photo_url = models.TextField(blank=True, null=True)

    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)

    language = models.CharField(max_length=5, null=True, blank=True)

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

class Message(BaseModel):
    room = models.ForeignKey(
        "refacturedb.Room",
        related_name="messages",
        verbose_name=_("room"),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "refacturedb.User",
        related_name="messages",
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        "refacturedb.Contact",
        related_name="messages",
        verbose_name=_("contact"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    text = models.TextField(_("Text"), blank=True, null=True)
    seen = models.BooleanField(_("Was it seen?"), default=False)

class RoomText(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_is_active = self.is_active

    user = models.ForeignKey(
        "refacturedb.User",
        related_name="roomss",
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        "refacturedb.Contact",
        related_name="roomss",
        verbose_name=_("contact"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    queue = models.ForeignKey(
        "refacturedb.Queue",
        related_name="roomss",
        verbose_name=_("Queue"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    custom_fields = models.JSONField(
        _("custom fields"),
        blank=True,
        null=True,
    )
    urn = models.CharField(_("urn"), null=True, blank=True, max_length=100, default="")

    callback_url = models.TextField(_("Callback URL"), null=True, blank=True)

    ended_at = models.DateTimeField(
        _("Ended at"), auto_now_add=False, null=True, blank=True
    )

    ended_by = models.CharField(_("Ended by"), max_length=50, null=True, blank=True)

    is_active = models.BooleanField(_("is active?"), default=True)
    is_waiting = models.BooleanField(_("is waiting for answer?"), default=False)

    transfer_history = models.JSONField(_("Transfer History"), null=True, blank=True)

class MessageText(BaseModel):
    index = models.BooleanField(default=False)

    room = models.ForeignKey(
        "refacturedb.RoomText",
        related_name="messagess",
        verbose_name=_("room"),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "refacturedb.User",
        related_name="messagess",
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        "refacturedb.Contact",
        related_name="messagess",
        verbose_name=_("contact"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    text = models.TextField(_("Text"), blank=True, null=True)
    seen = models.BooleanField(_("Was it seen?"), default=False)