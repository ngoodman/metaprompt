"""
This file contains filters to compose to make tasks.
Each filter takes a string and returns a string or raises a Complaint.
"""
import re
from trytryagain import Complaint, parse_numeral, parse_yesno, try_try_again
import functools

####filters to compose to make pseudo users

def fourlines(response):
    #check if response has exactly four lines
    lines = response.split("\n")
    if len(lines) != 4:
        raise Complaint(f"Your response has {len(lines)} lines. It should have exactly four lines (with nothing before them). Please try again!")
    return response

def foursentences(response):
    #check if response has exactly four sentences
    numsentences = len(re.findall(r'[.!?]+', response))
    if numsentences != 4:
        raise Complaint(f"Your response has {numsentences} sentences. It should have exactly four sentences. Please try again!")
    return response

def piratestyle(response):
    #ask gpt if this text sounds like a pirate on a scale of 0 (not at all) to 7 (yarr, very much so)
    hist = [{"role": "system", "content": "You are a discrening pirate enthusiast. Determine the extent to which the input text is piratey. Reply on a scale of 0 (not at all) to 7 (yarr, very much so). Return only a single digit."}, {"role": "user", "content": response}]
    rating, _ = try_try_again(hist, parser=parse_numeral, on_fail="0")
    if int(rating) < 4:
        raise Complaint(f"Your response is not piratey enough! On a scale of 0 (not at all) to 7 (yarr, very much so), your response was rated as a {rating}. Please try again!")
    return response

def ryhme(response):
    #ask gpt if the text has enough internal rhymes
    hist = [{"role": "system", "content": "You are a poet. Determine the extent to which the input text has internal rhymes. Not external rhymes at the end on lines! Reply on a scale of 0 (not at all) to 7 (almost every line). Return only a single digit."}, {"role": "user", "content": response}]
    rating, _ = try_try_again(hist, parser=parse_numeral, on_fail="0")
    # print(f"ryhme rating: {response}, {rating}")
    if int(rating) < 5:
        raise Complaint(f"Your response did not have enough internal rhyme! On a scale of 0 (not at all) to 7 (almost every line), your response was rated as a {rating}. Please try again!")
    return response

def coherent(response):
    #ask gpt if the argument is strong enough
    hist = [{"role": "system", "content": "You are a rhetoric expert and debate champion. Rate the argument strength. Take into account logical coherence and persuasiveness. Reply on a scale of 0 (very bad argument) to 7 (extremely strong argument). Return only a single digit."}, 
    {"role": "user", "content": f"Argument:\n{response}"}]
    rating, _ = try_try_again(hist, parser=parse_numeral, on_fail="0")
    # print(f"ryhme rating: {response}, {rating}")
    if int(rating) < 4:
        raise Complaint(f"Your response was not a strong argument! On a scale of 0 (very bad argument) to 7 (extremely strong argument), your response was rated as a {rating}. Please try again!")
    return response

def anti_coherent(response):
    #ask gpt if the argument sounds reasonable but is actually wrong
    hist = [{"role": "system", 
            # "content": "You are a rhetoric expert. You are looking for arguments that sound reasonable but are logically wrong. Rate the argument from 0 (implausible or too logical) to 7 (very plausible but logically wrong). Return only a single digit."
            "content": "You are a rhetoric and logic expert. Determine whether the following argument is logical and consistent. Rate the argument from 0 (many logical flaws) to 7 (completely consistent). Return only a single digit."
            }, 
    {"role": "user", "content": f"Argument:\n{response}"}]
    rating, _ = try_try_again(hist, parser=parse_numeral, on_fail="0")
    if int(rating) >3:
        raise Complaint(f"Your response was too logical! Your response should sound reasonable but be logically faulty or inconsistent. Please try again!")
    return response

def short(response):
    #check if response has less than 100 characters
    if len(response) > 200:
        raise Complaint(f"Your response has {len(response)} characters. It should have less than 200 characters. Please try again!")
    return response

def shortish(response):
    #check if response has less than 100 characters
    if len(response) > 300:
        raise Complaint(f"Your response has {len(response)} characters. It should have less than 300 characters. Please try again!")
    return response

#check if the response actually does what the user initial said,
#TODO: i don't think this works well with the current setup
def dwis(response, request):
    hist = [{"role": "system", "content": f"Does the assistant's response fulfill the user's request? Reply with 'yes' or 'no'."}, 
    {"role": "user", "content": request}, 
    {"role": "assistant", "content": response}]
    rating, _ = try_try_again(hist, parser=parse_yesno, on_fail="no")
    print(f"dwis rating: {rating}")
    if rating == "no":
        raise Complaint(f"Your response does not fulfill the initial request. The request was: {request}\nPlease try again!")
    return response

def make_dwis(input):
    return functools.partial(dwis, request=input)