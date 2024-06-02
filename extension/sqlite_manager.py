#!/usr/bin/env -S python3 -u

import sys
import json
import struct
import logging
import sqlite3

# Read a message from stdin and decode it.
def getMessage():
    try:
        rawLength = sys.stdin.buffer.read(4)
        if len(rawLength) == 0:
            sys.exit(0)
        messageLength = struct.unpack('@I', rawLength)[0]
        message = sys.stdin.buffer.read(messageLength).decode('utf-8')
        return json.loads(message)
    except Exception as e:
        logging.error(f"Error while getting message: {e}")
        return None

# Encode a message for transmission,
# given its content.
def encodeMessage(messageContent):
    try:
        # https://docs.python.org/3/library/json.html#basic-usage
        # To get the most compact JSON representation, you should specify
        # (',', ':') to eliminate whitespace.
        # We want the most compact representation because the browser rejects # messages that exceed 1 MB.
        encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
        encodedLength = struct.pack('@I', len(encodedContent))
        return {'length': encodedLength, 'content': encodedContent}
    except Exception as e:
        logging.error(f"Error while encoding message: {e}")
        return None

# Send an encoded message to stdout
def sendMessage(encodedMessage):
    try:
        sys.stdout.buffer.write(encodedMessage['length'])
        sys.stdout.buffer.write(encodedMessage['content'])
        sys.stdout.buffer.flush()
    except Exception as e:
        logging.error(f"Error while sending message: {e}")

# Setup logging
logging.basicConfig(
    filename='native_messaging_host.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(message):
    logging.debug(message)

def init_db():
    try:
        con = sqlite3.connect('hyperlinks.db')
        c = con.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS hyperlinks (
                     host TEXT, 
                     link TEXT, 
                     frequency INTEGER, 
                     PRIMARY KEY (host, link)
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS meta (
                     key TEXT PRIMARY KEY, 
                     value INTEGER
                     )''')
        con.commit()
        con.close()
        log("Initialized the database and created tables if they didn't exist.")
    except Exception as e:
        logging.error(f"Error while initializing database: {e}")

def insert_hyperlinks(data, visited, hyper):
    try:
        con = sqlite3.connect('hyperlinks.db')
        c = con.cursor()
        for obj in data:
            for site, links in obj.items():
                for link, freq in links.items():
                    c.execute('''INSERT INTO hyperlinks (host, link, frequency) 
                                 VALUES (?, ?, ?) 
                                 ON CONFLICT(host, link) 
                                 DO UPDATE SET frequency = frequency + excluded.frequency''', 
                              (site, link, freq))
                    log(f"Inserted/Updated hyperlink: host={site}, link={link}, frequency={freq}")

        c.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", ('visited', visited))
        c.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", ('hyper', hyper))
        con.commit()
        con.close()
        log(f"Inserted/Updated meta: visited={visited}, hyper={hyper}")
    except Exception as e:
        logging.error(f"Error while inserting hyperlinks: {e}")

try:
    init_db()
    while True:
        receivedMessage = getMessage()
        if receivedMessage:
            if 'visited' in receivedMessage:
                log(f"Received message: {receivedMessage}")
                insert_hyperlinks(receivedMessage['data'], receivedMessage['visited'], receivedMessage['hyperlinks'])
                sendMessage(encodeMessage({'status': 'success'}))
            else:
                sendMessage(encodeMessage({'status': 'data not found'}))
except Exception as e:
    logging.error(f"Unhandled error: {e}")
