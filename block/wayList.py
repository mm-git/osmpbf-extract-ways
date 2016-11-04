import ConfigParser
import os


class WayList:
    ID_RANGE = 1024 * 1024 * 8

    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        conf.read('./way.conf')

        self.output_folder = conf.get('way', 'folder')
        self.start_id = -1
        self.way_list = []

        try:
            os.mkdir(self.output_folder)
        except:
            pass

    def add_way(self, way):
        way_id = way[0]
        line_string = way[4]

        start_id = (way_id // WayList.ID_RANGE) * WayList.ID_RANGE
        if start_id > self.start_id:
            self.write_way_list()
            self.start_id = start_id

        self.way_list.append((way_id, way[1], way[2], way[3], line_string))

    def write_way_list(self):
        if len(self.way_list) == 0:
            return

        file_name = "way_{0}.tsv".format(self.start_id)
        with open(self.output_folder + file_name, 'w') as f:
            f.write('\n'.join('%s\t%s\t%s\t%s\t%s' % x for x in self.way_list))
        self.way_list = []
