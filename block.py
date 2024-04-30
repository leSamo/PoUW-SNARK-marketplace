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
        self.__header = BlockHeader(obj['header'])
        self.__body = BlockBody(obj['body'])
