import socket, re, time, json, argparse, os
from types import SimpleNamespace
from decouple import config

class TwitchChatIRC():
	__HOST = 'irc.chat.twitch.tv'

	__DEFAULT_NICK = 'justinfan67420'
	__DEFAULT_PASS = 'SCHMOOPIIE'

	# print(os.environ.get('NICK'))
	# exit()
	
	__NICK = config('NICK', __DEFAULT_NICK)
	__PASS = config('PASS', __DEFAULT_PASS)  # https://twitchapps.com/tmi/
	__PORT = 6667

	__PATTERN = re.compile(r'@(.+?(?=\s+:)).*PRIVMSG[^:]*:([^\r\n]*)')

	def __init__(self):
		
		# create new socket
		self.__SOCKET = socket.socket()
		
		# start connection
		self.__SOCKET.connect((self.__HOST, self.__PORT))
		print('Connected to',self.__HOST,'on port',self.__PORT)

		# log in
		self.__send_string('CAP REQ :twitch.tv/tags')
		self.__send_string('PASS ' + self.__PASS)
		self.__send_string('NICK ' + self.__NICK)
	
	def __send_string(self, string):
		self.__SOCKET.send((string+'\r\n').encode('ISO-8859-1'))

	def __print_message(self, message):
		print('['+message['tmi-sent-ts']+']',message['display-name']+':',message['message'])

	def __recvall(self, buffer_size):
		data = b''
		while True:
			part = self.__SOCKET.recv(buffer_size)
			data += part
			if len(part) < buffer_size:
				break
		return data.decode('ISO-8859-1')

	__CURRENT_CHANNEL = None
	def __join_channel(self,channel_name):
		channel_lower = channel_name.lower()

		if(self.__CURRENT_CHANNEL != channel_lower):
			self.__send_string('JOIN #{}'.format(channel_lower))
			self.__CURRENT_CHANNEL = channel_lower

	def listen(self, channel_name, messages = [], timeout=None, message_timeout=1.0, on_message = None, buffer_size = 4096, message_limit = None, output=None):
		self.__join_channel(channel_name)

		# flush?

		# message_limit
		# set variables
		# self.__MESSAGE_TIMEOUT = message_timeout
		self.__SOCKET.settimeout(message_timeout)

		if(on_message is None):
			on_message = self.__print_message
		


		print('Begin retrieving messages:')

		time_since_last_message = 0
		readbuffer = ''
		try:
			while True:
				try:
					new_info = self.__recvall(buffer_size)
					readbuffer += new_info

					if('PING :tmi.twitch.tv' in readbuffer):
						self.__send_string('PONG :tmi.twitch.tv')

					matches = list(self.__PATTERN.finditer(readbuffer))

					if(matches):
						time_since_last_message = 0

						if(len(matches) > 1):
							matches = matches[:-1] # assume last one is not complete

						last_index = matches[-1].span()[1]
						readbuffer = readbuffer[last_index:]

						for match in matches:
							data = {}
							for item in match.group(1).split(';'):
								keys = item.split('=',1)
								data[keys[0]]=keys[1]
							data['message'] = match.group(2)

							messages.append(data)

							if(message_limit is not None and len(messages) >= message_limit):
								break

							if(callable(on_message)):
								try:
									on_message(data)
								except:
									raise Exception('Incorrect number of parameters for function '+on_message.__name__)
				
				except socket.timeout:
					if(timeout != None):
						time_since_last_message += message_timeout
					
						if(time_since_last_message >= timeout):
							print('No data received in',timeout,'seconds. Timing out.')
							break
		
		except KeyboardInterrupt:
			print('Interrupted by user.')
			
		except Exception as e:
			print('Unknown Error:',e)
			raise e		

		self.__SOCKET.close()
		print('Connection closed')

		return messages

	def send(self, channel_name, message):
		self.__join_channel(channel_name)

		# check that is using custom client id, not standard
		if(self.__NICK == self.__DEFAULT_NICK):
			raise Exception('Unable to send messages with default user.')
		else:
			self.__send_string('PRIVMSG #{} :{}'.format(self.__NICK.lower(),message))
			print('PRIVMSG #{} :{}'.format(self.__NICK.lower(),message))





if __name__ == '__main__':
	

	parser = argparse.ArgumentParser(description='Retrieve Twitch chat in real time. Use "Ctrl + C" to manually end the program or set a timeout.')

	parser.add_argument('channel_name', help='Twitch channel name (username)')
	parser.add_argument('--dynamic_buffer', action='store_false', help='dynamically adjust buffer size if there is too much data (default: True)')
	parser.add_argument('-buffer_size','-b', default=2**12, type=int, help='initial buffer size (default: 4096 bytes = 4 KB)')
	parser.add_argument('-max_buffer_size','-m', default=2**20, type=int, help='maximum buffer size (default: 1048576 bytes = 1 MB)')
	parser.add_argument('-timeout','-t', default=None, type=float, help='time in seconds needed to close connection after not receiving any new data (default: None = no timeout)')
	parser.add_argument('-message_timeout','-mt', default=1.0, type=float, help='time in seconds between checks for new data (default: 1 second)')

	parser.add_argument('-output','-o', default=None, help='output json file (default: None)')

	twitch_chat_irc = TwitchChatIRC()
	args = parser.parse_args()
	# # https://dev.twitch.tv/docs/irc/guide
	# a.listen('pokerstars')
# a.send('xenova','hello there')

# def get_messages(channel_name, on_message = None, dynamic_buffer=True, buffer_size=2**12, max_buffer_size=2**20, timeout=None, message_timeout=1.0, output=None):
# 	return main(SimpleNamespace(**locals()),on_message)
# if(args.output != None):
# 		with open(args.output, 'w') as fp:
# 			json.dump(messages, fp)
	
# 		print('Wrote messages to',args.output)
	
# 	return messages
# user = sys.argv[1]

# f = open('output/'+user+'.txt','a+',encoding='ISO-8859-1', buffering=1)

# def write_to_file(message):
# 	print('\t',message['message'])
# 	print(message['message'],file=f, flush=True)

# get_messages(user, write_to_file)

# f.close()