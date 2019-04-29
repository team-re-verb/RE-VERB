import redis
import time
import traceback
from os import environ
from daiarization import get_diarization

def ServerMain():
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
                    print(f"Got file name: {command[1]}")
                    diarization_results = get_diarization(command[1])
                    r.publish("diarization_node", f"{diarization_results}")
                
    except Exception as e:
        print(e)


if __name__ == "__main__":
    ServerMain()