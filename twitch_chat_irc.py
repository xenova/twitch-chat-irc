import socket, re, time, json, argparse, os
from types import SimpleNamespace
from decouple import config

class TwitchChatIRC():
	__HOST = 'irc.chat.twitch.tv'
	__DEFAULT_NICK = 'justinfan67420'
	__DEFAULT_PASS = 'SCHMOOPIIE'
	__PORT = 6667

	__PATTERN = re.compile(r'@(.+?(?=\s+:)).*PRIVMSG[^:]*:([^\r\n]*)')

	__CURRENT_CHANNEL = None

	def __init__(self, username = None, password = None):
		# try get from environment variables (.env)
		self.__NICK = config('NICK', self.__DEFAULT_NICK)
		self.__PASS = config('PASS', self.__DEFAULT_PASS)

		# overwrite if specified
		if(username is not None):
			self.__NICK = username
		if(password is not None):
			self.__PASS = password
		
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

	def __join_channel(self,channel_name):
		channel_lower = channel_name.lower()

		if(self.__CURRENT_CHANNEL != channel_lower):
			self.__send_string('JOIN #{}'.format(channel_lower))
			self.__CURRENT_CHANNEL = channel_lower

	def listen(self, channel_name, messages = [], timeout=None, message_timeout=1.0, on_message = None, buffer_size = 4096, message_limit = None, output=None):
		self.__join_channel(channel_name)
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

							if(callable(on_message)):
								try:
									on_message(data)
								except:
									raise Exception('Incorrect number of parameters for function '+on_message.__name__)
							
							if(message_limit is not None and len(messages) >= message_limit):
								return messages
							
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

		# check that is using custom login, not default
		if(self.__NICK == self.__DEFAULT_NICK):
			raise Exception('Unable to send messages with default user.')
		else:
			self.__send_string('PRIVMSG #{} :{}'.format(self.__NICK.lower(),message))
			print('Sent "{}" to {}'.format(message,channel_name))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Send and receive twitch chat messages using IRC. For more info, go to https://dev.twitch.tv/docs/irc/guide')

	parser.add_argument('channel_name', help='Twitch channel name (username)')
	parser.add_argument('-timeout','-t', default=None, type=float, help='time in seconds needed to close connection after not receiving any new data (default: None = no timeout)')
	parser.add_argument('-message_timeout','-mt', default=1.0, type=float, help='time in seconds between checks for new data (default: 1 second)')
	parser.add_argument('-buffer_size','-b', default=4096, type=int, help='buffer size (default: 4096 bytes = 4 KB)')
	parser.add_argument('-message_limit','-l', default=None, type=int, help='maximum amount of messages to get (default: None = unlimited)')
	
	parser.add_argument('-username','-u', default=None, help='username (default: None)')
	parser.add_argument('-password','-p','-oauth', default=None, help='oath token (default: None). Get custom one from https://twitchapps.com/tmi/')
	
	parser.add_argument('--send', action='store_true', help='send mode (default: False)')
	parser.add_argument('-output','-o', default=None, help='output file (default: None = print to standard output)')

	args = parser.parse_args()

	twitch_chat_irc = TwitchChatIRC(username=args.username,password=args.password)

	if(args.send):
		while True:
			message = input('>>> Enter message (blank to exit): ')
			if(not message):
				break
			twitch_chat_irc.send(args.channel_name, message)
	else:
		messages = twitch_chat_irc.listen(
			args.channel_name,
			timeout=args.timeout,
			message_timeout=args.message_timeout,
			buffer_size=args.buffer_size,
			message_limit=args.message_limit)

		if(args.output != None):
			if(args.output.endswith('.json')):
				with open(args.output, 'w') as fp:
					json.dump(messages, fp)
			else:
				f = open(args.output,'w', encoding='ISO-8859-1')
				for message in messages:
					print('['+message['tmi-sent-ts']+']',message['display-name']+':',message['message'],file=f)
				f.close()

			print('Finished writing',len(messages),'messages to',args.output)