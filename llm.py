# OpenAI API key
import hashlib
import os
import openai
import logging
from retry import retry
import functools
import pickle

openai.api_key = os.getenv("OPENAI_API_KEY")
DEBUG_CACHE = False
CACHE_DIR = "openai_cache"
if not os.path.exists(CACHE_DIR):
    logging.info("making cache dir")
    os.makedirs(CACHE_DIR)

def disk_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not DEBUG_CACHE:
            return func(*args, **kwargs)
        logging.info("cache check..")
        args_bytes = pickle.dumps(args)
        kwargs_bytes = pickle.dumps(sorted(kwargs.items()))
        cache_key = f"{func.__name__}_{hashlib.md5(args_bytes + kwargs_bytes).hexdigest()}"        
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.pkl")
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as cache_file:
                logging.info(f"cache hit!\n")
                return pickle.load(cache_file)
        logging.info("cache miss..")
        result = func(*args, **kwargs)
        with open(cache_path, "wb") as cache_file:
            pickle.dump(result, cache_file)
        return result
    return wrapper

##our main LM call, it is decorated to cache the results to disk and retry on failure
@disk_cache
@retry(tries=3, delay=1)
def openAI(history, temp=0, max_tokens=100, model="gpt-4"):
    #gpt-3.5-turbo or gpt-4
    response = openai.ChatCompletion.create(model=model,messages=history,temperature=temp,max_tokens=max_tokens)
    return response['choices'][0]['message']['content']

