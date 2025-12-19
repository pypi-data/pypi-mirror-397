from django import template

from .greeting import greeting
from .shout import shout
from .show_today_timestamp import show_today_timestamp
from .simple_alert import simple_alert

register = template.Library()

# 1. simple_tags
register.simple_tag(show_today_timestamp)
register.simple_tag(greeting)

# 2. simple_block_tags
register.simple_block_tag(shout)
register.simple_block_tag(simple_alert)
