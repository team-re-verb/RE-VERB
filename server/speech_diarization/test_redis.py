#!/bin/python

import redis
import time
import traceback


def RedisExec():
    try:
        r = redis.StrictRedis(host='localhost', port=6379)

        p = r.pubsub()
        p.subscribe('diarization_py')
        
        while True:
            message = p.get_message()

            if message and message['data'] != 1:
                command = message['data']
                r.publish("diarization_node" , "hello " + str(command))
                
    except Exception as e:
        print(e)


if __name__ == "__main__":
    RedisExec()