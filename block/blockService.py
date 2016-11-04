import ConfigParser
import multiprocessing
import time

from imposm.parser.pbf.parser import PBFFile

from blockList import BlockList
from blockParser import BlockParser
from wayList import WayList
from nodeLngLatList import NodeLngLatList
from nodeParserProcess import NodeParserProcess
from pbfProcess import PbfProcess


class BlockService:
    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        conf.read('./way.conf')

        self.pbf_file_name = conf.get('pbf', 'file')
        self.node_process = int(conf.get('pbf', 'node_process'))
        self.node_block_list = BlockList('node')
        self.way_block_list = BlockList('way')
        self.node_lng_lat_list = None
        self.way_list = WayList()

    def create_block_list(self):
        count_queue = multiprocessing.JoinableQueue(32)
        pbf_process = PbfProcess(self.pbf_file_name, self.node_process, count_queue)
        pbf_process.start()

        finish_count = self.node_process
        while True:
            count = count_queue.get()
            if count is None:
                finish_count -= 1
                if finish_count == 0:
                    break
            else:
                self.append_count(count)

        pbf_process.join()

        self.node_block_list.sort()
        self.way_block_list.sort()

    def append_count(self, count):
        if count[0] == 0:
            self.node_block_list.add_block(count[1], count[2], count[3])
            print "node", count[1], count[2], count[3]
        elif count[0] == 1:
            self.way_block_list.add_block(count[1], count[2], count[3])
            print "way", count[1], count[2], count[3]

    def create_block_list_fast(self):
        pbf = PBFFile(self.pbf_file_name)
        block_list = list(pbf.blob_offsets())
        block_length = len(block_list)

        left = 0
        right = block_length - 1
        way_start_index = 0
        node_end_index = 0
        while left <= right:
            center = (right + left) / 2

            blob_pos = block_list[center]['blob_pos']
            blob_size = block_list[center]['blob_size']
            block_parser = BlockParser(self.pbf_file_name, blob_pos, blob_size)
            node_count = block_parser.count_nodes()
            way_count = block_parser.count_ways()

            if way_count > 0:
                way_start_index = center
                right = center - 1
            if node_count > 0:
                node_end_index = center
                left = center + 1
            if node_count > 0 and way_count > 0:
                break

        print 'way start', way_start_index

        for i in xrange(node_end_index + 1):
            blob_pos = block_list[i]['blob_pos']
            blob_size = block_list[i]['blob_size']
            self.node_block_list.add_block(blob_pos, blob_size, 0)

        for i in xrange(way_start_index, block_length):
            blob_pos = block_list[i]['blob_pos']
            blob_size = block_list[i]['blob_size']
            self.way_block_list.add_block(blob_pos, blob_size, 0)

    def create_node_lng_lat_list(self):
        last_node_block = self.node_block_list.block_list[-1]
        block_parser = BlockParser(self.pbf_file_name, last_node_block[0], last_node_block[1])
        node_end_id = block_parser.get_node_end_id()
        self.node_lng_lat_list = [None] * (node_end_id // NodeLngLatList.ID_RANGE + 1)

        nodes_queue = multiprocessing.JoinableQueue(32)
        node_parser_pool = []

        for i in xrange(self.node_process):
            node_block_list = list(self.node_block_list.blocks_with_skip(i, self.node_process))
            node_parser_process = NodeParserProcess(
                self.pbf_file_name,
                nodes_queue,
                node_block_list
            )
            node_parser_pool.append(node_parser_process)
            node_parser_process.start()

        finish_count = self.node_process
        while True:
            nodes = nodes_queue.get()
            if nodes is None:
                finish_count -= 1
                if finish_count == 0:
                    break
            else:
                self.append_node(nodes)

        for node_parser_process in node_parser_pool:
            node_parser_process.join()

    def append_node(self, nodes):
        while len(nodes[0]) > 0:
            start_id = nodes[0][0] // NodeLngLatList.ID_RANGE
            if self.node_lng_lat_list[start_id] is None:
                self.node_lng_lat_list[start_id] = NodeLngLatList()
                print 'node_lat_lng_list', start_id
            nodes = self.node_lng_lat_list[start_id].append_node(nodes)

    def get_lng_lat(self, node_id):
        start_id = node_id // NodeLngLatList.ID_RANGE

        try:
            return self.node_lng_lat_list[start_id].get_lng_lat(node_id)
        except:
            return 0, 0

    def ways(self):
        way_total = self.way_block_list.get_total_block()
        count = 0
        start = time.time()
        for way_block in self.way_block_list.blocks():
            block_parser = BlockParser(self.pbf_file_name, way_block[0], way_block[1])
            for way in block_parser.ways_only_highway_with_name():
                line = []
                for node_id in way[4]:
                    line.append(self.get_lng_lat(node_id))

                yield way[0], way[1], way[2], way[3], line

            count += 1
            passed = time.time() - start
            estimate = way_total * passed / count - passed
            print count, '/', way_total, passed, estimate

    def store_ways_to_file(self):
        for way in self.ways():
            self.way_list.add_way(way)
        self.way_list.write_way_list()

    def check_offset(self):
        for pos in self.node_block_list.blocks():
            blob_pos = pos[0]
            blob_size = pos[1]

            blob = BlockParser(self.pbf_file_name, blob_pos, blob_size)
            if (blob.primitive_block.granularity != 100 and blob.primitive_block.granularity is not None) or \
               blob.primitive_block.lat_offset is not None or\
               blob.primitive_block.lon_offset is not None:
                print blob.primitive_block.granularity, blob.primitive_block.lat_offset, blob.primitive_block.lon_offset
            else:
                print 'OK', blob_pos, blob_size
