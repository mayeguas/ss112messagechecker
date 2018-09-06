import xmlrpc.client
from logwindow import ServerLog, ClientLog

class MyTransport(xmlrpc.client.Transport):
    
    def __init__(self, use_datetime=False, use_builtin_types=False):
        super().__init__(use_datetime, use_builtin_types)
        
    def single_request(self, host, handler, request_body, verbose=False):
        # issue XML-RPC request
        try:
            http_conn = self.send_request(host, handler, request_body, verbose)
            ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, "Send:\n%s" % (request_body.decode()))
            resp = http_conn.getresponse()
            
            if resp.status == 200:
                self.verbose = verbose
                return self.parse_response(resp)

        except xmlrpc.client.Fault:
            raise
        except Exception:
            #All unexpected errors leave connection in
            # a strange state, so we clear it.
            self.close()
            raise

        #We got an error response.
        #Discard any response data and raise exception
        if resp.getheader("content-length", ""):
            resp.read()
        raise ProtocolError(
            host + handler,
            resp.status, resp.reason,
            dict(resp.getheaders())
            )
        
    def parse_response(self, response):
        # read response data from httpresponse, and parse it
        # Check for new http response object, otherwise it is a file object.
        if hasattr(response, 'getheader'):
            if response.getheader("Content-Encoding", "") == "gzip":
                stream = GzipDecodedResponse(response)
            else:
                stream = response
        else:
            stream = response

        p, u = self.getparser()

        while 1:
            data = stream.read(1024)
            if not data:
                break
            if self.verbose:
                print("body:", repr(data))
            ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, "Received:\n%s" % (data.decode()))
            p.feed(data)

        if stream is not response:
            stream.close()
        p.close()

        return u.close()