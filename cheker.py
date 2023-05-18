from flask import session
from functools import wraps

def check_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs) ->str:
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return "You're NOT logged in."
    return wrapper