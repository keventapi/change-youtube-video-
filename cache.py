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
    def __init__(self, login_limit, login_time_stamp_in_seconds, login_expire_limit_in_minutes=5,
                 event_expire_time_in_seconds=0.5, 
                 create_account_limit=5, create_account_time_stamp_in_days=1, create_account_expire_limit_in_days=30,
                 host="localhost", port=6379):
        try:
            if self.check_if_its_a_number_parameters(login_limit, login_time_stamp_in_seconds, login_expire_limit_in_minutes,
                                                     event_expire_time_in_seconds,
                                                     create_account_limit, create_account_time_stamp_in_days, create_account_expire_limit_in_days) and self.check_redis_parameters(host, port):
                self.r = None
                self.host = host
                self.port = port
                
                self.login_limit = login_limit
                self.login_time_stamp_in_seconds = login_time_stamp_in_seconds
                self.login_expire_limit_in_minutes = self.minutes_to_seconds(login_expire_limit_in_minutes) 
                
                self.event_expire_time_in_seconds = event_expire_time_in_seconds
                
                self.create_account_limit = create_account_limit
                self.create_account_time_stamp_in_days = self.days_to_seconds(create_account_time_stamp_in_days)
                self.create_account_expire_limit_in_days = self.days_to_seconds(create_account_expire_limit_in_days)
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
    def seconds_to_milliseconds(event_expire_time_in_seconds):
        return int(event_expire_time_in_seconds*1000)
    
    @staticmethod
    def minutes_to_seconds(minutes):
        return int(minutes*60)
    
    @staticmethod
    def days_to_seconds(days):
        return int(days*60*60*24)
    
    @staticmethod
    def check_if_its_a_number_parameters(*args):
        for i in args:
            if i is not None and isinstance(i, (int, float)) and i > 0:
                continue
            return False
        return True
    
    @staticmethod
    def check_redis_parameters(host, port):
        if host and port:
            if isinstance(host, str) and isinstance(port, int):
                return True
        return False
    
    @staticmethod
    def validate_event_expire_time(event_expire_time_in_seconds):
        return event_expire_time_in_seconds is not None and isinstance(event_expire_time_in_seconds, (int, float)) and event_expire_time_in_seconds > 0
     
    @start_required
    def set_login_rate_limit(self, ip):
        try:
            key = f"black_list:{ip}"
            if not self.r.exists(key):
                self.r.set(key, 1, ex=self.login_time_stamp_in_seconds)
                attempts = 1
            else:
                attempts = self.r.incr(key)
            
            if attempts > self.login_limit:
                expire_time = min(self.login_time_stamp_in_seconds * (attempts - self.login_limit), self.login_expire_limit_in_minutes)
                self.r.expire(key, expire_time)
        except Exception as e:
            logging.error(f'erro ao definir o login rate, identificador do erro: {e} \n{traceback.format_exc()}')
            
    @start_required
    def is_black_listed(self, ip):
        try:
            key = f"black_list:{ip}"
            attempts_byte = self.r.get(key)
            if not attempts_byte:
                return False
            
            attempts = int(attempts_byte.decode('utf-8'))
            return attempts > self.login_limit
        except Exception as e:
            logging.error(f'erro ao checar se o usuario esta no blacklist, identificador do erro: {e} \n{traceback.format_exc()}')
            return False
    
    @start_required
    def create_account_limit_handler(self, ip):
        try:
            key = f"create_account_limit:{ip}"
            if not self.r.exists(key):
                self.r.set(key, 1, ex=self.create_account_time_stamp_in_days)
                attempts = 1
            else:
                attempts = self.r.incr(key)
            if attempts > self.create_account_limit:
                expire_time = min(self.create_account_time_stamp_in_days*(attempts - self.create_account_limit), self.create_account_expire_limit_in_days)
                self.r.expire(key, expire_time)
        except Exception as e:
            logging.error(f'erro ao atualizar o limite de criação de contas, identificador do erro: {e} \n{traceback.format_exc()}')
    
    @start_required
    def check_create_account_validation(self, ip):
        try:
            key = f"create_account_limit:{ip}"
            attempts_byte = self.r.get(key)
            if not attempts_byte:
                return True
            attempts = int(attempts_byte.decode('utf-8'))
            return attempts < self.create_account_limit
        except Exception as e:
            logging.error(f'erro ao checar o limite de criação de contas, identificador do erro: {e} \n{traceback.format_exc()}')
            return True
    
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
            if not token_byte:
                return None
            
            return str(token_byte.decode('utf-8'))
        except Exception as e:
            logging.error(f'erro ao buscar token de usuario: {e} \n{traceback.format_exc()}')
            return None

    @start_required
    def ws_event_throttle(self, sid, event_name, event_expire_time_in_seconds):
        try:
            if not self.validate_event_expire_time(event_expire_time_in_seconds):
                event_expire_time_in_seconds = self.event_expire_time_in_seconds
            
            px = self.seconds_to_milliseconds(event_expire_time_in_seconds)
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
            if token:
                self.r.delete(key)
                return token.decode('utf-8')
            return None            
        except Exception as e:
            logging.error(f'erro ao apagar e buscar o token de usuario: {e} \n{traceback.format_exc()}')
            return None