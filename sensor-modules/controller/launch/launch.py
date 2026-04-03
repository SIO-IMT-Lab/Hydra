from core.launch import launch
from core.utils import load_config
from nodes.apc import APC
from nodes.conductivity import Conductivity
from nodes.recorder import Recorder
from nodes.sita import SITA


def main(args=None):
    config = load_config("config/nodes.yaml")
    nodes = [
        APC(config),
        Conductivity(config),
        Recorder(config),
        # SITA(config)
    ]    
    launch(nodes)

if __name__ == '__main__':
    main()
