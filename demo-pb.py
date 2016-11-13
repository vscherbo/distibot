#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pushbullet import Pushbullet

pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
c = [x for x in pb.channels if x.name == u"Billy's moonshine"][0]
c.push_note("Заголовок", "Сообщение")

# push = pb.push_note("This is the title", "This is the body")
# print(pb.devices)

# one_plus_one = pb.get_device('OnePlus One')
# push = one_plus_one.push_note("Процесс", "Тело.")


