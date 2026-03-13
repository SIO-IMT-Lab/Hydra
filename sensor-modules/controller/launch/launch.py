from core.launch import launch
from nodes.apc import APC
from nodes.conductivity import Conductivity
from nodes.recorder import Recorder
from nodes.sita import SITA


def main(args=None):
    nodes = [
        APC(),
        Conductivity(),
        Recorder(),
        # SITA()
    ]
    
    launch(nodes)

if __name__ == '__main__':
    main()
