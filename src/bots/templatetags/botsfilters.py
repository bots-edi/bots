# -*- coding: utf-8 -*-

import os
from django import template

register = template.Library()


@register.filter
def shortpath(path):
    if path:
        terug = os.path.basename(path)
        if terug:
            return terug
        else:
            return "(file)"  # for soem cases there is no good filename.....
    return ""
