from graphmix.chemistry.units import Volume
from graphmix.graph.solution import Solution
from graphmix.location import Location


class Node(Solution, Location):
    final_volume: Volume
    initial_volume: Volume = Volume(0, "mL")
