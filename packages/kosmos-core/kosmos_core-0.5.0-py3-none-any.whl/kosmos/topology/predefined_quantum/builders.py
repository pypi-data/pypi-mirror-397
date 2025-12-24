from abc import ABC, abstractmethod

from kosmos.topology.link import LinkId, QuantumLink
from kosmos.topology.net import Network
from kosmos.topology.node import NodeId, NodeRole, QuantumNode

DEFAULT_COHERENCE_TIME: float = 1.0
DEFAULT_DISTANCE: float = 1.0
DEFAULT_ATTENUATION: float = 0.0
DEFAULT_SIGNAL_SPEED: float = 2e-4
DEFAULT_REPETITION_RATE: float = 1e6


def _default_node(i: int, role: NodeRole, num_qubits: int) -> QuantumNode:
    """Create a default quantum node for predefined quantum topologies.

    Args:
        i (int): Index to convert to a NodeId.
        role (NodeRole): Assigned role of the node.
        num_qubits (int): Number of qubits for the node.

    Returns:
        QuantumNode: Quantum node instance.

    """
    return QuantumNode(
        id=NodeId(str(i)),
        roles=[role],
        num_qubits=num_qubits,
        coherence_time=DEFAULT_COHERENCE_TIME,
    )


def _default_link(src: QuantumNode, dst: QuantumNode) -> QuantumLink:
    """Create a default quantum link for predefined quantum topologies.

    Args:
        src (QuantumNode): Source node.
        dst (QuantumNode): Destination node.

    Returns:
        QuantumLink: Quantum link instance.

    """
    return QuantumLink(
        id=LinkId(f"{src.id.value}-{dst.id.value}"),
        src=src,
        dst=dst,
        distance=DEFAULT_DISTANCE,
        attenuation=DEFAULT_ATTENUATION,
        signal_speed=DEFAULT_SIGNAL_SPEED,
        repetition_rate=DEFAULT_REPETITION_RATE,
    )


class PredefinedQuantumTopology(ABC):
    """Abstract base class for predefined quantum topologies."""

    @abstractmethod
    def build(self) -> Network:
        """Construct the topology and return a Network instance.

        Returns:
            Network: Constructed network instance.

        """


class LineTopology(PredefinedQuantumTopology):
    """Line quantum topology."""

    def __init__(self, num_nodes: int, num_qubits: int) -> None:
        """Initialize the line quantum topology.

        Args:
            num_nodes (int): Number of nodes (must be >= 2).
            num_qubits (int): Number of qubits for the node.

        """
        min_num_nodes = 2
        if num_nodes < min_num_nodes:
            msg = "Line topology requires at least 2 nodes."
            raise ValueError(msg)

        self.num_nodes = num_nodes
        self.num_qubits = num_qubits

    def build(self) -> Network:
        """Build the line quantum topology.

        Returns:
            Network: Network with nodes connected in a linear chain.

        """
        network = Network()

        # endpoints = END_USER, inner nodes = REPEATER
        nodes: list[QuantumNode] = []
        for i in range(self.num_nodes):
            role = NodeRole.END_USER if i == 0 or i == self.num_nodes - 1 else NodeRole.REPEATER
            node = _default_node(i, role, self.num_qubits)
            network.add_node(node)
            nodes.append(node)

        # Create links between consecutive nodes
        for i in range(self.num_nodes - 1):
            link = _default_link(nodes[i], nodes[i + 1])
            network.add_link(link)

        return network


class RingTopology(PredefinedQuantumTopology):
    """Ring quantum topology."""

    def __init__(self, num_nodes: int, num_qubits: int) -> None:
        """Initialize the ring quantum topology.

        Args:
            num_nodes (int): Number of nodes (must be >= 3).
            num_qubits (int): Number of qubits for the node.

        """
        min_num_nodes = 3
        if num_nodes < min_num_nodes:
            msg = "Ring topology requires at least 3 nodes."
            raise ValueError(msg)
        self.num_nodes = num_nodes
        self.num_qubits = num_qubits

    def build(self) -> Network:
        """Build the ring quantum topology.

        Returns:
            Network: Network forming a closed cycle.

        """
        network = Network()

        # All nodes in a ring are ROUTERs.
        nodes: list = []
        for i in range(self.num_nodes):
            node = _default_node(i, NodeRole.ROUTER, self.num_qubits)
            network.add_node(node)
            nodes.append(node)

        for i in range(self.num_nodes):
            src = nodes[i]
            dst = nodes[(i + 1) % self.num_nodes]
            link = _default_link(src, dst)
            network.add_link(link)

        return network


class StarTopology(PredefinedQuantumTopology):
    """Star quantum topology."""

    def __init__(self, num_nodes: int, num_qubits: int) -> None:
        """Initialize the star quantum topology.

        Args:
            num_nodes (int): Number of nodes (must be >= 2).
            num_qubits (int): Number of qubits for the node.

        """
        min_num_nodes = 2
        if num_nodes < min_num_nodes:
            msg = "Star topology requires at least 2 nodes."
            raise ValueError(msg)
        self.num_nodes = num_nodes
        self.num_qubits = num_qubits

    def build(self) -> Network:
        """Build the star quantum topology.

        Returns:
            Network: Network with one central node and all other nodes connected to the center.

        """
        network = Network()

        # The center node is a ROUTER, all other nodes are END_USERS
        nodes: list = []
        node_center = _default_node(0, NodeRole.ROUTER, self.num_qubits)
        network.add_node(node_center)
        nodes.append(node_center)
        for i in range(1, self.num_nodes):
            node = _default_node(i, NodeRole.END_USER, self.num_qubits)
            network.add_node(node)
            nodes.append(node)
        for i in range(1, self.num_nodes):
            link = _default_link(nodes[0], nodes[i])
            network.add_link(link)
        return network
