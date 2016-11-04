from block.blockService import BlockService

if __name__ == '__main__':
    block_service = BlockService()

    # Step 1
    #  The osm.pbf file consists of group data which are zlib-compressed,
    #  Google Protocol Buffer format data.
    #  Each group includes one or sime dense, ways and relations blocks.
    #  Each block is maximum 8000 data.
    #  As far as I checked, block order is always in order dense, ways and relations.
    #  So the first thing to do is figuring out where the start way block is.
    #  If you need number of data in each group, use create_block_list() instead of create_block_list_fast()
    block_service.create_block_list_fast()

    # Step 2
    #  As far as I checked, there are no blocks which the value granularity is not 100 and
    #  lat_offset/lon_offset is not None.
    #  However if you want to check whether it is correct or not, you can comment out next line.
    # block_service.check_offset()

    # Step 3
    #  This step uses a huge amount of memories.
    #  The coordinate data is included dense blocks.
    #  Each dense data consists of node_id(same as osm_id), latitude, longitude, and other some information.
    #  The node_id is always stored ascendant order, however some number is skipped.
    #  So in order to search the coordinate data of any node_id extremely quickly,
    #  it arranges the coordinate data to the absolute address on the memory.
    #  The number of node_id is more than 4 billion, and coordinate data are two 16bit data(8 bytes).
    #  Therefore, more than 32GB of memories are used.
    #  However don't worry about it, physical memories are not necessary so much.
    #  This code can be run enough by using virtual memory.
    #  Because the most of coordinate data are not used simultaneously.
    #  I believe it is the best option to go with the flow of the macOS paging system.
    block_service.create_node_lng_lat_list()

    # Step 4
    #  Finally, it can extract ways data.
    #  The ways data consists of way_id(same as osm_id), line data, and other some
    #  information.(name, number of road, type of road, and so on)
    #  The line data is the array of the node_id. The most of node_id number in the same line are close,
    #  however it is often quite different.
    #  It create tsv files with way_id, highway type, name, number of road, line csv.
    block_service.store_ways_to_file()
