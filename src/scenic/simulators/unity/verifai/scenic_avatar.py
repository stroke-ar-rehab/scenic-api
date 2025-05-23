from verifai.samplers import *
from verifai.falsifier import *
from verifai.monitor import specification_monitor, mtl_specification
from dotmap import DotMap
from verifai.scenic_server import ScenicServer
import os

# From current path of this file, look for the scenic file
current_dir = os.path.dirname(os.path.abspath(__file__))
target_script = os.path.join(current_dir, '../../../../../../../program_synthesis/scenic_output/',
                             'exercise2.scenic')

path_to_scenic_script = target_script
sampler = ScenicSampler.fromScenario(path_to_scenic_script)

MAX_ITERS = 1
PORT = 8888
MAXREQS = 5
BUFSIZE = 4096

# Setting up Falsifiers
falsifier_params = DotMap(
    n_iters=MAX_ITERS,
    save_error_table=False,
    save_good_samples=True,
    verbosity=1
)
server_options = DotMap(
    bufsize=BUFSIZE,
    maxreqs=MAXREQS,
    verbosity=1
)


class MyMonitor(specification_monitor):
    def __init__(self):
        self.specification = mtl_specification(['G safe'])
        super().__init__(self.specification)

    def evaluate(self, simulation):
        # rightElbow = []
        # leftElbow = []
        # angles = simulation.result.records['angles']

        # for i, jointAngle in angles:
        #     if jointAngle:
        #         rightElbow.append(float(jointAngle.rightElbow))
        #         leftElbow.append(float(jointAngle.leftElbow))

        # jointDict = {
        #     'rElbow > 130' : any(angle > 130 for angle in rightElbow),
        #     'lElbow > 130' : any(angle > 130 for angle in leftElbow)
        #     }

        # print('\n',jointDict, '\n')

        # print(simulation.result.records)
        eval_dictionary = {'safe': list(enumerate([0, 1, 3]))}
        # Evaluate MTL formula given values for its atomic propositions
        return self.specification.evaluate(eval_dictionary)


falsifier = generic_falsifier(sampler=sampler,
                              monitor=MyMonitor(),
                              falsifier_params=falsifier_params,
                              server_class=ScenicServer,
                              server_options=server_options)

falsifier.run_falsifier()
print('Safe table:')
print(falsifier.safe_table.table)
