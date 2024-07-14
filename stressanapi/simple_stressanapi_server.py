#!/usr/bin/env python3
import sys, argparse, threading, time, asyncio, random, logging, datetime as dt
sys.tracebacklimit = 0
try:
    import tornado
except:
    print(f"To use the example_server.py you need the 'tornado' library. Run: pip install tornado")
    sys.exit(1)

class averageCounter:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()
        threading.Thread(target=self.print_stats,daemon=True).start()
    def print_stats(self):
        while True:
            time.sleep(5)
            print(f"{dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}   > Average Requests: {int(self.get_average())} per second")
    def reset(self):
        self.data_time = []
        self.last_time = time.monotonic()
    def mark(self):
        now = time.monotonic()
        self.data_time.append(now-self.last_time)
        self.last_time = now
    def get_average(self):
        with self._lock:
            try:return (len(self.data_time)-1) / sum(sorted(self.data_time[1:])) # ignore first 
            except:return 0.0
            finally:self.reset()

import socket, struct
def int2ipv4(iplong):
    """Convert an integer to IPv4"""
    return socket.inet_ntoa(struct.pack('>L', iplong))
def getRandomIPv42(): # faster
    return int2ipv4(random.randint(16777216,3758096383)) # from 1.0.0.0 to 223.255.255.255

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.error_codes = list(map(int,[200,404,502,200,404,200,200,405,500,901]))
        random.shuffle(self.error_codes)
    def return_a_random_error(self):
        return self.error_codes[random.randrange(len(self.error_codes)-1)]
    def on_finish(self) -> None:
        counter.mark()
    def get(self,*args):
        # self.set_status(self.return_a_random_error())
        header_keys = list(self.request.headers.keys())
        self.write(f"GET request path: {self.request.path} - header keys: {','.join(header_keys)}")
    def post(self,*args):
        self.set_status(self.return_a_random_error())
        arguments = tornado.escape.json_decode(self.request.body)
        arg_keys, arg_values = list(arguments.keys()), list(arguments.values())
        self.write(f"POST argument keys: {','.join(arg_keys)} - values: {','.join(arg_values)}")
    def put(self,*args):
        body_arguments = tornado.escape.json_decode(self.request.body)
        body_keys, body_values = list(body_arguments.keys()), list(body_arguments.values())
        self.set_status(201)
        self.write(f"PUT body argument keys: {','.join(body_keys)} - values: {','.join(body_values)}")
    def patch(self,*args):
        body_arguments = tornado.escape.json_decode(self.request.body)
        body_keys, body_values = list(body_arguments.keys()), list(body_arguments.values())
        # print(f"PATCH body argument keys: {','.join(body_keys)} - values: {','.join(body_values)}")
        self.set_status(204)
    def delete(self,*args):
        header_keys = list(self.request.headers.keys())
        # print(f"DELETE request path: {self.request.path} - header keys: {','.join(header_keys)}")
        self.set_status(202)
    
async def run_server():
    app = tornado.web.Application([(r"/(.*)", MainHandler),],debug=True, autoreload=True)
    http_server = tornado.httpserver.HTTPServer(app,idle_connection_timeout=0.01,body_timeout=0.01)
    http_server.listen(port=args.port,address=args.host,reuse_port=True,backlog=100000)
    print(f"{dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} >>> Tornado Server is listening on http://{args.host}:{args.port}/")
    if args.log:
        tornado.log.enable_pretty_logging()
        print(f"{dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}   > Tornado pretty logging: ENABLED")
    else:
        ##──── Hide tornado default logging ───────────────────────────────────────────────────────────────────────────────────────────────
        tornado.options.options.logging = None
        logging.getLogger('tornado.access').disabled = True
        print(f"{dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}   > Run with --log to enable Tornado pretty logging.")
    await asyncio.Event().wait()

def main_function():
    asyncio.run(run_server())
  
class myArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        self._print_message(self.format_help()+"\n", file)
  
def get_argparse_menu():
    parser = myArgumentParser(allow_abbrev=True,add_help=True)

    parser.add_argument('--host',dest="host",metavar="<ip_address>",default="127.0.0.1",help="enter the IP address to bind the server. Default: 127.0.0.1")
    parser.add_argument('--port',dest="port",metavar="<port_number>",type=int,default=8000,help="choose the port to listen on. Default: 8000")
    parser.add_argument('--log',dest="log",default=False,action="store_true",help="enable Tornado pretty logging")
    return parser

if __name__ == "__main__":
    counter = averageCounter()
    parser = get_argparse_menu()
    args = parser.parse_args()
    
    main_function()
