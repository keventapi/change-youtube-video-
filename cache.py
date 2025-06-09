import redis
r = redis.Redis(host='localhost', port=6379, db=0)


def set_login_rate_limit(sid, limit, time_stamp):
    if not r.exists(sid):
        r.set(sid, 1)
        r.expire(sid, time_stamp)
    else:
        r.incr(sid)
    
    attempts = int(r.get(sid))
    if attempts > limit:
        r.expire(sid, time_stamp*(attempts - limit))

def is_black_listed(sid, limit):
    attempts_byte = r.get(sid)
    if attempts_byte is None:
        return False
    
    attempts = int(r.get(sid))
    return attempts > limit