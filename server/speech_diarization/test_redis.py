import redis
import time
import traceback
from os import environ


def RedisExec():
    try:
        r = redis.StrictRedis.from_url(environ['REDIS_URI'])

        p = r.pubsub()
        p.subscribe('diarization_py')

        while True:
            message = p.get_message()

            if message and message['data'] != 1:
                command = message['data'].decode('utf-8').split(':')

                if command[0] == "param":
                    print("sending hello " + command[1])
                    r.publish("diarization_node" , "hello " + command[1])
                elif command[0] == "file":
                    print("sending file sent!")
                    r.publish("diarization_node", "file sent!")
                
    except Exception as e:
        print(e)


if __name__ == "__main__":
    RedisExec()