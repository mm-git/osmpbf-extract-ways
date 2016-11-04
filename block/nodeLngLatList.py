import numpy as np


class NodeLngLatList:
    ID_RANGE = 1024 * 1024

    def __init__(self):
        self.start_id = -1
        self.lat_lng_list = np.zeros(NodeLngLatList.ID_RANGE * 2, dtype=np.int32)

    def append_node(self, nodes):
        node_id_list = nodes[0]
        node_lng_lat_list = nodes[1]

        if self.start_id == -1:
            self.start_id = (node_id_list[0] // NodeLngLatList.ID_RANGE) * NodeLngLatList.ID_RANGE

        for i in xrange(len(node_id_list)):
            list_id = node_id_list[i] - self.start_id
            if list_id >= NodeLngLatList.ID_RANGE:
                return node_id_list[i:], node_lng_lat_list[i:]

            self.lat_lng_list[list_id * 2] = node_lng_lat_list[i][0]
            self.lat_lng_list[list_id * 2 + 1] = node_lng_lat_list[i][1]

        return [], []

    def get_lng_lat(self, node_id):
        list_id = node_id - self.start_id
        return self.lat_lng_list[list_id * 2], self.lat_lng_list[list_id * 2 + 1]
