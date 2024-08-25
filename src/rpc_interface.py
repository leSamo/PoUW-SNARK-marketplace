from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

import util
import network

""" curl -X POST http://localhost:123 -H "Content-Type: application/json" -d '{"params": [0], "method":"GET_BLOCK", "id": 123}' """

def start_json_rpc_server(port):
    if port is None:
        port = 9545

    server = SimpleJSONRPCServer(('localhost', port), logRequests=False)

    util.vprint(f"Starting RPC server on port {port}")

    server.register_function(lambda: { 'latest_id': network.blockchain[-1].get_id() }, util.Command.GET_LATEST_BLOCK_ID)
    # TODO: try-except int cast, check list bounds
    server.register_function(lambda block_id: { 'block': network.blockchain[int(block_id)].encode() }, util.Command.GET_BLOCK)

    # TODO: Handle KeyboardInterrupt
    server.serve_forever()
