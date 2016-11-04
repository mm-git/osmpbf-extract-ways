class BlockList:
    def __init__(self, block_category):
        self.block_list = []
        self.block_category = block_category
        self.total_count = 0

    def add_block(self, pos, size, count):
        self.block_list.append((pos, size, count))
        self.total_count += count

    def sort(self):
        self.block_list.sort(key=lambda x: x[0])

    def get_total_count(self):
        print self.block_category, "total count", self.total_count
        return self.total_count

    def get_total_block(self):
        print self.block_category, "total block", len(self.block_list)
        return len(self.block_list)

    def blocks(self):
        for block in self.block_list:
            yield block

    def blocks_with_skip(self, start, skip):
        for i in xrange(start, len(self.block_list), skip):
            yield self.block_list[i]
