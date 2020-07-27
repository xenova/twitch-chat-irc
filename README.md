# Twitch Chat IRC
A simple tool used to send and receive Twitch chat messages over IRC with python web sockets. Receiving does not require authentication, while sending does.

### Requirements:
* This tool was created in a Python 3 environment.
* Run `pip install -r requirements.txt` to ensure you have the necessary dependencies.


### Set up
If you intend to send messages, you will require authentication.
1. Go to https://twitchapps.com/tmi/
2. Click "Connect".
3. Log in with Twitch.
4. Copy the generated oath token. Now, there are 2 ways to proceed:
	- (Recommended) Create a file called `.env` and save your credentials here as:
      > NICK=x <br> PASS=y
	  
	  replacing `x` and `y` with your username and oauth token respectively.<br> See `example.env` for an example.

	- Pass your credentials as function/command line arguments. See below for examples.


### Command line:
#### Usage
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

#### Examples
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

##### 5. Send messages to a channel (authentication via .env)
```
python twitch_chat_irc.py --send <channel_name>
```

##### 6. Send messages to a channel (authentication via arguments)
```
python twitch_chat_irc.py --send <channel_name> -username <username> -oauth <oauth_token>
```

#### Example outputs
[JSON Example](examples/example.json):
```
python chat_replay_downloader.py https://www.youtube.com/watch?v=pMsvr55cTZ0 -start_time 14400 -end_time 15000 -output example.json
```

[CSV Example](examples/example.csv):
```
python chat_replay_downloader.py https://www.youtube.com/watch?v=pMsvr55cTZ0 -start_time 14400 -end_time 15000 -output example.csv
```

[Text Example](examples/example.txt):
```
python chat_replay_downloader.py https://www.youtube.com/watch?v=pMsvr55cTZ0 -start_time 14400 -end_time 15000 -output example.txt
```

### Python module

#### Importing the module

```python
import chat_replay_downloader
```
or

```python
from chat_replay_downloader import get_chat_replay, get_youtube_messages, get_twitch_messages
```
The following examples will use the second form of importing.

#### Examples
##### 1. Return list of all chat messages, given a video url:
```python
youtube_messages = get_chat_replay('https://www.youtube.com/watch?v=xxxxxxxxxxx')
twitch_messages = get_chat_replay('https://www.twitch.tv/videos/xxxxxxxxx')
```

##### 2. Return list of all chat messages, given a video id
```python
youtube_messages = get_youtube_messages('xxxxxxxxxxx')
twitch_messages = get_twitch_messages('xxxxxxxxx')
```
<br/>

The following examples use parameters which all three methods (`get_chat_replay`, `get_youtube_messages`, `get_twitch_messages`) have. Both of the following parameters are optional:
* `start_time`: start time in seconds or hh:mm:ss (Default is 0, which is the start of the video)
* `end_time`: end time in seconds or hh:mm:ss (Default is None, which means it will continue until the video ends)

##### 3. Return list of chat messages, starting at a certain time (in seconds or hh:mm:ss)
```python
messages = get_chat_replay('video_url', start_time = 60) # Start at 60 seconds and continue until the end
```

##### 4. Return list of chat messages, ending at a certain time (in seconds or hh:mm:ss)
```python
messages = get_chat_replay('video_url', end_time = 60) # Start at 0 seconds (beginning) and end at 60 seconds
```

##### 5. Return list of chat messages, starting and ending at certain times (in seconds or hh:mm:ss)
```python
messages = get_chat_replay('video_url', start_time = 60, end_time = 120) # Start at 60 seconds and end at 120 seconds
```
