# Twitch Chat IRC
A simple tool used to send and receive Twitch chat messages over IRC with python web sockets. Receiving does not require authentication, while sending does.




## Setup
### Requirements:
* This tool was created in a Python 3 environment.
* Run `pip install -r requirements.txt` to ensure you have the necessary dependencies.

### Authentication
If you intend to send messages, you will require authentication.
1. Go to https://twitchapps.com/tmi/
2. Click "Connect".
3. Log in with Twitch.
4. Copy the generated oath token. Now, there are 2 ways to proceed:
	- (Recommended) Create a file called `.env` and save your credentials here as:
      > NICK=x <br> PASS=y
	  
	  replacing `x` and `y` with your username and oauth token respectively.<br> See `example.env` for an example.

	- Pass your credentials as function/command line arguments. See below for examples.


## Command line:
### Usage
```
usage: twitch_chat_irc.py [-h] [-timeout TIMEOUT]
                          [-message_timeout MESSAGE_TIMEOUT]
                          [-buffer_size BUFFER_SIZE]
                          [-message_limit MESSAGE_LIMIT] [-username USERNAME]
                          [-oauth OAUTH] [--send] [-output OUTPUT]
                          channel_name

Send and receive Twitch chat messages over IRC with python web sockets. For
more info, go to https://dev.twitch.tv/docs/irc/guide

positional arguments:
  channel_name          Twitch channel name (username)

optional arguments:
  -h, --help            show this help message and exit
  -timeout TIMEOUT, -t TIMEOUT
                        time in seconds needed to close connection after not
                        receiving any new data (default: None = no timeout)
  -message_timeout MESSAGE_TIMEOUT, -mt MESSAGE_TIMEOUT
                        time in seconds between checks for new data (default:
                        1 second)
  -buffer_size BUFFER_SIZE, -b BUFFER_SIZE
                        buffer size (default: 4096 bytes = 4 KB)
  -message_limit MESSAGE_LIMIT, -l MESSAGE_LIMIT
                        maximum amount of messages to get (default: None =
                        unlimited)
  -username USERNAME, -u USERNAME
                        username (default: None)
  -oauth OAUTH, -password OAUTH, -p OAUTH
                        oath token (default: None). Get custom one from
                        https://twitchapps.com/tmi/
  --send                send mode (default: False)
  -output OUTPUT, -o OUTPUT
                        output file (default: None = print to standard output)
```

### Examples
#### Receiving messages
##### 1. Output messages from a livestream to standard output
```
python twitch_chat_irc.py <channel_name>
```

##### 2. Output messages from a livestream to a file
```
python twitch_chat_irc.py <channel_name> -output <file_name>
```

If the file name ends in `.json`, the array will be written to the file in JSON format. Similarly, if the file name ends in `.csv`, the data will be written in CSV format. <br> Otherwise, the chat messages will be outputted to the file in the following format:<br>
`[<time>] <author>: <message>`

##### 3. Set a timeout (close connection if no message has been sent in a certain time)
```
python twitch_chat_irc.py <channel_name> -timeout <time_in_seconds> -output <file_name>
```

There are other options, such as `message_timeout` and `buffer_size`, but these normally do not need to be changed. See above for a description of all options.

##### 4. Set a maximum number of messages to read (close connection once limit has been reached)
```
python twitch_chat_irc.py <channel_name> -message_limit <number_of_messages> -output <file_name>
```


#### Example outputs
[JSON Example](examples/example.json):
```
python twitch_chat_irc.py <channel_name> -output example.json
```

[CSV Example](examples/example.csv):
```
python twitch_chat_irc.py <channel_name> -output example.csv
```

[Text Example](examples/example.txt):
```
python twitch_chat_irc.py <channel_name> -output example.txt
```


#### Sending messages
This will open an interactive session which allows you to send messages to the specified channel.
##### 1. Send messages to a channel (authentication via .env)
```
python twitch_chat_irc.py --send <channel_name>
```

##### 2. Send messages to a channel (authentication via arguments)
```
python twitch_chat_irc.py --send <channel_name> -username <username> -oauth <oauth_token>
```
<br>

## Python module

### Importing the module

```python
import twitch_chat_irc
```

### Examples
#### Starting a connection
This allows for both receiving and sending of messages
##### 1. Start a connection with Twitch chat using credentials in `.env` (if any)

```python
connection = twitch_chat_irc.TwitchChatIRC()
```
##### 2. Start a connection with Twitch chat using credentials

```python
connection = twitch_chat_irc.TwitchChatIRC('username','oauth:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
```
#### Receiving messages
The `listen` method returns a list when a `KeyboardInterrupt` is fired, or when a timeout/limit has been reached. The arguments shown below can be used together to form more complex method calls.

##### 1. Get a list of messages from a channel
```python
messages = connection.listen('channel_name')
```

##### 2. Get a list of messages from a channel, stopping after not getting a message for 30 seconds
```python
messages = connection.listen('channel_name', timeout=30)
```

##### 3. Get a list of messages from a channel, stopping after getting 100 messages
```python
messages = connection.listen('channel_name', message_limit=100)
```

##### 4. Write messages from a channel to a file
```python
connection.listen('channel_name', output='file.txt')
```

##### 5. Set a callback function to be fired each time a message is received
```python
def do_something(message):
	print(message)

connection.listen('channel_name', on_message=do_something)
```

#### Sending messages
The `send` method allows for messages to be sent to different channels. This method requires valid authentication to be provided, otherwise an exception will be called.

##### 1. Send a message
```python
message = 'Hello world!'
connection.send('channel_name', message)
```

#### Close connection
The `close_connection` method closes the connection with Twitch chat. No futher messages can be received or sent now.

##### 1. Close a connection
```python
connection.close()
```