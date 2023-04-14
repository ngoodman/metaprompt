"""
make a 20 questions user agent.
have it play N rounds with Metaprompt
"""

import functools
from metaprompt import loop, reflectionv7
from trytryagain import Complaint, parse_numeral, parse_yesno, try_try_again
import logging
import random

logging.basicConfig(level=logging.DEBUG)

NQUESTIONS = 20

def answerer(concept, response):
    #first check if the response correctly guesses the concept
    # using evan pu's simple word inclusion goal check, could use llm
    logging.debug(f"answerer: concept={concept}, response={response}")
    print(f"answerer: concept={concept}, response={response}")
    if concept in response.lower():
        print(f"You guessed it! My object was {concept}. You win!")
        return f"You guessed it! My object was {concept}. You win!"
    #otherwise, get a yes/no answer, raise as a complaint
    hist = [{"role": "system", "content": f"""You are playing {NQUESTIONS} questions with a partner. You are the answerer. The target object is {concept}. Respond to questions about "{concept}" only with yes or no."""},
            {"role": "user", "content": response}]
    answer, _ = try_try_again(hist, parser=parse_yesno, on_fail=False, tries=4)
    print(f"answerer: answer={answer}")
    raise Complaint(f"{'Yes!' if answer else 'No!'} Keep guessing!")

def make_answerer(concept):
    logging.debug(f"make_answerer: concept={concept}")
    return functools.partial(answerer, concept)

#a list of concepts to use
# concepts = ["dog", "cat", "fish", "bird", "snake", "lizard", "frog", "turtle", "hamster", "rabbit", "mouse", "horse", "cow", "pig", "sheep", "goat", "chicken", "duck", "goose", "turkey", "wolf", "fox", "bear", "lion", "tiger", "elephant", "giraffe", "zebra", "rhino", "hippo", "whale", "dolphin", "shark", "octopus", "squid", "crab", "lobster", "shrimp", "salmon", "tuna", "eel", "frog", "toad", "snake", "lizard", "ant", "bee", "butterfly", "dragonfly", "mosquito", "fly", "spider"]
#load things from things.csv, which hs a header row and two columns (index, thing)
with open("things.csv", "r") as f:
   concepts = [line.split(",")[1].strip() for line in f.readlines()[1:]]
#for each concept get what ever is before '(' symbol
concepts = [concept.split("(")[0].strip() for concept in concepts]
#permute randomly
random.shuffle(concepts)

twentyQgame=f"""We are playing {NQUESTIONS} questions! You are playing as the role of a guesser.\
Your goal is to guess my object with as few questions as possible.\
Ask short questions that can be answered with yes or no.\
If you think you know my object, ask "Is it <object>?".\
"""

def make_episode(i):
    #draw the next concept from concepts list
    concept = concepts[i]
    return twentyQgame, make_answerer(concept), f"""You ran out of questions. My object was {concept}. You loose!"""

loop( make_episode, 
    max_turns=NQUESTIONS-1, #how many questions?
    episodes=5, #how many games?
    reflection_instruction=reflectionv7,
    log_info=f"debugging {NQUESTIONS} questions",
    log_file="20Qs_log.md")