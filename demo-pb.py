#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pushbullet import Pushbullet

pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')

# push = pb.push_note("This is the title", "This is the body")
# print(pb.devices)

one_plus_one = pb.get_device('OnePlus One')

push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!", "We're using the api.", device=one_plus_one)
