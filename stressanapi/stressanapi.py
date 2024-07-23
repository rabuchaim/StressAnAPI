#!/usr/bin/env python3
# encoding: utf-8
# -*- coding: utf-8 -*-
"""StressAnAPI v1.0.3 - An API stress-test tool"""
"""
     ____  _                        _             _    ____ ___
    / ___|| |_ _ __ ___  ___ ___   / \   _ __    / \  |  _ \_ _|
    \___ \| __| '__/ _ \/ __/ __| / _ \ | '_ \  / _ \ | |_) | |
     ___) | |_| | |  __/\__ \__ \/ ___ \| | | |/ ___ \|  __/| |
    |____/ \__|_|  \___||___/___/_/   \_\_| |_/_/   \_\_|  |___|

    Author.: Ricardo Abuchaim - ricardoabuchaim@gmail.com
    License: MIT
    Github.: https://github.com/rabuchaim/StressAnAPI
    Issues.: https://github.com/rabuchaim/StressAnAPI/issues
    PyPI...: https://pypi.org/project/stressanapi/  ( pip install stressanapi )

"""
import sys, os, warnings

MIN_PYTHON = (3,10)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

os.environ['PYTHONWARNINGS']          ="ignore"
os.environ['PYTHONDONTWRITEBYTECODE'] ="ignore"
warnings.simplefilter("ignore")
sys.dont_write_bytecode = True
sys.tracebacklimit = 0

__appname__ = 'StressAnAPI'
__version__ = '1.0.3'
__release__ = '15/July/2024'
__descr__   = 'A stress-test tool for API servers'
__url__     = 'https://github.com/rabuchaim/StressAnAPI/'

import logging, logging.handlers
import socket, struct, binascii, itertools, math, gc
import tty, termios, subprocess, ctypes, shlex, signal, shutil
import urllib, urllib.request, urllib.response, urllib.parse, bisect
import re, argparse, threading, time, json, random, textwrap, functools
from typing import List,Dict
from collections import defaultdict, deque
from datetime import timedelta, datetime as dt

current_filename = sys.argv[0]
if not current_filename.endswith(".py"):
    current_filename = os.path.basename(current_filename)

lock = threading.Lock()
rlock = threading.RLock()

# __all__ = ['extract_template_var']
##################################################################################################################################
##################################################################################################################################

  ###  #      ##   ###    ##   #           #  #   ##   ###    ###
 #     #     #  #  #  #  #  #  #           #  #  #  #  #  #  #
 # ##  #     #  #  ###   #  #  #           #  #  #  #  ###    ##
 #  #  #     #  #  #  #  ####  #            ##   ####  # #      #
  ###  ####   ##   ###   #  #  ####         ##   #  #  #  #  ###

class classGlobal:
    def __init__(self):
        self.start_time = time.monotonic()

    DEBUG = os.getenv('STRESSANAPI_DEBUG','') != ""

    argsvars = {}
    config = None
    thread_list = []
    lock = threading.Lock()
    event_pause = threading.Event()
    event_pause_time = None
    event_quit = threading.Event()
    event_debug = threading.Event()

    logger = None
    syslog_message_formatter = '%(message)s'

    garbage_collector_interval = 300
    stats_window_size = 50000
    
    middot = '\xb7'
    doubleLine = "═"
    singleLine = "─"
    singleQuote = "'"
    doubleQuote = '"'
    bold_up, bold_down, bold_right, bold_left = '▲', '▼', '►', '◄'
    light_up, light_down, light_right, light_left = '↑', '↓', '→', '←'
    bold_square, light_square, bold_square_small = '■', '□', '▪'
    bold_circle, light_circle = '●', '○'

    date_format = '%Y/%m/%d %H:%M:%S.%f'
    date_format_no_milisec = '%Y/%m/%d %H:%M:%S'
    date_format_no_date = '%H:%M:%S.%f'
    date_format_no_date_no_milisec = '%H:%M:%S'
    date_format_no_time = '%Y/%m/%d'
    date_format_no_datetime = ''

    allowed_methods = ['GET','POST','PUT','PATCH','DELETE']
    default_wait_time = 0.5
    default_burst = 1
    default_threads = 1
    default_timeout = 1
    default_syslog_server_url = 'udp://127.0.0.1:514/local7'
    default_success_status_codes = [200,201,202,204]
    default_user_agent = f"{__appname__} v{__version__}"
    default_template = {
        "url": "http://localhost:8000/api/v1/foo_action",
        "method": "|".join(allowed_methods),
        "post_data": {"id": "my_customer_id", "name": "spécial_çhärs", "token": "mysupertoken"},
        "headers": {
            "User-Agent": f"{__appname__} v{__version__}",
            "Host": "set_your_api_hostname_here",
            "Content-Type": "application/json",
            "X-Forwarded-For": "1.2.3.4",
            "X-Forwarded-Host": "1.2.3.4",
            "X-Real-IP": "1.2.3.4",
        },
        # "max_redirects": 0, # not yet implemented
        "timeout": default_timeout,
        "success_status_codes": default_success_status_codes,
        "user_agent": default_user_agent,
        "start_interval": default_wait_time,
        "start_burst": default_burst,
        "start_threads": default_threads,
        "cpu_affinity": [-1],
        "syslog_server_url": default_syslog_server_url,
    }

G = classGlobal()

##################################################################################################################################
##################################################################################################################################

 ####  #  #   ###  ####  ###  #####  ###    ##   #  #   ###
 #     #  #  #     #     #  #   #     #    #  #  ## #  #
 ###    ##   #     ###   ###    #     #    #  #  # ##   ##
 #     #  #  #     #     #      #     #    #  #  #  #     #
 ####  #  #   ###  ####  #      #    ###    ##   #  #  ###

class StressAnAPIException(BaseException):
    def __init__ (self, message):
        self.message = cException(message)
        super().__init__(self.message)
    def __str__(self):
        return self.message
    def __repr__(self):
        return self.message

class StressAnAPIConfigException(StressAnAPIException):...

##################################################################################################################################
##################################################################################################################################

  ###   ##   #  #  ####  ###    ###
 #     #  #  ## #  #      #    #
 #     #  #  # ##  ###    #    # ##
 #     #  #  #  #  #      #    #  #
  ###   ##   #  #  #     ###    ###

class configFile:
    def __init__(self,filename,config_dict,url,method,post_data,headers,timeout,success_status_codes,
                 interval,burst,threads,cpu_affinity,syslog_server,start_time):
        self.config_file = filename
        self.config_dict = config_dict
        self.url = url
        self.method = str(method).upper()
        self.post_data = post_data
        self.headers = headers
        self.timeout = timeout
        self.success_status_codes = success_status_codes
        self.interval = interval
        self.burst = burst
        self.threads = threads
        self.cpu_affinity = cpu_affinity
        self.syslog_server = syslog_server
        self.elapsed_load_time = '%.6f'%(time.monotonic() - start_time)

def validateConfigFile(config_file):
    try:
        start_time = time.monotonic()
        new_config_dict = {}

        try:
            with open(config_file,'r') as f:
                config_dict = json.load(f)
        except Exception as ERR:
            raise StressAnAPIException(f"The json file appears to be invalid - {str(ERR)}") from None

        url = str(config_dict.get('url',''))
        method = str(config_dict.get('method',''))
        post_data = config_dict.get('post_data',{})
        headers = config_dict.get('headers',{})
        timeout = config_dict.get('timeout',G.default_timeout)
        interval = config_dict.get('start_interval',G.default_wait_time)
        burst = config_dict.get('start_burst',G.default_burst)
        success_status_codes = config_dict.get('success_status_codes',G.default_success_status_codes)
        threads = config_dict.get('start_threads',G.default_threads)
        cpu_affinity = config_dict.get('cpu_affinity',[])
        syslog_server_url = config_dict.get('syslog_server_url','')

        ##──── Check URL and METHOD - required data
        if (config_dict.get('url',None) is None) or (config_dict.get('url',None) == ""):
            raise StressAnAPIConfigException(f'Missing "url" information in configuration file "{config_file}"') from None
        elif not str(config_dict.get('url','')).startswith(('http://','https://')):
            raise StressAnAPIConfigException(f'Malformed URL - must starts with http:// or https://') from None
        elif not isValidURL(url):
            raise StressAnAPIConfigException(f'Malformed URL - "{url}"') from None
        elif config_dict.get('method',None) is None:
            raise StressAnAPIConfigException(f'Missing "method" information in configuration file "{config_file}"') from None
        elif method.upper() not in G.allowed_methods:
            allowed_methods_joined = ", ".join(G.allowed_methods)
            allowed_methods_result = allowed_methods_joined.rsplit(", ", 1)
            allowed_methods_string = " or ".join(allowed_methods_result)
            raise StressAnAPIConfigException(f'The allowed methods are {allowed_methods_string}, not "{method}"') from None
        new_config_dict['url'] = url
        new_config_dict['method'] = method.upper()

        ##──── check post data
        if not isinstance(post_data,Dict):
            raise StressAnAPIConfigException(f'Error in "post_data", must be a Dict not {str(type(post_data))}') from None
        for key,val in post_data.items():
            if len(re.findall('random:', val)) + len(re.findall('file:', val)) + len(re.findall('filerand:', val)) > 1:
                raise StressAnAPIConfigException(f'Error in post_data "{key}" - Only 1 "random:", "file:" or "filerand:" instruction per value') from None
        new_config_dict['post_data'] = post_data

        ##──── check headers
        if not isinstance(headers,Dict):
            raise StressAnAPIConfigException(f'Error in "headers", must be a Dict not {str(type(headers))}') from None
        for key,val in headers.items():
            if (key.lower() == 'content-type') and (val.lower() not in CONTENT_TYPES.values()):
                raise StressAnAPIConfigException(f'Invalid content-type: {val}') from None
            if len(re.findall('random:', val)) + len(re.findall('file:', val)) + len(re.findall('filerand:', val)) > 1:
                raise StressAnAPIConfigException(f'Error in header "{key}" - Only 1 "random:", "file:" or "filerand:" instruction per value') from None
        new_config_dict['headers'] = headers

        ##──── validate timeout
        try:
            timeout = float(G.default_timeout) if float(timeout) < 0.001 else float(timeout)
        except:
            raise StressAnAPIConfigException(f'Invalid "timeout" value - "{timeout}"') from None
        new_config_dict['timeout'] = timeout

        ##──── validate success status code list
        if not isinstance(success_status_codes,List):
            raise StressAnAPIConfigException(f'Error in "success_status_codes", must be a List not {str(type(success_status_codes))}') from None
        try:
            success_status_codes = list(map(int,success_status_codes))
        except Exception as ERR:
            raise StressAnAPIConfigException(f'Error in "success_status_codes", values must be an integer - {str(ERR)}') from None
        new_config_dict['success_status_codes'] = success_status_codes

        ##──── validate interval
        try:
            interval = float(interval)
            assert interval > 0
        except:
            raise StressAnAPIConfigException(f'Invalid "interval" value, must be float and greater than 0 - "{interval}"') from None
        new_config_dict['interval'] = interval

        ##──── validate burst
        try:
            burst = int(burst)
            assert burst > 0
        except:
            raise StressAnAPIConfigException(f'Invalid "burst" value, must be an integer and greater than 0 - "{burst}"') from None
        new_config_dict['burst'] = burst

        ##──── validate threads
        try:
            threads = int(threads)
            assert threads > 0
        except:
            raise StressAnAPIConfigException(f'Invalid "threads" value, must be an integer and greater than 0 - "{threads}"') from None
        new_config_dict['threads'] = threads


        ##──── validate cpu affinity
        if not isinstance(cpu_affinity,List):
            raise StressAnAPIConfigException(f'Error in "cpu_affinity", must be a List not {str(type(cpu_affinity))}') from None
        try:
            try:
                cpu_affinity = [int(item) for item in cpu_affinity]
            except:
                raise StressAnAPIConfigException(f'Error in "cpu_affinity", cpu numbers must be an integer from 0 to {os.cpu_count()-1}') from None
            if len(cpu_affinity) == 1 and cpu_affinity[0] == -1:
                cpu_affinity = [os.cpu_count()-1]
            else:
                cpu_affinity_fail = [item for item in cpu_affinity if item > (os.cpu_count()-1)]
                if len(cpu_affinity_fail) > 0:
                    raise StressAnAPIConfigException(f'Error in "cpu_affinity", invalid cpu number "{cpu_affinity_fail}" - valid cpu number are from 0 to {os.cpu_count()-1}') from None
            if cpu_affinity != []:
                setCPUAffinity(os.getpid(),cpu_affinity)
        except Exception as ERR:
            logDebug(f"validateConfigFile: {str(ERR)}")
            raise StressAnAPIConfigException(f'{str(ERR)}') from None
        new_config_dict['cpu_affinity'] = cpu_affinity

        ##──── validate syslog server url 
        syslog_server = {}
        if syslog_server_url != '':
            result = urllib.parse.urlparse(syslog_server_url)
            result = result._asdict()
            if result.get('path','').lower() != '/dev/log':
                syslog_server['scheme'] = result['scheme']
                if syslog_server['scheme'].lower() not in ['udp','tcp']:
                    raise StressAnAPIConfigException(f'Error in "syslog_server_url", invalid protocol - {str(syslog_server)}') from None
                syslog_server['host'],syslog_server['port'],*junk = str(result['netloc']+":").split(":")
                syslog_server['facility'] = result['path'].replace('/','').lower()
                try:
                    syslog_server['port']  = int(syslog_server['port'])
                except:
                    raise StressAnAPIConfigException(f'Error in "syslog_server_url", missing/invalid port number - {str(syslog_server)}') from None
                try:
                    syslog_server['facility_number'] = SYSLOG_FACILITIES[syslog_server['facility']]
                except:
                    raise StressAnAPIConfigException(f'Error in "syslog_server_url", invalid syslog facility name - {str(syslog_server)}') from None
                syslog_server['url'] = f"{syslog_server['scheme']}://{syslog_server['host']}:{syslog_server['port']}/{syslog_server['facility']}"
            else:
                syslog_server['scheme'] = '/dev/log'
                syslog_server['url'] = syslog_server['scheme']
                
            logDebug(f"Syslog server configuration: {syslog_server}")
        new_config_dict['syslog_server'] = syslog_server
        
        new_config_dict['stats_window_size'] = G.stats_window_size
        new_config_dict['garbage_collector_interval'] = G.garbage_collector_interval
        
        ##──── set the values to the G.config global variable
        G.config = configFile(os.path.realpath(config_file),new_config_dict,url,method,post_data,headers,timeout,success_status_codes,
                            interval,burst,threads,cpu_affinity,syslog_server,start_time)
    except Exception as ERR:
        logDebug(f"failed at validateConfigFile: {str(ERR)}")
        return False
    return True

