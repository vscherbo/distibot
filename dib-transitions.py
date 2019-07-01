#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -

from transitions import Machine
# Set up logging
import logging
from transitions import logger
logger.setLevel(logging.INFO)
import distibot

class Dib(Machine):

    def __init__(self):
        self.t = 0  # state variable of the model
        self.conditions = {  # each state 
            'off': (0.0, 'start'),
            'pause': (75.0, 't_pause'),
            'body': (79.0, 't_body'),
            'finish': (94.5, 't_finish'),
        }

    def poll(self):
        global logger
        logger.info('t={0}, state={1}'.format(self.t, self.state))
        (t, trans) = self.conditions[self.state]
        if self.t >= t:
            eval('self.to_' + trans + '()')

dib = distibot.Distibot(emu_mode=True)
dib_model = Dib()


states = ['off', 'initial_power', 'pause', 'low_power', 'heads_power', 'body_power', 'tail_power', 'finish', 'force_finish']
transitions = [
['start', 'off', 'initial_power'],
['t_pause', '*', 'pause'],
['t_body', 'heads_power', 'body_power'],
['t_finish', 'tail_power', 'finish']
]

machine = Machine(model=dib_model, states=states, transitions=transitions, initial='off', queued=True)
# machine.add_transition('heat', '*', '*', conditions='is_step')

do_flag = True
while do_flag:
    dib.temperature_step()
    dib_model.t = dib.temperature_in_celsius
    dib_model.poll()
    do_flag = dib_model.state != 'finish'


