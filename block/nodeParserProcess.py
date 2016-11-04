import multiprocessing
from blockParser import BlockParser


class NodeParserProcess(multiprocessing.Process):
    def __init__(self, pbf_file_name, nodes_queue, node_block_list):
        multiprocessing.Process.__init__(self)
        self.daemon = True
        self.pbf_file_name = pbf_file_name
        self.nodes_queue = nodes_queue
        self.node_block_list = node_block_list

    def run(self):
        for node_block in self.node_block_list:
            block_parser = BlockParser(self.pbf_file_name, node_block[0], node_block[1])
            nodes = block_parser.nodes()
            self.nodes_queue.put(nodes)
        self.nodes_queue.put(None)