def displayConfig():
    logDebug(f"configuration: {json.dumps(G.config.config_dict,separators=(', ',':'))}")
    log(f"  - Request...: {cWhite(G.config.method)} at {cWhite(G.config.url)}")

    if G.config.method in ["GET","DELETE","PATCH"]:
        if G.config.post_data != {}:
            log(f'  - Post Data.: {sFaint(f"<ignored due {G.config.method} method>")}')
    else:
        if G.config.post_data != {}:
            lines_post_data = f"  - Post Data.: {cWhite(json.dumps(G.config.post_data,sort_keys=False,ensure_ascii=False,separators=(', ',':'))[1:-1])}"
            [log(cWhite(line)) if index > 0 else log(line) for index, line in
                                enumerate(textwrap.wrap(lines_post_data, classTerminal().max_width, break_long_words=True, break_on_hyphens=False,
                                                        subsequent_indent=' ' * 16))]

    if G.config.headers == {}:
        log(f"  - Headers...: {sFaint('<empty>')}")
    else:
        lines_headers = f"  - Headers...: {cWhite(json.dumps(G.config.headers,sort_keys=False,separators=(', ',':'))[1:-1])}"
        [log(cWhite(line)) if index > 0 else log(line) for index, line in
                            enumerate(textwrap.wrap(lines_headers, classTerminal().max_width, break_long_words=True, break_on_hyphens=False,
                                                    subsequent_indent=' ' * 16))]

    cpu_affinity = f'\t- CPU Affinity: {cWhite(str(G.config.cpu_affinity)[1:-1])}' if G.config.cpu_affinity != [] else ''
    log(f"  - Timeout...: {cWhite('%.6f'%(G.config.timeout))} {getPluralString(G.config.timeout,'second','seconds',show_value_string=False)}"
        f"\t - Success Status Codes: {cWhite(','.join(map(str,G.config.success_status_codes)))}{cpu_affinity}")

    tab = "\t" if G.config.threads < 10 else ""
    number_of_threads = G.config.threads if len(G.thread_list) == 0 else len(G.thread_list)
    log(f"  - Concurrent Threads: {cWhite(number_of_threads)} {tab}\t - Burst: {cWhite(G.config.burst)} \t\t- Interval between requests: {cWhite('%.6f'%(G.config.interval))} {getPluralString(G.config.interval,'second','seconds',show_value_string=False)}")

##################################################################################################################################
##################################################################################################################################

  ### #####   ##  #####  #  #   ###         ###   ##   ###   ####   ###
 #      #    #  #   #    #  #  #           #     #  #  #  #  #     #
  ##    #    #  #   #    #  #   ##         #     #  #  #  #  ###    ##
    #   #    ####   #    #  #     #        #     #  #  #  #  #        #
 ###    #    #  #   #     ##   ###          ###   ##   ###   ####  ###

HTTP_STATUS_CODES = {"100":"Continue","101":"Switching Protocols",
                     "200":"OK","201":"Created","202":"Accepted","203":"Non-Authoritative Information","204":"No Content",
                     "205":"Reset Content","206":"Partial Content",
                     "300":"Multiple Choices","301":"Moved Permanently","302":"Found","303":"See Other","304":"Not Modified",
                     "305":"Use Proxy","307":"Temporary Redirect",
                     ##──── Client Side Errors
                     "400":"Bad Request","401":"Unauthorized","402":"Payment Required","403":"Forbidden","404":"Not Found",
                     "405":"Method Not Allowed","406":"Not Acceptable","407":"Proxy Authentication Required","408":"Request Timeout",
                     "409":"Conflict","410":"Gone","411":"Length Required","412":"Precondition Failed","413":"Request Entity Too Large",
                     "414":"Request-URI Too Long","415":"Unsupported Media Type","416":"Requested Range Not Satisfiable",
                     "417":"Expectation Failed","426":"Upgrade Required","428":"Precondition Required","429":"Too Many Requests",
                     "431":"Request Header Fields Too Large",
                     ##──── Server Side Errors
                     "500":"Internal Server Error","501":"Not Implemented","502":"Bad Gateway","503":"Service Unavailable",
                     "504":"Gateway Timeout","505":"HTTP Version Not Supported","511":"Network Authentication Required",
                     ##──── Connection Errors (created internally just to handle connection failures to an api server)
                     "900":"Connection Refused",
                     "901":"Connection Timeout",
                     "902":"Connection reset by peer",
                     "903":"Remote end closed connection without response",
                     "904":"Exceeded maximum redirects",
                     "999":"Unknown Error",
                     "32":"Broken Pipe"
                    }

  ###   ##   #  # #####  ####  #  # #####       ##### #   #  ###   ####   ###
 #     #  #  ## #   #    #     ## #   #           #    # #   #  #  #     #
 #     #  #  # ##   #    ###   # ##   #    ####   #     #    ###   ###    ##
 #     #  #  #  #   #    #     #  #   #           #     #    #     #        #
  ###   ##   #  #   #    ####  #  #   #           #     #    #     ####  ###

CONTENT_TYPES = {"javascript":"application/javascript", "json":"application/json", "zip":"application/zip",
                   "ogg":"application/ogg", "pdf":"application/pdf", "mpeg":"audio/mpeg", "wav":"audio/x-wav",
                   "gif":"image/gif", "jpeg":"image/jpeg", "png":"image/png", "form_data":"multipart/form-data",
                   "css":"text/css", "csv":"text/csv", "html":"text/html", "plain":"text/plain", "xml":"text/xml",
                   "video_mpeg":"video/mpeg", "mp4":"video/mp4", "quicktime":"video/quicktime", "webm":"video/webm"}

##################################################################################################################################
##################################################################################################################################

  ### #####   ##  #####  ###    ### #####  ###    ###   ###
 #      #    #  #   #     #    #      #     #    #     #
  ##    #    #  #   #     #     ##    #     #    #      ##
    #   #    ####   #     #       #   #     #    #        #
 ###    #    #  #   #    ###   ###    #    ###    ###  ###

##──── class to store statistics about the elapsed time of the requests
class classTimeStats:
    def __init__(self, window_size=10000):
        self.window_size = window_size
        self.__times = deque(maxlen=window_size)
        self.__sorted_times = []

    def save(self, time_in_seconds: float):
        if len(self.__times) == self.window_size:
            old_time = self.__times.popleft()
            self.__sorted_times.pop(bisect.bisect_left(self.__sorted_times, old_time))

        self.__times.append(time_in_seconds)
        bisect.insort(self.__sorted_times, time_in_seconds)

    def reset(self):
        self.__times.clear()
        self.__sorted_times.clear()

    @property
    def min_time(self):
        return min(self.__times) if self.__times else None
    @property
    def max_time(self):
        return max(self.__times) if self.__times else None
    @property
    def avg_time(self):
        if not self.__times:
            return None
        return sum(self.__times) / len(self.__times)

    def percentile(self, percentile):
        if not self.__times:
            return None
        k = (len(self.__sorted_times) - 1) * percentile / 100
        f = int(k)
        c = f + 1
        if f == c or c >= len(self.__sorted_times):
            return self.__sorted_times[f]
        return self.__sorted_times[f] * (c - k) + self.__sorted_times[c] * (k - f)

    def stats(self):
        return {
            "min": '%.6f'%self.min_time, "avg": '%.6f'%self.avg_time, "max": '%.6f'%self.max_time,
            "50pct": '%.6f'%self.percentile(50), "75pct": '%.6f'%self.percentile(75),
            "90pct": '%.6f'%self.percentile(90), "99pct": '%.6f'%self.percentile(99)
        }

##──── class to store statistics about the returned status codes
class classHttpStats:
    def __init__(self):
        self._lock = threading.Lock()
        self.default_error_codes = [200, 201, 202, 204, 400, 401, 403, 404, 405, 429, 500, 501, 502, 503, 504]
        self._dict = defaultdict(int)
        self.reset()

    def __repr__(self) -> Dict:
        return str(dict(sorted({f"{k} {self.descr(k)}": v for k, v in self._dict.items()}.items(), key=lambda x: x[0])))

    def save(self, status_code):
        with self._lock:
            self._dict[status_code] = self._dict.get(status_code, 0) + 1

    def reset(self):
        with self._lock:
            self._dict.clear()
            self._dict = {item: 0 for item in self.default_error_codes}
        return True

    def descr(self, error_code: int):
        try:
            if error_code in self._dict.keys():
                return HTTP_STATUS_CODES[str(error_code)]
        except:
            raise StressAnAPIException(f"'{type(self).__name__}' object has no attribute '{error_code}'")

    @property
    def asdict(self) -> Dict:
        return self._dict
    @property
    def asdict_desc(self) -> Dict:
        with self._lock:
            return dict(sorted({f"{k} {self.descr(k)}": v for k, v in self._dict.items()}.items(), key=lambda x: x[0]))
    @property
    def values(self) -> Dict:
        return {k: v for k, v in self._dict.items() if v > 0}

