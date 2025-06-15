import redis
import logging
from functools import wraps
import traceback
from datetime import timedelta, datetime
def start_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        self = args[0]
        if self.r is None:
            raise RuntimeError('redis não foi iniciado, use .start() para iniciar o redis antes de chamar esse metodo')
        return f(*args, **kwargs)
    return wrapped

class CacheHandler:
    def __init__(self, limit, time_stamp, expire_limit=5, event_expire_time=0.5, host="localhost", port=6379):
        try:
            if self.check_redis_parameters(host, port) and self.check_initial_parameters(limit, time_stamp, expire_limit, event_expire_time):
                self.r = None
                self.host = host
                self.port = port
                self.limit = limit
                self.time_stamp = time_stamp
                self.expire_limit = expire_limit*60
                self.event_expire_time = event_expire_time
            else:
                raise Exception(f'os parametros fornecidos são invalidos, o cache não pode ser executado')
        except Exception as e:
            logging.error(f'erro ao iniciar o redis no cache, identificador do erro: {e} \n{traceback.format_exc()}')

    def start(self):
        try:
            self.r = redis.Redis(host=self.host, port=self.port, db=0)
            self.r.ping()
        except Exception as e:
            logging.error(f'erro ao iniciar o redis no cache, identificador do erro: {e} \n{traceback.format_exc()}')
            self.r = None
    
    @staticmethod
    def check_redis_parameters(host, port):
        if host and port:
            if isinstance(host, str) and isinstance(port, int):
                return True
        return False
    
    @staticmethod
    def check_initial_parameters(limit, time_stamp, expire_limit, event_expire_time):
        if limit is not None and time_stamp is not None and expire_limit is not None and event_expire_time is not None:
            if isinstance(limit, int) and isinstance(time_stamp, int) and isinstance(expire_limit, int) and isinstance(event_expire_time, (int, float)):
                if limit >= 0 and time_stamp >= 0 and expire_limit >= 0 and event_expire_time >= 0:
                    return True
        return False
    
    @staticmethod
    def validate_event_expire_time(event_expire_time):
        return event_expire_time is not None and isinstance(event_expire_time, (int, float)) and event_expire_time > 0
    
    @staticmethod
    def sanitize_event_expire_time(event_expire_time):
        px = int(event_expire_time*1000)
        return px 
     
    @start_required
    def set_login_rate_limit(self, ip):
        try:
            key = f"black_list:{ip}"
            if not self.r.exists(key):
                self.r.set(key, 1)
                self.r.expire(key, self.time_stamp)
            else:
                self.r.incr(key)
            
            attempts = int(self.r.get(key))
            if attempts > self.limit:
                expire_time = min(self.time_stamp * (attempts - self.limit), self.expire_limit)
                self.r.expire(key, expire_time)
        except Exception as e:
            logging.error(f'erro ao definir o login rate, identificador do erro: {e} \n{traceback.format_exc()}')
            
    @start_required
    def is_black_listed(self, ip):
        try:
            key = f"black_list:{ip}"
            attempts_byte = self.r.get(key)
            if attempts_byte is None:
                return False
            
            attempts = int(attempts_byte)
            return attempts > self.limit
        except Exception as e:
            logging.error(f'erro ao checar se o usuario esta no blacklist, identificador do erro: {e} \n{traceback.format_exc()}')
            return False
    
    @start_required
    def ws_cache_login(self, sid, token):
        try:
            key = f'login:{sid}'
            self.r.set(key, token)
            return True
        except Exception as e:
            logging.error(f'erro no cache_websocket de sessões identificador do erro: {e} \n{traceback.format_exc()}')
            return False
        
    @start_required
    def ws_cache_get_user(self, sid):
        try:
            key = f'login:{sid}'
            token_byte = self.r.get(key)
            if token_byte is None:
                return None
            return token_byte.decode('utf-8')
        except Exception as e:
            logging.error(f'erro ao buscar token de usuario: {e} \n{traceback.format_exc()}')
            return None

    @start_required
    def ws_event_throttle(self, sid, event_name, event_expire_time):
        try:
            if not self.validate_event_expire_time(event_expire_time):
                raise Exception(f'o valor de parametro fornecidos no event_expire_time é invalido, certifiquesse de passar um int ou um float')
            
            px = self.sanitize_event_expire_time(event_expire_time)
            key = f'{event_name}:{sid}'
            if not self.r.exists(key):
                
                self.r.set(key, 1, px=px)
                return True
            return False
        except Exception as e:
            logging.error(f'erro ao aplicar o throttle do evento: {e} \n{traceback.format_exc()}')
            return False

    @start_required
    def ws_cache_logout(self, sid):
        try:
            key = f'login:{sid}'
            token = self.r.get(key)
            if token is not None:
                self.r.delete(key)
                return token.decode('utf-8')
            return None            
        except Exception as e:
            logging.error(f'erro ao apagar e buscar o token de usuario: {e} \n{traceback.format_exc()}')
            return None