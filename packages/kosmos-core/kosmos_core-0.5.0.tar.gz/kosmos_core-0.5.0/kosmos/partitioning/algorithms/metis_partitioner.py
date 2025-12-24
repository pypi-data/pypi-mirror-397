from typing import override

import pymetis
from qiskit import QuantumCircuit

from kosmos.partitioning.algorithms.partitioning_algorithm import PartitioningAlgorithm
from kosmos.partitioning.graph import Graph


class METISPartitioner(PartitioningAlgorithm):
    """Graph-based partitioning using METIS."""

    @override
    def partition(self, circuit: Graph | QuantumCircuit) -> dict[int, int]:
        """Compute a partitioning for the given circuit.

        Args:
            circuit (Graph | QuantumCircuit): Circuit to partition.

        Returns:
            dict[int, int]: A mapping from each node index to the partition identifier it is
                assigned to.

        """
        graph = self._to_graph(circuit)
        adjacency = graph.to_adjacency_list()
        if not adjacency or self.num_partitions > len(adjacency):
            return dict.fromkeys(range(len(adjacency)), 0)

        num_parts = self.num_partitions
        _, membership = pymetis.part_graph(num_parts, adjacency=adjacency)

        return dict(enumerate(membership))