##################################################################################################################################
##################################################################################################################################

  ##    ###   ###  ###   ###          ###  #  #   ##   ###  #####
 #  #  #     #      #     #          #     #  #  #  #  #  #   #
 #  #   ##   #      #     #          #     ####  #  #  ###    #
 ####     #  #      #     #          #     #  #  ####  # #    #
 #  #  ###    ###  ###   ###          ###  #  #  #  #  #  #   #

##──── A modified version of https://pypi.org/project/chart/
class statChart:

    class scaler:
        def __init__(self, out_range=(0, 100), floor=None, round=True):
            self.out_range = out_range
            self.floor = floor
            self.round = round
        def scale(self,x, o=(0, 100), i=(0, 1)):
            return (x - i[0]) / (i[1] - i[0]) * (o[1] - o[0]) + o[0]
        def fit(self, y):
            if not self.floor and self.floor != 0:
                min_ = min(y)
            else:
                min_ = self.floor
            max_ = max(y)
            self.in_range_ = (min_, max_)
            return self
        def transform(self, y):
            y = [self.scale(yi, self.out_range, self.in_range_) for yi in y]
            if self.round:
                y = [int(round(yi)) for yi in y]
            return y
        def fit_transform(self, y):
            self.fit(y)
            return self.transform(y)

    def __init__(self):
        pass

    def __create_label(self,label, label_width):
        '''Add right padding to a text label'''
        label = label[:label_width]
        label = label.rjust(label_width)
        label += ': '
        return label

    def __build_row(self,value, label, width, mark):
        '''Build a complete row of data'''
        marks = value * mark
        row = marks.ljust(width)
        row = label + row
        return row

    def __format_number(self,number):
        return '{:,d}'.format(number).replace(',','.')

    def __percent(self,total,amount)->str:
        return ('%.2f%%'%((amount * 100) / total)).rjust(8)

    def bar(self,x, y, width=30, label_width=None, mark='◼', auto_sort=True, sort_reverse=True, with_percent=False, with_value=False, print_chart=False):
        total = sum(x) if len(x) > 0 else 0

        if total == 0: return '' # to avoid division by zero error

        if auto_sort:
            a_dict = dict(sorted(dict(zip(y,x)).items(),key=lambda x:int(x[1]), reverse=sort_reverse))
            x, y = list(a_dict.values()), list(a_dict.keys())

        if not label_width:
            label_width = max([len(l) for l in y])

        labels = [self.__create_label(l, label_width) for l in y]
        values = self.scaler((0, width), 0).fit_transform(x)
        string_chart = ''

        for value, label, amount in zip(values,labels,x):
            string_row = self.__build_row(value, label, width, mark)
            string_chart += string_row
            if with_percent:
                string_chart += self.__percent(total,amount)
            if with_value:
                string_chart += f" ({amount})"
            string_chart += '\n'

        if print_chart:
            print(string_chart)

        return string_chart

##################################################################################################################################
##################################################################################################################################

  ##    ###   ###  ###   ###        #####   ##   ###   #     ####
 #  #  #     #      #     #           #    #  #  #  #  #     #
 #  #   ##   #      #     #           #    #  #  ###   #     ###
 ####     #  #      #     #           #    ####  #  #  #     #
 #  #  ###    ###  ###   ###          #    #  #  ###   ####  ####

