# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️✔️✔️
# ####################################################################################################

from block_header import BlockHeader
from block_body import BlockBody
from encodeable import Encodeable

class Block(Encodeable):
    __header: BlockHeader
    __body: BlockBody

    def __init__(self):
        pass

    def setup(self, header, body):
        self.__header = header
        self.__body = body

    def encode(self):
        return {
            'header': self.__header.encode(),
            'body': self.__body.encode()
        }
    
    def decode(self, obj):
        header = BlockHeader()
        body = BlockBody()

        header.decode(obj['header'])
        body.decode(obj['body'])

        self.__header = header
        self.__body = body

    def get_id(self):
        return self.__header.get_id()
    
    def get_timestamp(self):
        return self.__header.get_timestamp()
    
    def get_difficulty(self):
        return self.__header.get_difficulty()
    
    def get_current_block_hash(self):
        return self.__header.get_current_block_hash()

    def get_state_tree(self):
        return self.__body.get_state_tree()

    def get_header(self):
        return self.__header
