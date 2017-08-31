#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -

import tsensor

class dib(object):
    pass

dib = dib()

from transitions import Machine
states = ['off', 'initial_power', 'pause', 'low_power', 'heads_power', 'body_power', 'tail_power', 'finish', 'force_finish']
transitions = [
['start', 'off', 'initial_power'],
['t_pause', '*', 'pause'],
['t_body', 'heads_power', 'body_power'],
['t_finish', 'tail_power', 'finish']
]

machine = Machine(model=dib, states=states, transitions=transitions, initial='off')

t1 = tsensor.Tsensor()

cnt = 0
T = 0

