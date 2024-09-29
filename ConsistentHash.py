import hashlib
from bisect import bisect_right

class Node:
    def __init__(self, name):
        self.name = name
        self.data = {}

    def add_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)

    def remove_data(self, key):
        return self.data.pop(key, None)

    def __str__(self):
        return f"Node({self.name})"

class ConsistentHash:
    def __init__(self, virtual_nodes=1):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self.nodes = {}

    def add_node(self, node):
        for i in range(self.virtual_nodes):
            key = self.hash(f'{node.name}:{i}')
            self.ring[key] = node
            index = bisect_right(self.sorted_keys, key)
            self.sorted_keys.insert(index, key)
        self.nodes[node.name] = node
        self._redistribute_keys()

    def remove_node(self, node_name):
        if node_name in self.nodes:
            node = self.nodes.pop(node_name)
            keys_to_redistribute = list(node.data.keys())
            
            # Remove all virtual nodes for this node
            self.sorted_keys = [k for k in self.sorted_keys if self.ring[k].name != node_name]
            self.ring = {k: v for k, v in self.ring.items() if v.name != node_name}
            
            # Redistribute keys to the next node in the ring
            for key in keys_to_redistribute:
                next_node = self.get_node(key)
                value = node.remove_data(key)
                next_node.add_data(key, value)

    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self.hash(key)
        index = bisect_right(self.sorted_keys, hash_key) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[index]]

    def add_key_value(self, key, value):
        node = self.get_node(key)
        if node:
            node.add_data(key, value)
            return node
        return None

    def get_value(self, key):
        node = self.get_node(key)
        if node:
            return node.get_data(key)
        return None

    def _redistribute_keys(self):
        all_keys = []
        for node in self.nodes.values():
            all_keys.extend(list(node.data.items()))
            node.data.clear()
        for key, value in all_keys:
            self.add_key_value(key, value)

    def print_ring(self):
        for key in self.sorted_keys:
            print(f"{self.ring[key]}: {key}")

    def print_node_states(self):
        for node in self.nodes.values():
            print(f"{node}: {node.data}")

    @staticmethod
    def hash(key):
        return hashlib.md5(key.encode()).hexdigest()

# Example usage
if __name__ == "__main__":
    ch = ConsistentHash()

    # Add some nodes
    nodes = [Node("node1"), Node("node2"), Node("node3")]
    for node in nodes:
        ch.add_node(node)

    print("\nInitial ring:")
    ch.print_ring()

    # Add key-value pairs
    keys_values = [
        ("key1", "value1"),
        ("key2", "value2"),
        ("key3", "value3"),
        ("key4", "value4"),
        ("key5", "value5")
    ]

    print("\nInitial distribution:")
    for key, value in keys_values:
        node = ch.add_key_value(key, ConsistentHash.hash(key))
        print(f"Key '{key}' with hash '{ch.hash(key)}' is mapped to {node} ")

    ch.print_node_states()
    print("\nAdding node4")
    ch.add_node(Node("node4"))

    print("\nAfter addition ring:")
    ch.print_ring()

    print("\nAfter addition:")
    ch.print_node_states()

    print("\nRemoving node3")
    ch.remove_node("node3")

    print("\nAfter removal ring:")
    ch.print_ring()

    print("\nAfter removal:")
    ch.print_node_states()


    # Add a new key-value pair
    new_key, new_value = "key6", "value6"
    node = ch.add_key_value(new_key, ch.hash(new_key))
    print(f"\nAdded new key '{new_key}' with value '{ch.hash(key)}' to {node}")

    # Print final state of each node
    print("\nFinal state of nodes:")
    ch.print_node_states()