##──── A modified version of https://pypi.org/project/print-table/
class Table:
    def __init__(self, cols: int = 0, max_size=None, with_border=True, border_size=1):
        self.table = []
        self.rows = []
        self.cols = cols
        self.max_size = max_size
        self.with_border = with_border
        self.border_size = border_size
        self.line_h = "-" if with_border else " "
        self.line_v = "|" if with_border else " "
        self.cross = "+" if with_border else " "
        self.colors = {'ENDC': '\033[0m', 'BOLD': '\033[1m'}

    def head(self, headers: list):
        self.rows.insert(0, headers)
        return self

    def row(self, row: list):
        self.rows.append(row)
        return self

    def get_terminal_size(self):
        return shutil.get_terminal_size((80, 80)).columns if self.max_size is None else self.max_size

    def get_responsive_line(self, msg='', padding='-', space_above=True):
        processed = msg.replace(self.colors['BOLD'], '').replace(self.colors['ENDC'], '')
        terminal_size = self.get_terminal_size()
        diff = max(0, (terminal_size - len(processed))) // 2
        if space_above:
            self.table.append("")
        self.table.append(padding * diff + msg + padding * diff)

    def get_colored_text(self, msg, color):
        return f"{color}{msg}{self.colors['ENDC']}"

    def print_table(self):
        for line in self.get_table():
            print(line)

    def get_table(self):
        if self.cols and self.rows:
            self._adjust_rows()
            terminal_size = self.get_terminal_size()
            per_col = (terminal_size - self.cols - 1) // self.cols
            pattern = self.line_h * (per_col * self.cols + self.cols + 1)
            self.get_responsive_line(pattern, padding=' ', space_above=False)
            for i, row in enumerate(self.rows):
                row = [self._adjust_cols(per_col, str(r)) for r in row]
                if i == 0:
                    row = [self.get_colored_text(r, self.colors['BOLD']) for r in row]
                self.get_responsive_line(self.line_v + self.line_v.join(row) + self.line_v, padding=' ', space_above=False)
                if i != len(self.rows) - 1:
                    self._print_mid_line(terminal_size)
            self.get_responsive_line(pattern, padding=' ', space_above=False)
            if not self.with_border and self.border_size == 0:
                self.table = [line for line in self.table if line.strip()]
            return self.table

    def _adjust_rows(self):
        for row in self.rows:
            row.extend([' '] * (self.cols - len(row)))
            del row[self.cols:]

    def _adjust_cols(self, per_col, col):
        dif = per_col - len(col)
        pad = ' ' * (dif // 2)
        return f"{pad}{col}{pad if dif % 2 == 0 else pad + ' '}"

    def _print_mid_line(self, t_size):
        per_col = (t_size - self.cols - 1) // self.cols
        pattern = self.line_h * (per_col * self.cols + self.cols + 1)
        mid_line = ''.join(
            self.cross if i % (per_col + 1) == 0 else self.line_v if i == 0 or i == len(pattern) - 1 else self.line_h
            for i in range(len(pattern))
        )
        self.get_responsive_line(mid_line, padding=' ', space_above=False)

##################################################################################################################################
##################################################################################################################################

#####  ###   #  #  ####  ###    ###
  #     #    ####  #     #  #  #
  #     #    ####  ###   ###    ##
  #     #    #  #  #     # #      #
  #    ###   #  #  ####  #  #  ###

##──── with elapsedTimer() as elapsed: ───────────────────────────────────────────────────────────────────────────────────────────
class elapsedTimer:
    def __enter__(self):
        self.start = time.monotonic()
        self.start = time.monotonic()
        self.time = None
        return self

    def __exit__(self, type, value, traceback):
        self.time = time.monotonic() - self.start

    def text(self,decimal_places:int=6,end_text:str="",with_brackets=True):
        if self.time is None:
            self.time = time.monotonic() - self.start
        timer_string = f"[{f'%.{decimal_places}f'%(self.time)}{end_text}]"
        self.time = None
        return timer_string if with_brackets else timer_string[1:-1]

##──── A decorator for cache with TTL - pip install cachettl ─────────────────────────────────────────────────────────────────────
def cachettl(ttl=60, maxsize=None, typed=False):
    """A minimal version of cachettl decorator without methods cache_info() and cache_clear()"""
    def _decorator(func):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new_lrucache(*args, __time_modificator, **kwargs):
            return func(*args, **kwargs)
        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            return _new_lrucache(*args, **kwargs, __time_modificator=int(time.time() / ttl))
        return _wrapped
    return _decorator

##──── Decorator to get the elapsed time of a function ───────────────────────────────────────────────────────────────────────────
def showElapsedTimeDecorator(method):
    def decorated_method(*args, **kwargs):
        try:
            startTime = time.monotonic()
            result = method(*args, **kwargs)
            print('\033[33m[ELAPSED_TIME] [%.9f sec] '%(time.monotonic()-startTime)+str(method)+"\033[0m")
            return result
        except Exception as ERR:
            print('\033[91m'+f"[ELAPSED_TIME] showElapsedTime {method} {str(ERR)}"+'\033[0m')
    return decorated_method

##──── a decorator to show the minimum_time, maximum_time and average_time time between requests ─────────────────────────────────
def showElapsedTimeAverageDecorator(window_size=1000):
    history, max_history = [], []
    min_avg, max_avg = 1000000000, 0.0
    min_time, max_time = min_avg, max_avg

    def decorator(method):
        nonlocal history, max_history, min_avg, max_avg, min_time, max_time

        def decorated_method(*args, **kwargs):
            nonlocal history, max_history, min_avg, max_avg, min_time, max_time
            startTime = time.monotonic()
            try:
                result = method(*args, **kwargs)
                elapsedTime = time.monotonic()-startTime
                min_time = elapsedTime if elapsedTime < min_time else min_time
                max_time = elapsedTime if elapsedTime > max_time else max_time
                history.append(elapsedTime)
                if len(history) >= window_size:
                    averageTime = sum(history) / len(history)
                    history.clear()
                    log(f'\033[32;1mElapsed Time for {method.__name__}() - {window_size} calls Min/Avg/Max: {"%.9f"%(min_time)} / \033[32;4;1m{"%.9f"%(averageTime)}\033[0m\033[32;1m / {"%.9f"%(max_time)}\033[0m')
                return result
            except Exception as ERR:
                print('\033[91m'+f"[AVERAGE_ELAPSED_TIME_EXCEPTION] {method.__name__}(): {str(ERR)}"+'\033[0m')

        return decorated_method

    return decorator

##################################################################################################################################
##################################################################################################################################

  ##  #####   ##   #  #  ###    ###   ###   ##   #  #  #  # #####  ####  ###
 #  #   #    #  #  ####   #    #     #     #  #  #  #  ## #   #    #     #  #
 #  #   #    #  #  ####   #    #     #     #  #  #  #  # ##   #    ###   ###
 ####   #    #  #  #  #   #    #     #     #  #  #  #  #  #   #    #     # #
 #  #   #     ##   #  #  ###    ###   ###   ##    ##   #  #   #    ####  #  #

##──── AN ELEGANT, FAST AND THREAD SAFE COUNTER
class AtomicCounter:
    def __init__(self,start_number:int=0):
        self.start_number = start_number
        self._counter = itertools.count(self.start_number)
        self._counter_access = itertools.count()
    def incr(self): # Increment the counter +1
        return next(self._counter)
    def reset(self):
        self._counter = itertools.count(self.start_number)
        self._counter_access = itertools.count()
    @property
    def value(self): # returns the current value of the counter
        return next(self._counter) - next(self._counter_access)

##──── A counter for calculate interactions per second 
class AtomicAverageCounter:
    def __init__(self, max_window_size:int=50000):
        self.__max_window_size = max_window_size
        self.__lock = threading.RLock()
        self.__time_data = []
        self.__last_time = None
        # threading.Thread(target=self.__thread_cut_list_window_size,daemon=True).start()

    ##──── Every 60 seconds this function truncates the list that stores the request times to avoid high memory consumption. ────
    def __thread_cut_list_window_size(self):
        while True:
            time.sleep(10)
            with elapsedTimer() as elapsed:
                with self.__lock:
                    size_before = sys.getsizeof(self.__time_data)
                    self.__time_data = self.__time_data[-self.__max_window_size:]
            print(f"Cutting {size_before} >> {sys.getsizeof(self.__time_data)} {elapsed.text()}")
            
    def start(self):
        self.__last_time = time.monotonic()
        self.mark = self.__mark
        self.get_average = self.__get_average
        self.reset = self.__reset
        self.time_sum = 0.0
        self.counter = 0
        return True

    def reset_counter(self):
        with self.__lock:
            self.__time_data.clear()
        
    def mark(self):...
    def __mark(self):
        with self.__lock:
            now = time.monotonic()
            delta = now - self.__last_time
            self.__last_time = now
            # self.__time_data.append(delta)
            self.time_sum += delta
            self.counter += 1

    def get_average(self)->list:return [0.0, 0.0]
    def __get_average(self)->list:
        try:
            value_counter, value_timesum = self.reset()
            secs_per_time = value_timesum / value_counter
            times_per_sec = value_counter / value_timesum
        except Exception as ERR:
            times_per_sec, secs_per_time = 0.0,0.0
        finally:
            return [times_per_sec, secs_per_time]

    def reset(self)->list:return [0, 0.0]
    def __reset(self)->list:
        try:
            # value_counter, value_timesum = 0,0.0
            with self.__lock:
                # value_counter = len(self.__time_data)
                # value_timesum = math.fsum(self.__time_data)
                # self.__time_data.clear()
                value_counter = self.counter
                value_timesum = self.time_sum
                self.counter = 0
                self.time_sum = 0.0
                self.__last_time = time.monotonic()
        except Exception as ERR:
            value_counter, value_timesum = 0,0.0
        finally:
            return [value_counter,value_timesum]

##################################################################################################################################
##################################################################################################################################

  ###   ##   ###   ###    ##    ###  ####         ###   ##   #     #     ####   ### #####   ##   ###
 #     #  #  #  #  #  #  #  #  #     #           #     #  #  #     #     #     #      #    #  #  #  #
 # ##  #  #  ###   ###   #  #  # ##  ###         #     #  #  #     #     ###   #      #    #  #  ###
 #  #  ####  # #   #  #  ####  #  #  #           #     #  #  #     #     #     #      #    #  #  # #
  ###  #  #  #  #  ###   #  #   ###  ####         ###   ##   ####  ####  ####   ###   #     ##   #  #

##──── Thread Function to run the garbage collector process to remove non-used data from memory ──────────────────────────────────
def threadGarbageCollector():
    logDebug(f"Starting Garbage Collector with an interval of {G.garbage_collector_interval} seconds")
    gc.enable = True
    while True:
        time.sleep(G.garbage_collector_interval)
        try:
            start_time = time.monotonic()
            count1 = gc.get_count()
            collect1 = gc.collect(0)
            collect2 = gc.collect(1)
            collect3 = gc.collect(2)
            count2 = gc.get_count()
            if count1 != count2:
                logDebug(f"[GARBAGECOLLECTOR] {count1} >> GC0:{collect1}, GC1:{collect2}, GC2:{collect3} >> {count2} "
                            f">> Memory Usage: {'%.03f'%(memoryInfo.rss())} MiB [{'%.6f'%(time.monotonic()-start_time)}]")
        except Exception as ERR:
            logDebug(f"An error ocurred in garbage collector: {str(ERR)}")
            continue

##################################################################################################################################
##################################################################################################################################

 ###   ###         ####  #  #  #  #   ### #####  ###    ##   #  #   ###
  #    #  #        #     #  #  ## #  #      #     #    #  #  ## #  #
  #    ###         ###   #  #  # ##  #      #     #    #  #  # ##   ##
  #    #           #     #  #  #  #  #      #     #    #  #  #  #     #
 ###   #           #      ##   #  #   ###   #    ###    ##   #  #  ###

def int2ipv4(iplong):
    """Convert an integer to IPv4"""
    return socket.inet_ntoa(struct.pack('>L', iplong))

def int2ipv6(iplong):
    """Convert an integer to IPv6"""
    return socket.inet_ntop(socket.AF_INET6, binascii.unhexlify(hex(iplong)[2:].zfill(32)))

def isValidIPv4(ipv4_address):
    """Try to convert the given ipv4_address to integer, if it fails, is invalid ;-)"""
    try:
        struct.unpack('>L', socket.inet_aton(ipv4_address))[0]
        return True
    except:
        return False

def isValidIPv6(ipv6_address):
    """Try to convert the given ipv6_address to integer, if it fails, is invalid ;-)"""
    try:
        int.from_bytes(socket.inet_pton(socket.AF_INET6, ipv6_address), byteorder='big')
        return True
    except:
        return False

# def getRandomPrivateIPv4(num_ips=1):
#     """Generate an IP address from networks 10.0.0.0/8 or 172.16.0.0/12 or 192.168.0.0/16

#         If only 1 IP is requested, returns a string, otherwise returns a list.

#         If fails for some reason, raise an error.
#     """
#     return_list = []
#     try:
#         while (len(return_list) < num_ips):
#             return_list.append(int2ipv4(random.choice([random.randint(167772160,184549375),random.randint(3232235520,3232301055),random.randint(2886729728,2887778303)])))
#     except Exception as ERR:
#         raise Exception(ERR)
#     return return_list[0] if len(return_list) == 1 else return_list

# def getRandomIPv4(num_ips=1):
#     """Generate an IPv4 address from networks 1.0.0.0 until 223.255.255.255

#         If only 1 IP is requested, returns a string, otherwise returns a list.

#         If fails for some reason, raise an error.
#     """
#     return_list = []
#     try:
#         while (len(return_list) < num_ips):
#             return_list.append(int2ipv4(random.randint(16777216,3758096383)))
#     except Exception as ERR:
#         raise Exception(ERR)
#     return return_list[0] if len(return_list) == 1 else return_list

# def getRandomIPv42(): # faster
#     return int2ipv4(random.randint(16777216,3758096383)) # from 1.0.0.0 to 223.255.255.255

# def generatorRandomIPv4():
#     while True:
#         yield int2ipv4(random.randint(16777216,3758096383)) # from 1.0.0.0 to 223.255.255.255

##################################################################################################################################
##################################################################################################################################

#####  ####  ###   #  #  ###   #  #   ##   #
  #    #     #  #  ####   #    ## #  #  #  #
  #    ###   ###   ####   #    # ##  #  #  #
  #    #     # #   #  #   #    #  #  ####  #
  #    ####  #  #  #  #  ###   #  #  #  #  ####

class cursor:
    @staticmethod
    def hide():
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
    @staticmethod
    def show():
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

##──── Get the terminal width
class classTerminal:
    def __init__(self):
        try:
            self.max_width = os.get_terminal_size().columns - 3
        except:
            self.max_width = 134
        self.max_width = 134 if self.max_width > 135 else self.max_width
        if ('--notime' in sys.argv and '--nodate' in sys.argv) or ('--nodatetime' in sys.argv):
            self.width = self.max_width + 3
        elif '--nodate' in sys.argv:
            self.width = self.max_width - len(G.date_format_no_date)
        else:
            self.width = self.max_width - len(G.date_format) - 1


##──── Returns a line filled with a char ─────────────────────────────────────────────────────────────────────────────────────────
class line:
    def max_width()->int:
        return classTerminal().width
    def spacedChar(char:str=G.middot,spaces:int=1):
        x = ''
        while len(x) <= classTerminal().width:
            x += char+(' '*spaces)
        return x[:classTerminal().width]
    middot = G.middot * max_width()     # ·············································································
    middot1s = spacedChar(spaces=1)     # · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·
    middot2s = spacedChar(spaces=2)     # ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
    middot3s = spacedChar(spaces=3)     # ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·   ·
    single = G.singleLine * max_width() # ─────────────────────────────────────────────────────────────────────────────
    double = G.doubleLine * max_width() # ═════════════════════════════════════════════════════════════════════════════
    dot = "." * max_width()             # .............................................................................
    dash = "-" * max_width()            # -----------------------------------------------------------------------------
    equal = "=" * max_width()           # =============================================================================
    underline = "_" * max_width()       # _____________________________________________________________________________
    greaterthan = ">" * max_width()     # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    lowerthan = "<" * max_width()       # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

##################################################################################################################################
##################################################################################################################################

  ##   #  #   ###  ###    ###   ##   #      ##   ###    ###
 #  #  ## #  #      #    #     #  #  #     #  #  #  #  #
 #  #  # ##   ##    #    #     #  #  #     #  #  ###    ##
 ####  #  #     #   #    #     #  #  #     #  #  # #      #
 #  #  #  #  ###   ###    ###   ##   ####   ##   #  #  ###

##──── COLOR FUNCTION NAMES ──────────────────────────────────────────────────────────────────────────────────────────────────────
def cDate(msg): return sFaint(cSilver(str(msg)));
def _cDateRaw(msg): return str(msg)
def cException(msg): return cTomato(str(msg))
def cError(msg): return cRed(str(msg))
def cDebug(msg): return cLime(str(msg))
def cWarning(msg): return cYellow(str(msg))
##──── COLOR NAMES ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def cSilver(msg): return '\033[38;2;192;192;192m'+str(msg)+'\033[0m'
def cTomato(msg): return '\033[38;2;255;99;71m'+str(msg)+'\033[0m'
def cRed(msg): return '\033[91;1m'+str(msg)+'\033[0m'
def cCyan(msg): return '\033[36;1m'+str(msg)+'\033[0m'
def cLime(msg): return '\033[38;2;0;255;0m'+str(msg)+'\033[0m'
def cYellow(msg): return '\033[93;1m'+str(msg)+'\033[0m'
def cDarkYellow(msg): return '\033[33m'+str(msg)+'\033[0m'
# def cGreen(msg): return '\033[32m'+str(msg)+'\033[0m'
def cGreen(msg): return '\033[38;2;0;250;154m'+str(msg)+'\033[0m'
def cSnow(msg): return '\033[38;2;245;245;245;1m'+str(msg)+'\033[0m'
def cWhite(msg): return cSnow(str(msg))
def cDimGrey(msg): return '\033[38;2;105;105;105m'+str(msg)+'\033[0m'
def cGrey(msg): return '\033[38;2;128;128;128m'+str(msg)+'\033[0m'
def cBlue(msg): return '\033[38;2;135;206;235m'+str(msg)+'\033[0m'
##──── ANSI STYLES ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def sBold(msg): return '\033[1m'+str(msg)+'\033[0m'
def sFaint(msg): return '\033[2m'+str(msg)+'\033[0m'
def sItalic(msg): return '\033[3m'+str(msg)+'\033[0m'
def sUnderline(msg): return '\033[4m'+str(msg)+'\033[0m'
def sNegative(msg): return '\033[7m'+str(msg)+'\033[0m'
def sStrikeout(msg): return '\033[9m'+str(msg)+'\033[0m'
def sReset(msg): return '\033[0m'+str(msg)
##──── REMOVE ANSI COLOR CODES (USED BEFORE SEND TO SYSLOG SERVER) ───────────────────────────────────────────────────────────────
def _stripColorEmpty(colored_string):return colored_string
def _stripColor(colored_string):return colored_string
def stripColor(colored_string):
    return re.sub('\x1b\\[(K|.*?m)', '', colored_string)
##──── RETURNS THE REAL LENGTH OF A COLORED STRING ───────────────────────────────────────────────────────────────────────────────
def ansiLen(s):
    return len(stripColor(s))

##################################################################################################################################
##################################################################################################################################

 ####  #  #  #  #   ### #####  ###    ##   #  #   ###
 #     #  #  ## #  #      #     #    #  #  ## #  #
 ###   #  #  # ##  #      #     #    #  #  # ##   ##
 #     #  #  #  #  #      #     #    #  #  #  #     #
 #      ##   #  #   ###   #    ###    ##   #  #  ###

##──── To help me with debug ─────────────────────────────────────────────────────────────────────────────────────────────────────
def HERE(textString=""):
    print(cRed("HERE ")+cDebug(str(textString)))
def here(textString=""):
    print(cRed("here ")+cDebug(str(textString)))

##──── Pretty print a dict as json ───────────────────────────────────────────────────────────────────────────────────────────────
def ppJson(a_dict,indent:int=3,compact:bool=True,print_dump=True):
    if compact:
        text = json.dumps(a_dict,indent=indent,sort_keys=False,ensure_ascii=False,default=jsonSerial,separators=(',',':'))
    else:
        text = json.dumps(a_dict,indent=indent,sort_keys=False,ensure_ascii=False,default=jsonSerial)
    if print_dump:
        print(text)
    return text
##──── Pretty print a dict as colored json ───────────────────────────────────────────────────────────────────────────────────────
def ppColorJson(a_dict,indent:int=3,compact:bool=True,print_dump=True):
    def colorize_json(json_str):
        def colorize(match):
            key, _, string, _, number, _, _, boolean, null, bracket, comma, colon = match.groups()
            if key:
                return '\033[38;2;70;130;180m'+str(key)+'\033[0m'
            elif string:
                return '\033[32m'+str(string)+'\033[0m'
            elif number:
                return '\033[93;1m'+str(number)+'\033[0m'
            elif boolean:
                return '\033[33m'+str(boolean)+'\033[0m'
            elif null:
                return '\033[38;2;128;128;128m'+str(null)+'\033[0m'
            elif bracket:
                return bracket
            elif comma:
                return comma
            elif colon:
                return colon
        json_pattern = re.compile(r'(\"(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\\"])*\"(?=\s*:))|(\"(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\\"])*\")|(-?\d+(\.\d*)?([eE][+-]?\d+)?)|(true|false)|(null)|([{}\[\]])|([,])|(:)')
        return json_pattern.sub(colorize, json_str)
    text = colorize_json(ppJson(a_dict,indent,compact,print_dump=False))
    if print_dump:
        print(text)
    return text
##──── To use in json dump as 'default' parameter ────────────────────────────────────────────────────────────────────────────────
def jsonSerial(obj):
    import datetime
    if isinstance(obj, (datetime, datetime.date)):
        return obj.isoformat()
    else:
        return str(obj)
##──── Validates an URL ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def isValidURL(uri):
    try:
        result = urllib.parse.urlparse(uri)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False
##──── Get a plural and singular strings for a value - like '1 request' '2 requests' ─────────────────────────────────────────────
def getPluralString(value=0,singularString="request",pluralString="requests",zeroString="",show_value_string=True):
    zeroString = singularString if zeroString == "" else zeroString
    if show_value_string:
        return f"{value} {zeroString}" if value == 0 else f"{value} {singularString}" if (value > 0 and value <= 1) else f"{value} {pluralString}"
    else:
        return f"{zeroString}" if value == 0 else f"{singularString}" if (value > 0 and value <= 1) else f"{pluralString}"
##──── returns a time in 00h00m00s ───────────────────────────────────────────────────────────────────────────────────────────────
def getTimeHumanReadable(start_time):
    a = start_time #last epoch recorded
    b = time.monotonic() #current epoch time
    c = b - a #returns seconds
    days = c // 86400
    hours = int(c // 3600 % 24)
    minutes = int(c // 60 % 60)
    seconds = int(c % 60)
    return (f"{'%02d'%hours}h{'%02d'%minutes}m{'%02d'%seconds}s")
##──── Format a number like 123456789 into 123.456.789 ───────────────────────────────────────────────────────────────────────────
def formatNumber(number):
    return '{:,d}'.format(number).replace(',','.')
##──── To make asyncio/thread stop on first CTRL+C ───────────────────────────────────────────────────────────────────────────────
def receivedSignalSTOP(signalSTOP, frame:str=''):
    try:
        logResponse.__code__ = logResponseEmpty.__code__
        G.event_quit.set()
    finally:
        cursor.show()
        os.system('stty sane')
        sys.exit(0)
##──── INTERCEPT THE BROKEN PIPE SIGNAL AND DON'T LET THE APPLICATION CRASH ──────────────────────────────────────────────────────
def received_SIGPIPE(signalPIPE,frame=""):
    time.sleep(0.00001)
    return True
##################################################################################################################################
##################################################################################################################################

 ####  ###   ###    ##   ###         ####  #  #  #  #   ### #####  ###    ##   #  #   ###
 #     #  #  #  #  #  #  #  #        #     #  #  ## #  #      #     #    #  #  ## #  #
 ###   ###   ###   #  #  ###         ###   #  #  # ##  #      #     #    #  #  # ##   ##
 #     # #   # #   #  #  # #         #     #  #  #  #  #      #     #    #  #  #  #     #
 ####  #  #  #  #   ##   #  #        #      ##   #  #   ###   #    ###    ##   #  #  ###

##──── Extract the http error code from a string ─────────────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=128,typed=False)
def extractErrorCode(error_message):
    try:
        match = re.search(r"(\d+)", error_message)
        if match:
            return int(match.group(1))
    except Exception as ERR:
        logDebug(f"extractErrorCode: {str(ERR)}")
        return 0

##──── Return the text of a status code ──────────────────────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=128,typed=False)
def getStatusCodeDescription(status_code:int):
    try:
        return HTTP_STATUS_CODES[str(status_code)]
    except Exception as ERR:
        logDebug(f"getStatusCodeDescription: {str(ERR)}")
        return ""

##──── Return the responde code as --- if is greater than 900 (StressAnAPI internal use) ─────────────────────────────────────────
# @functools.lru_cache(maxsize=128,typed=False)
def getFormattedStatusCode(status_code):
    try:
        new_status_code = '###' if str(status_code).startswith('9') else status_code
        status_code_message = cGreen(f"{new_status_code} {HTTP_STATUS_CODES[str(status_code)]}") if status_code in G.config.success_status_codes else cRed(f"{new_status_code} {HTTP_STATUS_CODES[str(status_code)]}")
        return f"{status_code_message}"
    except Exception as ERR:
        logDebug(f"getFormattedStatusCode: {str(ERR)}")
        return ""

##──── Return a internal response code based on given error_message ──────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=128,typed=False)
def getErrorResponseCode(error_message):
    try:
        if str(error_message).lower().find("connection refused") >= 0:
            return 900
        elif str(error_message).lower().find("timed out") >= 0:
            return 901
        elif str(error_message).lower().find("reset by peer") >= 0:
            return 902
        elif str(error_message).lower().find("closed connection") >= 0:
            return 903
        else:
            result = extractErrorCode(error_message)
            return 999 if result is None else result
    except Exception as ERR:
        logDebug(f"getErrorResponseCode: {str(ERR)}")
        return 0

@functools.lru_cache(maxsize=128,typed=False)
def shortenErrorMessage(string:str,max_width:int=128,placeholder:str="(..)"):
    if len(string)-len(placeholder) < max_width:
        return string
    else:
        return string[:max_width-len(placeholder)]+placeholder

##################################################################################################################################
##################################################################################################################################

 #      ##    ###   ###  ###   #  #   ###
 #     #  #  #     #      #    ## #  #
 #     #  #  # ##  # ##   #    # ##  # ##
 #     #  #  #  #  #  #   #    #  #  #  #
 ####   ##    ###   ###  ###   #  #   ###

#deflogging
def log(message:str="",end:str="\n"):
    print(getLogDate()+str(message),end=end)
def logSyslog(message:str="",end:str="\n"):
    log_string = getLogDate()+str(message)
    G.logger.info(stripColor(log_string))
    print(log_string,end=end)

def logDebug(message:str="",end:str="\n"):
    # print(getLogDate()+cDebug("[DEBUG] "+str(message)),end=end)
    log(cDebug("[DEBUG] "+str(message)))
def logDebugSyslog(message:str="",end:str="\n"):
    print(cDebug("[DEBUG] "+str(message)),end=end)
    G.logger.debug(stripColor(message))

def logEmpty(message:str="",end:str="\n"):pass
def logResponseEmpty(text_id,method,url,response_code,response_body,elapsed_time):pass
def logResponseSyslog(text_id,method,url,response_code,response_body,elapsed_time):
    G.logger.info(f"{G.middot} {text_id} {method} {url} - {stripColor(getFormattedStatusCode(response_code))} {response_body.strip()} {elapsed_time}")

# @showElapsedTimeAverageDecorator(window_size=5000)
def logResponse(text_id,method,url,response_code,response_body,elapsed_time):pass
# @showElapsedTimeAverageDecorator(window_size=5000)
def _logResponse(text_id,method,url,response_code,response_body,elapsed_time):
    with lock:
        log(f"{G.middot} {text_id} {method} {url} - {getFormattedStatusCode(response_code)} {elapsed_time}")
def _logResponseBody(text_id,method,url,response_code,response_body,elapsed_time):
    with lock:
        log(f"{G.middot} {text_id} {method} {url} - {getFormattedStatusCode(response_code)} {cDarkYellow(response_body.strip())} {elapsed_time}")

##──── Returns the current date time to be used with log to stdout functions ─────────────────────────────────────────────────────
def getLogDateEmpty():return ""
def getLogDate():
    A = dt.now()
    if A.microsecond%1000>=500:A=A+timedelta(milliseconds=1)
    if G.date_format.endswith("f"):
        D = A.strftime(G.date_format)[:-3]
    else:
        D = A.strftime(G.date_format)
    return cDate(D+" ")

##──── GetPID for logging multithreads ───────────────────────────────────────────────────────────────────────────────────────────
def _logGetPID():
    return "["+str(os.getpid())+"] "
def logGetPID():return ""

##################################################################################################################################
##################################################################################################################################

  ### #   #   ###  #      ##    ###         ###  ####  ###   #  #  ####  ###
 #     # #   #     #     #  #  #           #     #     #  #  #  #  #     #  #
  ##    #     ##   #     #  #  # ##         ##   ###   ###   #  #  ###   ###
    #   #       #  #     #  #  #  #           #  #     # #    ##   #     # #
 ###    #    ###   ####   ##    ###        ###   ####  #  #   ##   ####  #  #

SYSLOG_FACILITIES = {'kernel':0,'user':1,'mail':2,'daemon':3,'auth':4,'syslog':5,'lpr':6,'news':7,'uucp':8,
                      'clock':9,'authpriv':10,'ftp':11,'ntp':12,'security':13,'console':14,'cron':15,
                      'local0':16,'local1':17,'local2':18,'local3':19,'local4':20,'local5':21,'local6':22,'local7':23}

SYSLOG_FACILITIES_BY_ID = {v:k for k,v in SYSLOG_FACILITIES.items()}

class ReconnectingSysLogHandler(logging.handlers.SysLogHandler):
    def __init__(self, *args, **kwargs):
        self._is_retry = False
        try:
            super(ReconnectingSysLogHandler, self).__init__(*args, **kwargs)
            self._is_retry = False
        except Exception as ERR:
            raise StressAnAPIException(f"Failed to connect to syslog server {G.config.syslog_server}. {str(ERR)}") from None
    def is_socketstream_and_not_unixsocket(self):
        return self.socktype == socket.SOCK_STREAM and not self.unixsocket
    def _reconnect(self):
        if self.socket:
            self.socket.close()
        self.socket = socket.socket(socket.AF_INET, self.socktype)
        if (self.socktype == socket.SOCK_STREAM or self.socktype == socket.SOCK_DGRAM):
            self.socket.connect(self.address)
    def handleError(self, record):
        if self._is_retry:
            return
        self._is_retry = True
        try:
            __, exception, __ = sys.exc_info()
            if isinstance(exception, socket.error) and exception.errno == 32:
                try: self._reconnect()
                except Exception as ERR: 
                    self.sendErrorMessage(f"Failed at syslog handler self._reconnect(B): {str(ERR)}")
                    self._is_retry = True
                else: 
                    self.emit(record)
        except Exception as ERR: 
            self.sendErrorMessage(f"Failed at syslog handler self._reconnect(A): {str(ERR)}")
        finally:
            self._is_retry = False
    @cachettl(ttl=10)
    def sendErrorMessage(self,message):
        log.error(sNegative(message))

def getSyslogLogger(logger_name:str,scheme:str,host:str,port:int,facility=logging.handlers.SysLogHandler.LOG_LOCAL7,log_level='INFO'):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level) from None
    # The 1st blank space in the loggername is required ONLY for rsyslog otherwise you can´t filter 
    # the messages by $programname nor $msg. I don´t know why.
    logger = logging.getLogger("%s"%(logger_name)) 
    logger.setLevel(logging.DEBUG)  # Definindo o nível mais baixo para garantir que todos os logs sejam enviados ao syslog
    # if syslog_address.startswith('tcp://'):
    #     if str(syslog_address[6:]).find(":") < 0:
    #         raise ValueError(f'Unknown value for syslog_addr: {syslog_address}. Missing port number.')
    #     else:
    #         host,port = syslog_address[6:].split(":")
    #     syslog_handler = ReconnectingSysLogHandler(address=(host,int(port)), facility=facility, socktype=socket.SOCK_STREAM)
    # elif syslog_address.startswith('udp://'):
    #     if str(syslog_address[6:]).find(":") < 0:
    #         raise ValueError(f'Unknown value for syslog_addr: {syslog_address}. Missing port number.')
    #     else:
    #         host,port = syslog_address[6:].split(":")
    #     syslog_handler = ReconnectingSysLogHandler(address=(host,int(port)), facility=facility, socktype=socket.SOCK_DGRAM)
    # else:
    #     syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=facility)
    if scheme == 'udp':
        syslog_handler = ReconnectingSysLogHandler(address=(host,int(port)), facility=facility, socktype=socket.SOCK_DGRAM)
    elif scheme == 'tcp':
        syslog_handler = ReconnectingSysLogHandler(address=(host,int(port)), facility=facility, socktype=socket.SOCK_STREAM)
    else: # scheme == '/dev/log'
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=facility)        
    syslog_handler.setLevel(numeric_level)
    syslog_handler.propagate = False
    formatter = logging.Formatter(G.syslog_message_formatter)
    syslog_handler.setFormatter(formatter)
    logger.addHandler(syslog_handler)
    # G.logger_handler = syslog_handler
    return logger

##################################################################################################################################
##################################################################################################################################

 ###   #  #  #  #         ###   ##   #  #  #  #   ##   #  #  ###
 #  #  #  #  ## #        #     #  #  ####  ####  #  #  ## #  #  #
 ###   #  #  # ##        #     #  #  ####  ####  #  #  # ##  #  #
 # #   #  #  #  #        #     #  #  #  #  #  #  ####  #  #  #  #
 #  #   ##   #  #         ###   ##   #  #  #  #  #  #  #  #  ###

#──── RUN THE COMMAND LINE AND RETURNS A LIST [(True|False),(output|error),elapsed_time] OR RAISE AN ERROR
def runCommand(command_to_run,command_to_send:str='',raise_on_errors:bool=False,command_timeout:int=2)->list:
    """Returns: [bool(return_code == 0), result:str, elapsed_time:float] """
    try:
        start_time = time.monotonic()
        cmd2run = shlex.split(command_to_run)
        cmd2send = shlex.split(command_to_send)
        shell = True if '|' in cmd2run else False
        # logDebug(cmd2run)
        process = subprocess.Popen(cmd2run, universal_newlines=True,shell=shell,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        if cmd2send:
            for command in cmd2send:
                process.stdin.write(command)
        result, error = process.communicate(timeout=command_timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception(f"Command timeout ({str(cmd2run)})")
    except FileNotFoundError:
        raise Exception(f"File not found ({str(cmd2run)})")
    if process.returncode != 0:
        result = error
    return [(process.returncode == 0),result,'%.6f'%(time.monotonic()-start_time)]

##################################################################################################################################
##################################################################################################################################

 #  #  ####  #  #   ##   ###  #   #        ###   #  #  ####   ##
 ####  #     ####  #  #  #  #  # #          #    ## #  #     #  #
 ####  ###   ####  #  #  ###    #           #    # ##  ###   #  #
 #  #  #     #  #  #  #  # #    #           #    #  #  #     #  #
 #  #  ####  #  #   ##   #  #   #          ###   #  #  #      ##

class memoryInfo:
    def rss():
        ''' Memory usage in MiB '''
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong),
                        ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]

        try:
            ##──── LINUX and MACOS
            result = subprocess.check_output(['ps', '-p', str(os.getpid()), '-o', "rss="])
            return float('%0.2f'%(float(int(result.strip()) / 1024)))
        except:
            ##──── WINDOWS
            try:
                pid = ctypes.windll.kernel32.GetCurrentProcessId()
                process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
                counters = PROCESS_MEMORY_COUNTERS()
                counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
                if ctypes.windll.psapi.GetProcessMemoryInfo(process_handle, ctypes.byref(counters), ctypes.sizeof(counters)):
                    memory_usage = counters.WorkingSetSize
                    return float((int(memory_usage) / 1024) / 1024)
            except:
                return 0.0

class cpuInfo:
    def usage():
        try:
            time.sleep(0.2)
            cmd2run = f'ps -o pid,%cpu,command ax'
            result,output,elapsed_time = runCommand(cmd2run)
            if result:
                output = output.splitlines()
                ps_line = [item for item in output if item.lstrip().startswith(str(os.getpid()))]
                if len(ps_line) > 0:
                    cpu_percent = ps_line[0].split()[1]
                    return '%0.2f'%(float(cpu_percent))
        except Exception as ERR:
            logDebug(f"cpuInfo: {str(ERR)}")
            return 0.0
    def average_usage():
        CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
        return CPU_Pct


##################################################################################################################################
##################################################################################################################################

  ###  ###   #  #         ##   ####  ####  ###   #  #  ###  ##### #   #
 #     #  #  #  #        #  #  #     #      #    ## #   #     #    # #
 #     ###   #  #        #  #  ###   ###    #    # ##   #     #     #
 #     #     #  #        ####  #     #      #    #  #   #     #     #
  ###  #      ##         #  #  #     #     ###   #  #  ###    #     #

def setCPUAffinity(proc_pid:int,cpu_affinity:list):
    try:
        cmd2run = f"taskset -cpa {','.join(map(str,cpu_affinity))} {proc_pid}"
        result,output,elapsed_time = runCommand(cmd2run)
        return result == 0
    except Exception as ERR:
        raise StressAnAPIException(f"setCPUAffinity: {str(ERR)}")

##################################################################################################################################
##################################################################################################################################

 ###   ####   ##   ###   #  #  #### #   #
 #  #  #     #  #  #  #  # #   #     # #
 ###   ###   #  #  #  #  ##    ###    #
 # #   #     ####  #  #  # #   #      #
 #  #  ####  #  #  ###   #  #  ####   #

def readKey():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            # print(repr(b))
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b[:1])
            # print(k)
            key_mapping = {
                113: 'q',
                27: 'esc',
                10: 'return',
                65: 'up', 66: 'down',
                67: 'right', 68: 'left',
                61: 'plus', 43: 'plus', # 61: 'equal', 43: 'plus',
                45: 'minus', 95: 'minus', # 45: 'minus', 95: 'underline',
                44: 'comma', 46: 'dot',
                62: 'greaterthan', 60: 'lowerthan',
                40: 'openparenthesis', 41: 'closeparenthesis',
                91: 'opensquarebracket', 93: 'closesquarebracket',
                123: 'opencurlybracket', 125: 'closecurlybracket',
            }
            return key_mapping.get(k, chr(k))
    except Exception as ERR:
        logDebug(f"readKey: {str(ERR)}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

##################################################################################################################################
##################################################################################################################################

 #  #  #### #   #   ###        ####  #  #  #  #   ### #####  ###    ##   #  #   ###
 # #   #     # #   #           #     #  #  ## #  #      #     #    #  #  ## #  #
 ##    ###    #     ##         ###   #  #  # ##  #      #     #    #  #  # ##   ##
 # #   #      #       #        #     #  #  #  #  #      #     #    #  #  #  #     #
 #  #  ####   #    ###         #      ##   #  #   ###   #    ###    ##   #  #  ###

def pause():
    if G.event_pause.is_set():
        counterAverage.reset()
        log(cGrey(line.middot1s))
        log(f">>> {cWhite(f'Resuming the application after {getTimeHumanReadable(G.event_pause_time)}')}")
        log(cGrey(line.middot1s))
        G.event_pause.clear()
    else:
        counterAverage.reset()
        G.event_pause_time = time.monotonic()
        log(cGrey(line.middot1s))
        log(f">>> {cWhite('PAUSE requested!')}")
        log(cGrey(line.middot1s))
        G.event_pause.set()

def keyMemInfo():
    log(f">>> {__appname__} Memory usage: {memoryInfo.rss()} MiB - CPU usage: {cpuInfo.usage()}%")

def increaseThreads():
    ThreadMakeRequests = threadMakeRequestsURLLib(timeStats=timeStats,httpStats=httpStats)
    ThreadMakeRequests.setDaemon(False)
    G.thread_list.append(ThreadMakeRequests)
    ThreadMakeRequests.start()
    log(f"  {G.bold_right} Creating one more thread... {getPluralString(len(G.thread_list),'thread','threads')} currently running")

def decreaseThreads():
    if len(G.thread_list) == 1:
        unique_thread = G.thread_list[0]
        thread_name,thread_id = unique_thread.identify()
        log(f"  {G.light_circle} There is only 1 thread running ({thread_name} pid:{thread_id})... can't join it.")
    else:
        thread_to_join = G.thread_list[0]
        thread_name,thread_id = thread_to_join.join()
        G.thread_list.pop(0)
        log(f"  {G.bold_left} Joining thread '{thread_name}' pid:{thread_id}... {getPluralString(len(G.thread_list),'thread','threads')} currently running")

def increaseTimeout():
    limit_reached = ''
    G.config.timeout = round(G.config.timeout, 5)
    if G.config.timeout >= 60.0:
        G.config.timeout = 60.0
        limit_reached = '(limit reached!)'
    elif G.config.timeout >= 0.00001 and G.config.timeout < 0.0001:
        G.config.timeout = round(G.config.timeout + 0.00001, 5)
    elif G.config.timeout >= 0.0001 and G.config.timeout < 0.001:
        G.config.timeout = round(G.config.timeout + 0.0001, 5)
    elif G.config.timeout >= 0.001 and G.config.timeout < 0.01:
        G.config.timeout = round(G.config.timeout + 0.001, 5)
    elif G.config.timeout >= 0.01 and G.config.timeout < 0.1:
        G.config.timeout = round(G.config.timeout + 0.01, 5)
    elif G.config.timeout >= 0.1:
        G.config.timeout = round(G.config.timeout + 0.1, 5)
    log(f"  + Increasing the request timeout to %.6f sec {limit_reached}"%(G.config.timeout))

def decreaseTimeout():
    limit_reached = ''
    G.config.timeout = round(G.config.timeout, 5)
    if G.config.timeout > 0.1:
        G.config.timeout = round(G.config.timeout - 0.1, 5)
    elif G.config.timeout > 0.01:
        G.config.timeout = round(G.config.timeout - 0.01, 5)
    elif G.config.timeout > 0.001:
        G.config.timeout = round(G.config.timeout - 0.001, 5)
    elif G.config.timeout > 0.0001:
        G.config.timeout = round(G.config.timeout - 0.0001, 5)
    elif G.config.timeout > 0.00001:
        G.config.timeout = round(G.config.timeout - 0.00001, 5)
    else:
        G.config.timeout = 0.000010
        limit_reached = '(limit reached!)'
    log(f"  - Decreasing the request timeout to %.6f sec {limit_reached}"%(G.config.timeout))

def increaseInterval():
    limit_reached = '(slower)'
    G.config.interval = round(G.config.interval, 5)
    if G.config.interval >= 5.0:
        G.config.interval = 5.0
        limit_reached = '(limit reached!)'
    elif G.config.interval >= 0.00001 and G.config.interval < 0.0001:
        G.config.interval = round(G.config.interval + 0.00001, 5)
    elif G.config.interval >= 0.0001 and G.config.interval < 0.001:
        G.config.interval = round(G.config.interval + 0.0001, 5)
    elif G.config.interval >= 0.001 and G.config.interval < 0.01:
        G.config.interval = round(G.config.interval + 0.001, 5)
    elif G.config.interval >= 0.01 and G.config.interval < 0.1:
        G.config.interval = round(G.config.interval + 0.01, 5)
    elif G.config.interval >= 0.1:
        G.config.interval = round(G.config.interval + 0.1, 5)
    log(f"  {G.light_up} Increasing the interval between requests to %.6f sec {limit_reached}" % (G.config.interval))

def decreaseInterval():
    limit_reached = '(faster)'
    G.config.interval = round(G.config.interval, 5)
    if G.config.interval > 0.1:
        G.config.interval = round(G.config.interval - 0.1, 5)
    elif G.config.interval > 0.01:
        G.config.interval = round(G.config.interval - 0.01, 5)
    elif G.config.interval > 0.001:
        G.config.interval = round(G.config.interval - 0.001, 5)
    elif G.config.interval > 0.0001:
        G.config.interval = round(G.config.interval - 0.0001, 5)
    elif G.config.interval > 0.00001:
        G.config.interval = round(G.config.interval - 0.00001, 5)
    else:
        G.config.interval = 0.000010
        limit_reached = '(limit reached!)'
    log(f"  {G.light_down} Decreasing the interval between requests to %.6f sec {limit_reached}"%(G.config.interval))

def increaseBurst():
    limit_reached = '(faster)'
    G.config.burst += 1
    if G.config.burst > 300:
        G.config.burst = 300
        limit_reached = '(limit reached!)'
    log(f"  {G.light_right} Increasing the burst of requests to {getPluralString(G.config.burst,'request','requests')} {limit_reached}")

def decreaseBurst():
    limit_reached = '(slower)'
    G.config.burst -= 1
    if G.config.burst < 1:
        G.config.burst = 1
        limit_reached = '(limit reached!)'
    log(f"  {G.light_left} Decreasing the burst of requests to {getPluralString(G.config.burst,'request','requests')} {limit_reached}")

def resetStats():
    httpStats.reset()
    timeStats.reset()
    counter.reset()
    counterAverage.reset_counter()
    log(cGrey(line.middot1s))
    log(f"  > All statistics have been reset as requested")
    log(cGrey(line.middot1s))

def displayCurrentConfiguration():
    log(line.single)
    log(f">>> {cWhite(f'Current {__appname__} Configuration:')}")
    log("")
    displayConfig()
    log(line.single)

def displayAverageTimeStats():
    if G.event_pause.is_set():
        log(f">>> Average: 0 requests/sec (PAUSED)")
    else:
        requests_per_sec, sec_per_requests = counterAverage.get_average()
        log(f">>> Average {'%.0f'%(requests_per_sec)} req/sec - Min/Avg/Max: {'%.6f'%(timeStats.min_time)}/{'%.6f'%(timeStats.avg_time)}/{'%.6f'%(timeStats.max_time)} - Total: {counter.value} reqs")

def displayFullHttpStats():
    def remove9XXFromString(col_str): # remove errors 900 used by internal control
        return "###"+col_str[3:] if col_str.startswith('9') else col_str
    try:
        with lock:
            log(line.single)
            log(f">>> {cWhite('Statistics of Success vs. Errors:')}")
            log("")
            max_number_len = len(str(sorted(list(httpStats.asdict.values()))[-1]))
            max_size = (classTerminal().max_width-ansiLen(getLogDate())-10)
            max_col_size = max_size // 2
            stats = {key:val for key,val in httpStats.asdict_desc.items() if val > 0}
            ##──── Chart
            success = [val for key,val in httpStats.asdict.items() if key in G.config.success_status_codes]
            errors400 = [val for key,val in httpStats.asdict.items() if key >= 400 and key < 500]
            errors500 = [val for key,val in httpStats.asdict.items() if key >= 500 and key < 600]
            conn_errors = [val for key,val in httpStats.asdict.items() if key >= 900]
            # print(sum(success),sum(errors),sum(conn_errors))
            x = [sum(success),sum(errors400),sum(errors500),sum(conn_errors)]
            y = ['Success','HTTP 4XX errors','HTTP 5XX errors','Connection errors']
            a_chart = statChart().bar(x,y,width=(max_size//3)*2,with_percent=True, with_value=True).splitlines()
            [log(f"         {line}") for line in a_chart]
            log(line.middot1s)
            ##──── Table
            keys = list(stats.keys())
            half_size = (len(keys) + 1) // 2
            col1 = keys[:half_size]
            col2 = keys[half_size:]
            for i in range(half_size):
                col1_key = col1[i] if i < len(col1) else ''
                col2_key = col2[i] if i < len(col2) else ''
                col1_str = f"{col1_key}: {stats[col1_key]}" if col1_key else ''
                col2_str = f"{col2_key}: {stats[col2_key]}" if col2_key else ''
                log(f"      {remove9XXFromString(col1_str):<{max_col_size}} {remove9XXFromString(col2_str)}")
            log(line.middot1s)
            log(f">>> {cWhite(f'Statistics of elapsed time of the last {timeStats.window_size} requests:')}")
            log("")
            stats = timeStats.stats()
            min,avg,max,pct50,pct75,pct90,pct99 = stats.values()
            min_avg_max = f"{min}  {avg}  {max}"
            requests_per_sec, sec_per_requests = counterAverage.get_average()
            requests_per_sec = 'Paused!' if G.event_pause.is_set() else '%.0f'%(requests_per_sec)
            a = Table(cols=7,max_size=max_size,with_border=False,border_size=0).head(['Total','Req/Sec',' Min       Avg       Max'.center(len(min_avg_max)),'50th pct','75th pct','90th pct','99th pct']).row([counter.value,requests_per_sec,min_avg_max,pct50,pct75,pct90,pct99]).get_table()
            [log(f"{line}") for line in a]
            log(line.single)
    except Exception as ERR:
        logDebug(f"httpStats.asdict: {httpStats.asdict}")
        logDebug(f"displayFullHttpStats: {str(ERR)}")

def finishApplication():
    displayFullHttpStats()
    quit()

def displayHelp():
# {line.double}
#  {__doc__}
    help_text = f"""{line.single}
  Control keys available:
  {line.middot[:23]}
    {G.light_up}   -> Increases the time interval between requests in +10% (slower)
    {G.light_down}   -> Decreases the time interval between requests in -10% (faster)
    {G.light_right}   -> Increase the burst of requests (faster)
    {G.light_left}   -> Reduces the burst of requests (slower)
   +/-  -> Increase/Decrease the timeout in +/- 10%
   < >  -> Increase/Decrease the number of threads
    C   -> Displays information about the current configuration
    P   -> Pause/Resume the application
    M   -> Shows Memory usage and CPU usage information
    V   -> Start/stop viewing each request sent and returned status code
    B   -> The same as V key, but also include the returned response body
    S   -> Displays a detailed report about success, failures, average time, etc
    R   -> Reset all statistics data
    F   -> Finish the application by displaying the statistics
  ENTER -> Displays statistics of the current rate of requests per second
  ESC/Q -> Exit the application
    H   -> Show this help message
{line.single}
"""
    [log(line) for line in help_text.splitlines()]

##################################################################################################################################
##################################################################################################################################

 #  #   ##   #  #  ####        ###   ####   ##   #  #  ####   ### #####   ###
 ####  #  #  # #   #           #  #  #     #  #  #  #  #     #      #    #
 ####  #  #  ##    ###         ###   ###   #  #  #  #  ###    ##    #     ##
 #  #  ####  # #   #           # #   #     #  #  #  #  #        #   #       #
 #  #  #  #  #  #  ####        #  #  ####   ##    ##   ####  ###    #    ###
                                             ##

class threadMakeRequestsURLLib(threading.Thread):
    def __init__(self,timeStats,httpStats):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.timeStats = timeStats
        self.httpStats = httpStats
        zfill_len = len(str(len(G.thread_list))) if len(str(len(G.thread_list))) >= 2 else 2
        self.text_id = f"[#{self.name.split('-')[1].zfill(zfill_len)}]"
    def run(self):
        self.method, self.url = G.config.method, G.config.url
        if self.method == "GET":
            self.post_data = b''
        else:
            self.post_data = str(json.dumps(G.config.post_data,sort_keys=False,ensure_ascii=False,separators=(",",":"))).encode()
        self.template_var = self.extract_template_var(self.url)
        if self.template_var == '%%randomipv4%%':
            self.get_url = self.__get_url_random_ipv4
        elif self.template_var == '%%randomipv6%%':
            self.get_url = self.__get_url_random_ipv6
        elif self.template_var == '%%randomprivateipv4%%':
            self.get_url = self.__get_url_random_private_ipv4
        elif self.template_var.startswith('%%randomint:'):
            try:
                self.template_var = self.extract_template_var(self.url)
                _, self.random_min, self.random_max = self.template_var.replace("%","").split(":")
            except Exception as ERR:
                raise StressAnAPIException(f"Failed in config url: invalid url variable '{self.template_var}' - usage: %%randomint:val_min:val_max%% - {str(ERR)}")
            try:
                self.random_min = int(self.random_min)
                self.random_max = int(self.random_max)
            except Exception as ERR:
                raise StressAnAPIException(f"Failed in '{self.template_var}' - invalid integer values for min and max - usage: %%randomint:val_min:val_max%% - {str(ERR)}")
            self.get_url = self.__get_url_random_int
        
        req = urllib.request.Request(url=self.url,method=self.method)
        ##──── configure StressAnAPI useragent if the user has not configured any other
        if 'user-agent' not in [key.lower() for key,val in G.config.headers.items()]:
            req.add_header('User-Agent',G.default_user_agent)
        ##─────────────────────────────────────────────────────────────────────────────
        for header_key, header_value in G.config.headers.items():
            req.add_header(header_key,header_value)
            
        while True:
            if G.event_quit.is_set() or self.stop.is_set():
                break
            while G.event_pause.is_set():
                time.sleep(1)
                if self.stop.is_set():
                    break
            for I in range(G.config.burst):
                if self.stop.is_set(): break
                try:
                    with elapsedTimer() as elapsed:
                        req.full_url = next(self.get_url())
                        req.data = self.post_data
                        response_code,response_body = self.urllib_open(req,G.config.timeout)
                    self.timeStats.save(elapsed.time)
                except Exception as ERR:
                    logDebug(f"urllib_get error: {str(ERR)}")
                finally:
                    counter.incr()
                    logResponse(self.text_id,self.method,req.full_url,response_code,response_body,elapsed.text())
            time.sleep(G.config.interval)

    # @showElapsedTimeAverageDecorator(5000)
    def urllib_open(self,urllib_request,timeout):
        try:
            with urllib.request.urlopen(urllib_request,timeout=timeout) as response:
                response_code = response.getcode()
                response_text = response.readline().strip().decode() if response_code not in [202,204] else '\b'
        except Exception as ERR:
            response_code,response_text = getErrorResponseCode(str(ERR)),shortenErrorMessage(str(ERR),128)
            logDebug(f"urllib_open: {str(ERR)}")
        finally:
            counterAverage.mark()
            self.httpStats.save(response_code)
            return response_code,response_text

    def identify(self):
        return self.name,self.native_id

    def join(self):
        try:
            self.stop.set()
            threading.Thread.join(self)
        except Exception as ERR:
            log(f"Unable to join thread {self.name} - {self.native_id}")
        return self.name,self.native_id

    def extract_template_var(self,text_string):
        try:
            match = re.search(r"(\%\%.*\%\%)",text_string)
            return match.group(1) if match else ''
        except Exception as ERR:
            logDebug(f"extract_template_var: {str(ERR)}")
            return ''
        
    def __get_url_random_int(self):
        yield self.url.replace(self.template_var,str(random.randint(self.random_min,self.random_max)))
    def __get_url_random_ipv4(self):
        yield self.url.replace(self.template_var,int2ipv4(random.randint(16777216,3758096383)))
    def __get_url_random_ipv6(self):
        yield self.url.replace(self.template_var,':'.join([f'{random.randint(0, 0xffff):04x}' for _ in range(8)]))
    def __get_url_random_private_ipv4(self):
        yield self.url.replace(self.template_var,int2ipv4(random.choice([random.randint(167772160,184549375),random.randint(3232235520,3232301055),random.randint(2886729728,2887778303)])))
    @showElapsedTimeAverageDecorator()
    def get_url(self):
        yield self.url


##################################################################################################################################
##################################################################################################################################

  ##   ###    ###  ###    ##   ###    ###  ####        #  #  ####  #  #  #  #
 #  #  #  #  #     #  #  #  #  #  #  #     #           ####  #     ## #  #  #
 #  #  ###   # ##  ###   #  #  ###    ##   ###         ####  ###   # ##  #  #
 ####  # #   #  #  #     ####  # #      #  #           #  #  #     #  #  #  #
 #  #  #  #   ###  #     #  #  #  #  ###   ####        #  #  ####  #  #   ##

class classArgparseHelpFormatter(argparse.HelpFormatter):
    def format_help(self):
        help = self._root_section.format_help()
        if help:
            help = self._long_break_matcher.sub('\n\n', help)
            help = help.strip('\n') + '\n'
            help = help.replace("<br>","\n")
        return help

    def add_usage(B,usage,actions,groups,prefix=None):
        A=prefix
        if A is None:A='Usage: '
        return super(classArgparseHelpFormatter,B).add_usage(usage,actions,groups,A)

    def _format_action(self, action):
        self._max_help_position = 40
        self._indent_increment = 2
        self._width = classTerminal().max_width
        return super(classArgparseHelpFormatter, self)._format_action(action)

class myArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        self._print_message(self.format_help()+"\n", file)

def getArgParseMenu():
    parser = myArgumentParser(
        formatter_class=classArgparseHelpFormatter,
                                     description=cWhite(__appname__+" v"+__version__+" - "+__descr__+" - "+__url__),
                                     add_help=False,
                                     allow_abbrev=True,
                                     prog=current_filename)

    main = parser.add_argument_group("Main Options")
    main.add_argument('--conf',dest="configfile",metavar="<json file>",action="store",default="",help='Provide the file name of a configuration file. Use the option --template to see a template.')
    main.add_argument('-c',dest="configfile",action="store",help=argparse.SUPPRESS)

    template = parser.add_argument_group("Configuration Template")
    template.add_argument('--template',action="store_true", default=False, help="Displays a configuration template. Required values are 'url' and 'method'.")

    optional = parser.add_argument_group("More options")
    optional.add_argument('--nodate','--nodatetime', action="store_true", default=False, help="Hide the date/time information at the begin of the output lines.")
    optional.add_argument('--debug','-d', dest="debug", action='store_true', default=False, help="Print debug information do stdout/syslog. Or use 'export STRESSANAPI_DEBUG=1'.")
    optional.add_argument('--help','-h', action='help', help='Show a help message about the allowed commands.')
    optional.add_argument('--version',dest="version", action='store_true', default=False, help=argparse.SUPPRESS)
    return parser

##################################################################################################################################
##################################################################################################################################

 #  #   ##   ###   #  #         ###  #      ##    ###   ###
 ####  #  #   #    ## #        #     #     #  #  #     #
 ####  #  #   #    # ##        #     #     #  #   ##    ##
 #  #  ####   #    #  #        #     #     ####     #     #
 #  #  #  #  ###   #  #         ###  ####  #  #  ###   ###

class classStressAnAPI:
    def __init__(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        try:
            G.event_quit.set()
            G.event_pause.clear()
            logResponse.__code__ = logResponseEmpty.__code__
            log(line.middot)
            log(cWhite(f">>> Exiting {__appname__} as requested - PID: {os.getpid()} - {dt.now().strftime(G.date_format_no_milisec)}"))
            log(line.middot)
        finally:
            cursor.show()
            os.system('stty sane')
            sys.exit(0)

##################################################################################################################################
##################################################################################################################################

 #  #   ##   ###   #  #        ####  #  #  #  #   ### #####  ###    ##   #  #
 ####  #  #   #    ## #        #     #  #  ## #  #      #     #    #  #  ## #
 ####  #  #   #    # ##        ###   #  #  # ##  #      #     #    #  #  # ##
 #  #  ####   #    #  #        #     #  #  #  #  #      #     #    #  #  #  #
 #  #  #  #  ###   #  #        #      ##   #  #   ###   #    ###    ##   #  #

##################################################################################################################################
##################################################################################################################################

def startApp():
    global httpStats, timeStats, counter, counterAverage
    log(line.middot)
    log(cWhite(f">>> Starting {__appname__} v{__version__} - PID: {os.getpid()} - {dt.now().strftime(G.date_format_no_milisec)}"))
    log(line.middot)
    log(f">>> Loaded configuration from {cWhite(str(G.config.config_file))} [{G.config.elapsed_load_time}]")
    if G.logger is not None:
        log(f"  - Logging to syslog server at {cWhite(G.config.syslog_server['url'])}")
    displayConfig()
    log(cGrey(line.middot1s))
    log(f">>> All done in {'%.6f'%(time.monotonic()-G.start_time)}'s! {cWhite(f'It{G.singleQuote}s Showtime!')}")
    log(cGrey(line.middot1s))
    log(cWhite(f"Use the arrow keys to increase/decrease the speed. Press H for a quick help or ESC/Q to quit.".center(classTerminal().width)))
    log(cGrey(line.middot1s))

    threading.Thread(target=threadGarbageCollector,daemon=True).start()

    counter = AtomicCounter()
    counterAverage = AtomicAverageCounter(max_window_size=G.stats_window_size)
    counterAverage.start()

    timeStats = classTimeStats(window_size=G.stats_window_size)
    httpStats = classHttpStats()

    for I in range(G.config.threads):
        try:
            ThreadMakeRequests = threadMakeRequestsURLLib(timeStats=timeStats,httpStats=httpStats)
        except Exception as ERR:
            logDebug(str(ERR))
        ThreadMakeRequests.setDaemon(True)
        G.thread_list.append(ThreadMakeRequests)
        ThreadMakeRequests.start()

    try:
        view_response = False
        view_response_body = False
        cursor.hide()
        while True:
            k = readKey()
            k = k.lower()
            # logDebug(f"KEY PRESSED: {k}")
            if k in ['esc','q']:
                quit()
            else:
                cursor.hide()
                if k == 'f':
                    finishApplication()
                    break
                elif k == 'h':
                    displayHelp()
                elif k == 'up':
                    increaseInterval()
                    counterAverage.reset()
                elif k == 'down':
                    decreaseInterval()
                    counterAverage.reset()
                elif k == 'right':
                    increaseBurst()
                    counterAverage.reset()
                elif k == 'left':
                    decreaseBurst()
                    counterAverage.reset()
                elif k == 'plus':
                    increaseTimeout()
                elif k == 'minus':
                    decreaseTimeout()
                elif k == 'greaterthan':
                    increaseThreads()
                elif k == 'lowerthan':
                    decreaseThreads()
                elif k == 'm':
                    keyMemInfo()
                elif k == 'p':
                    pause()
                elif k == 'c':
                    displayCurrentConfiguration()
                elif k == 'return':
                    displayAverageTimeStats()
                elif k == 's':
                    displayFullHttpStats()
                elif k == 'r':
                    resetStats()
                elif k == 'b':
                    view_response_body = not view_response_body
                    view_response = False
                    if view_response_body:
                        logResponse.__code__ = _logResponseBody.__code__
                    else:
                        logResponse.__code__ = logResponseEmpty.__code__
                elif k == 'v':
                    view_response = not view_response
                    view_response_body = False
                    if view_response:
                        logResponse.__code__ = _logResponse.__code__
                    else:
                        logResponse.__code__ = logResponseEmpty.__code__
                else:
                    continue
    except (KeyboardInterrupt,SystemExit):
        pass
    except Exception as ERR:
        logDebug(f"startApp: {str(ERR)}")
        raise StressAnAPIException(str(ERR)) from None
    finally:
        quit()

def main_function():
    if ('-d' in sys.argv) or ('--debug' in sys.argv):
        G.DEBUG = True
    if G.DEBUG:
        sys.tracebacklimit = 0
    else:
        logDebug.__code__ = logEmpty.__code__
    if (('--nodate' in sys.argv) and ('--notime' in sys.argv)) or ('--nodatetime' in sys.argv):
        getLogDate.__code__ = getLogDateEmpty.__code__
    elif '--nodate' in sys.argv:
        G.date_format = G.date_format_no_date
    elif '--notime' in sys.argv:
        G.date_format = G.date_format_no_time

    parser = getArgParseMenu()
    args = parser.parse_args()

    if args.version:
        print(f"\n{__appname__} v{__version__} ({__release__}) - {__descr__}")
        print(f"Github.: {__url__}\n")
        sys.exit(0)

    if G.DEBUG:
        args.debug = True

    G.argsvars = vars(args)

    if args.template and args.configfile == '':
        ppJson(G.default_template,compact=False)
    elif args.configfile == '' and not args.template:
        parser.print_help()
    elif args.configfile:
        if not os.path.isfile(args.configfile):
            raise StressAnAPIException(f'Cannot locate the file {args.configfile}')
        else:
            if not validateConfigFile(args.configfile):
                raise StressAnAPIException(f'Invalid configuration found at {args.configfile}') from None
            else:
                if G.config.syslog_server != {}:
                    try:
                        sys.tracebacklimit = 0
                        G.logger = getSyslogLogger(__appname__,G.config.syslog_server['scheme'],G.config.syslog_server.get('host',''),G.config.syslog_server.get('port',0),facility=G.config.syslog_server.get('facility_number',0))
                        log.__code__ = logSyslog.__code__
                        logResponse.__code__ = logResponseEmpty.__code__ = logResponseSyslog.__code__
                        logDebug.__code__ = logDebugSyslog.__code__ if G.DEBUG else logDebug.__code__
                    except Exception as ERR:
                        raise StressAnAPIConfigException(str(ERR)) from None
                logDebug(f"argparser vars: {G.argsvars}")
                try:
                    with classStressAnAPI() as StressAnAPI:
                        return startApp()
                except Exception as ERR:
                    logDebug(f"Failed in classStressAnAPI() as StressAnAPI: {str(ERR)}")
    else:
        parser.print_help()

##################################################################################################################################
##################################################################################################################################

if __name__ == '__main__':
    signal.signal(signal.SIGINT, receivedSignalSTOP)   # to make asyncio/thread stop on first CTRL+C
    signal.signal(signal.SIGTERM, receivedSignalSTOP)  # to make asyncio/thread stop on first CTRL+C
    signal.signal(signal.SIGPIPE, received_SIGPIPE)    # intercept the broken pipe signal and avoid the application crash
    sys.exit(main_function())