import multiprocessing
from blockParser import BlockParser


class NodeCountParserProcess(multiprocessing.Process):
    def __init__(self, pbf_file_name, count_queue, block_queue):
        multiprocessing.Process.__init__(self)
        self.daemon = True
        self.pbf_file_name = pbf_file_name
        self.count_queue = count_queue
        self.block_queue = block_queue

    def run(self):
        while True:
            node_block = self.block_queue.get()
            if node_block is None:
                self.block_queue.task_done()
                break
            blob_pos = node_block['blob_pos']
            blob_size = node_block['blob_size']
            block_parser = BlockParser(self.pbf_file_name, blob_pos, blob_size)

            node_count = block_parser.count_nodes()
            if node_count > 0:
                self.count_queue.put((0, blob_pos, blob_size, node_count))

            way_count = block_parser.count_ways()
            if way_count > 0:
                self.count_queue.put((1, blob_pos, blob_size, way_count))

            self.block_queue.task_done()

        self.count_queue.put(None)