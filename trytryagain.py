
import json
import logging
from llm import openAI


##first some useful parser functions

#an exception to raise when the parser fails that signals to try_try_again to try again
class Complaint(Exception):
    pass

def try_try_again(history, parser=lambda x: x, tries=2, on_fail="raise", temp=0, max_tokens=200, model="gpt-4"):
    """Generate from chatgpt, 
    if the parser fails to parse the response try again with an extended history and a complaint.
    parser takes a string and returns anythign you want. it should raise a Complaint if it fails.
    (parser doesn't need to be a parser -- it can be a filter or discriminator or whatever.)
    if the parser fails after all allowed tries, return on_fail.
    """
    logging.info(f"try_try_again: tries={tries}\n")
    logging.debug(f"  try_try_again: history={history}\n")
    response = openAI(history, temp=temp, max_tokens=max_tokens, model=model)
    history = history+ [{"role": "assistant", "content": response}]         
    try:
        extract = parser(response)
        logging.info(f"try_try_again success: return={extract}\n")
        return extract, history
    except Complaint as e:
        logging.info(f"try_try_again parse fail: complaint={e}, response={response}\n")
        history = history+ [{"role": "user", "content": f"{e}"}]
        if tries<=0:
            #out of tries
            logging.info(f"try_try_again: out of tries, returning on_fail\n")
            return on_fail, history
        else:
            #try again
            return try_try_again(history, parser,tries-1, on_fail)

####below here are some helpful parsers for getting structure data from the response

# def get_json_parser(fields):
#     def json_parser(response):
#         try:
#             #extact a json object from the response
#             response = response[response.find('{'):]
#             response = response[:response.rfind('}')+1]
#             response = json.loads(response)
#         except Exception as e:
#             raise Complaint(f"I just ran your response with json.loads and got this error:\n{e}\nPlease try again!")
#         #check if the json object has the fields we want
#         for field in fields:
#             if field not in response:
#                 raise Complaint(f"Your response JSON doesn't have a {field} field.\nPlease try again!")
#         return response
#     return json_parser

def parse_yesno(response):
    #lowercase and strip punctuation and whitespace
    response = response.lower().strip('.,!?')
    if response in ['yes','no']:
        return response == 'yes'
    else:
        raise Complaint('Response was not yes or no.\nPlease try again!')

def parse_numeral(response):
    #lowercase and strip punctuation and whitespace
    response = response.lower().strip('.,!?')
    #check if response is an integer or a numeral word
    if response.isdigit():
        return int(response)
    if response in ['one','two','three','four','five','six','seven','eight','nine','ten']:
        return ['one','two','three','four','five','six','seven','eight','nine','ten'].index(response)+1
    else:
        raise Complaint('Response was not a numeral.\nPlease try again!')
