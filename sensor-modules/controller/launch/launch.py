from core.launch import launch
from core.utils import load_config
from nodes.apc import APC
from nodes.conductivity import Conductivity
from nodes.pdb_controller import PDB_Controller
from nodes.recorder import Recorder
from nodes.sita import SITA
from nodes.supervisor import Supervisor


def main(args=None):
    node_config = load_config("config/nodes.yaml")
    pdb_config = load_config("config/pdb_pins.yaml")
    
    nodes = [
        # APC(config),
        # Conductivity(node_config),
        PDB_Controller(node_config, pdb_config),
        # Recorder(node_config),
        # SITA(config)
        Supervisor(node_config, pdb_config)
    ]
    
    launch(nodes)

if __name__ == '__main__':
    main()
