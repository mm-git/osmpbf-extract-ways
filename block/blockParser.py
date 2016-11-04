from imposm.parser.pbf.parser import read_blob_data
from imposm.parser.pbf import OSMPBF
import numpy as np


class BlockParser:
    def __init__(self, filename, blob_pos, blob_size):
        self.pos = filename, blob_pos, blob_size
        data = read_blob_data(filename, blob_pos, blob_size)
        self.primitive_block = OSMPBF.PrimitiveBlock()
        self.primitive_block.ParseFromString(data)
        self.primitive_group = self.primitive_block.primitivegroup
        self.string_table = self.primitive_block.stringtable.s
        self.highway_index = self.get_string_table_index('highway')
        self.number_index = self.get_string_table_index('ref')
        self.name_index = self.get_string_table_index('name')

    def get_string_table_index(self, tag):
        try:
            return self.string_table.index(tag)
        except ValueError:
            return None

    def count_nodes(self):
        count = 0
        for group in self.primitive_group:
            if group.dense:
                ids = group.dense.id
                count += len(ids)
        return count

    def get_node_end_id(self):
        last_dense = None
        for group in self.primitive_group:
            if group.dense:
                last_dense = group.dense

        if last_dense:
            return np.sum(np.array(last_dense.id))

        return 0

    def count_ways(self):
        count = 0
        for group in self.primitive_group:
            if group.ways:
                ways = group.ways
                count += len(ways)
        return count

    def get_way_end_id(self):
        last_ways = None
        for group in self.primitive_group:
            if group.ways:
                last_ways = group.ways

        if last_ways:
            return last_ways[-1].id

        return 0

    def nodes(self):
        nodes_id_list = []
        nodes_lng_lat_list = []
        for group  in self.primitive_group:
            dense = group.dense
            if dense:
                ids = dense.id
                lons = dense.lon
                lats = dense.lat
                last_id = 0
                last_lon = 0
                last_lat = 0
                for i in xrange(len(ids)):
                    last_id += ids[i]
                    last_lon += lons[i]
                    last_lat += lats[i]
                    nodes_id_list.append(last_id)
                    nodes_lng_lat_list.append((last_lon, last_lat))
        return nodes_id_list, np.array(nodes_lng_lat_list)

    def ways_only_highway(self):
        if self.highway_index is not None:
            for group in self.primitive_group:
                ways = group.ways
                if ways:
                    for way in ways:

                        if self.highway_index in way.keys:
                            delta_refs = way.refs
                            refs = []
                            ref = 0
                            for delta in delta_refs:
                                ref += delta
                                refs.append(ref)
                            yield (way.id, refs)

    def ways_only_highway_with_name(self):
        if self.highway_index is not None:
            for group in self.primitive_group:
                ways = group.ways
                if ways:
                    for way in ways:
                        keys = way.keys
                        values = way.vals

                        highway = self.get_key_value(keys, values, self.highway_index)
                        if highway != '':
                            name = self.get_key_value(keys, values, self.name_index)
                            number = self.get_key_value(keys, values, self.number_index)

                            delta_refs = way.refs
                            refs = []
                            ref = 0
                            for delta in delta_refs:
                                ref += delta
                                refs.append(ref)
                            yield (way.id, highway, name, number, refs)

    def get_key_value(self, keys, values, key_index):
        if key_index is None:
            return ''

        try:
            index = keys.index(key_index)
            return self.string_table[values[index]]
        except ValueError:
            return ''
