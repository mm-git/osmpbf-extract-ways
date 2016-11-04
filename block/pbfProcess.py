import multiprocessing
from imposm.parser.pbf.parser import PBFFile
from blockParser import BlockParser
from nodeCountParserProcess import NodeCountParserProcess


class PbfProcess(multiprocessing.Process):
    def __init__(self, pbf_file_name, process_count, count_queue):
        multiprocessing.Process.__init__(self)
        self.daemon = False
        self.pbf_file_name = pbf_file_name
        self.process_count = process_count
        self.count_queue = count_queue

    def run(self):
        block_queue = multiprocessing.JoinableQueue(32)
        node_counter_pool = []
        for _ in xrange(self.process_count):
            node_counter_process = NodeCountParserProcess(
                self.pbf_file_name,
                self.count_queue,
                block_queue
            )
            node_counter_pool.append(node_counter_process)
            node_counter_process.start()

        pbf = PBFFile(self.pbf_file_name)
        for block in pbf.blob_offsets():
            block_queue.put(block)

        block_queue.join()

        for _ in xrange(len(node_counter_pool)):
            block_queue.put(None)
        for node_counter_process in node_counter_pool:
            node_counter_process.join()

