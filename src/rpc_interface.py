from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler

import util
import network

""" curl -X POST http://localhost:9545 -H "Content-Type: application/json" -d '{"params": [0], "method":"GET_BLOCK", "id": 123}' """

server = None

class CustomJSONRPCRequestHandler(SimpleJSONRPCRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'OPTIONS, POST')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # TODO: Remove most of this method's code
    def do_POST(self):
        if not self.is_rpc_path_valid():
            self.report_404()
            return
        try:
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                chunk = self.rfile.read(chunk_size).decode()
                L.append(chunk)
                size_remaining -= len(L[-1])
            data = ''.join(L)
            response = self.server._marshaled_dispatch(data)
            self.send_response(200)
        except Exception:
            self.send_response(500)
            err_lines = traceback.format_exc().splitlines()
            trace_string = '%s | %s' % (err_lines[-3], err_lines[-1])
            fault = jsonrpclib.Fault(-32603, 'Server error: %s' % trace_string)
            response = fault.response()
        if response is None:
            response = ''
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Content-type", "application/json-rpc")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        if isinstance(response, bytes):
            self.wfile.write(response)
        else:
            self.wfile.write(response.encode())
        self.wfile.flush()
        self.connection.shutdown(1)

def start_json_rpc_server(port):
    global server

    server = SimpleJSONRPCServer(('localhost', port), requestHandler=CustomJSONRPCRequestHandler, logRequests=False)

    util.vprint(f"Starting RPC server on port {port}")

    server.register_function(lambda: { 'latest_id': network.blockchain[-1].get_id() }, util.Command.GET_LATEST_BLOCK_ID)
    # TODO: try-except int cast, check list bounds
    server.register_function(lambda block_id: { 'block': network.blockchain[int(block_id)].encode() }, util.Command.GET_BLOCK)

    server.serve_forever()
