from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from datetime import datetime, date, timezone, timedelta
from django.core.validators import RegexValidator
import os

