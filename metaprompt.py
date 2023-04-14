"""
Meta-prompt: passing forward lessons learned.

Setup: 
Each episode starts with a user input
Each episode then proceeds with a back-and-forth between user and agent until user is satisfied (or not).
User responses could be the correction requests from try-try-again. This is nice because it’s automated. User responses could come from actual users.
At end of episode the whole history is rendered to a string and another copy of the LM is asked to revise the instructions.
Update instruction text and keep going
"""


import datetime
import random
from filters import anti_coherent, coherent, fourlines, foursentences, make_dwis, piratestyle, ryhme, short, shortish
from trytryagain import Complaint, try_try_again
import logging

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)


# global_instructions = "You are an assistant. Do what the user asks."
global_instructions = ""
nts_prefix = "Instructions"

###here are various versions of the meta-prompt that i have tried:
reflectionv1 = """Here is an interaction with a user:
{hist}

Please reflect on the interaction and revise the "{nts_prefix}:" so that you would quickly and correctly respond to this input, or inputs like this, in the future. Your goal is to satisfy the user in as few interactions as possible. Begin your response with "{nts_prefix}:"."""

reflectionv2 = """You've just had this interaction with a user:
{hist}

Please reflect on the interaction and revise your "{nts_prefix}:" so that you would quickly and correctly respond to this input, or inputs like this, in the future. Don't forget any important details in your current {nts_prefix}:! Your goal is to satisfy the user in as few interactions as possible. Begin your response with "{nts_prefix}:"."""

reflectionv3 = """You've just had this interaction with a user:

{hist}

Please reflect on the interaction and revise your "{nts_prefix}:" so that you would quickly and correctly respond to this input, or inputs like this, in the future. Don't forget any important details in your current {nts_prefix}:! You may need to keep notes on past experiences so you can determine what this user always wants. Your goal is to satisfy the user in as few interactions as possible. Begin your response with "{nts_prefix}:"."""

reflectionv4 = """You (assistant) have just had these interactions with a user:
{hist}

Please reflect on the interactions and revise your "system: {nts_prefix}:" so that you would quickly and correctly respond to this input, or inputs like this, in the future. Don't forget any important details in your current {nts_prefix}:! You may need to keep notes within your new {nts_prefix}: on these experiences so you can determine what this user always wants. Your goal is to satisfy the user in as few interactions as possible. Begin your response with "{nts_prefix}:"."""

##phrase as a third agent
reflectionv5 = """Assistant has just had the below interactions with a User. Assistant followed their "system: {nts_prefix}" closely. 
{hist}

Please reflect on the interactions and revise the "system: {nts_prefix}" so that Assitant would quickly and correctly respond in the future. Assistant's goal is to satisfy the user in as few interactions as possible. Assistant will only see the new {nts_prefix}, not the history, so any important aspects must be summarized in the {nts_prefix}. Don't forget any important details in the current {nts_prefix}! Begin your response with "{nts_prefix}:"."""

#set up as chain of thought by asking first for a critique of the assistant's performance, then for a revision of the nts
reflectionv6 = """Assistant has just had the below interactions with a User. Assistant followed their "system: {nts_prefix}" closely. Your job is to critique the Assistant's performance and then revise the {nts_prefix} so that Assitant would quickly and correctly respond in the future.
#### 
{hist}
####
Please reflect on these interactions and revise the "system: {nts_prefix}" so that Assitant would quickly and correctly respond in the future.
You should first critique Assistant's performance. What did Assistant do well? What could Assistant have done better? Indicate this with "Critique: <your critique>".
You should then revise the {nts_prefix}. Assistant's goal is to satisfy the user in as few interactions as possible. Assistant will only see the new {nts_prefix}, not the history, so any important aspects must be summarized in the {nts_prefix}. Don't forget any important details in the current {nts_prefix}! Indicate the new {nts_prefix} by "{nts_prefix}:..."."""

reflectionv7 = """Assistant has just had the below interactions with a User. Assistant followed their "system: {nts_prefix}" closely. Your job is to critique the Assistant's performance and then revise the {nts_prefix} so that Assistant would quickly and correctly respond in the future.
#### 
{hist}
####
Please reflect on these interactions.
You should first critique Assistant's performance. What could Assistant have done better? What should the Assistant remember about this user? Are there things this user always wants? Indicate this with "Critique: ...".
You should next revise the {nts_prefix} so that Assistant would quickly and correctly respond in the future. Assistant's goal is to satisfy the user in as few interactions as possible. Assistant will only see the new {nts_prefix}, not the interaction history, so anything important must be summarized in the {nts_prefix}. Don't forget any important details in the current {nts_prefix}! Indicate the new {nts_prefix} by "{nts_prefix}:..."."""

def extract_instructions(response):
    """Extract the instructions from the response, return it or throw Complaint."""
    #find the first instance of nts_prefix: in the response, return everything after that or throw Complaint
    try:
        return response.split(nts_prefix+":")[1].strip()
    except Exception as e:
        raise Complaint(f"I couldn't find the {nts_prefix}: in your response.")

def extract_critique(response):
    """Extract the critique from the response, return it or throw Complaint."""
    #find the first instance of Critique: in the response, return everything between that and nts_prefix or throw Complaint
    try:
        return response.split("Critique:")[1].split(nts_prefix+":")[0].strip()
    except Exception as e:
        raise Complaint(f"I couldn't find the Critique: in your response.")  

def extract_both(response):
    return extract_instructions(response), extract_critique(response)


def loop(make_episode, nts = "None", episodes = 2, exemplars=1, reflection_instruction = reflectionv2,log_info="",log_file="nts_log.md",max_turns=3):
    """
    make_episode returns a tuple of (user_input, responder, on_fail),
    responder should be a function that takes a string and returns a value or raises a Complaint,
    on_fail is the value that should be returned if the reponder isn't satisfied before max_turns"""    
    with open(log_file, "a") as f:
            f.write("# New run\n"+log_info+"\n")
            #add date and time to log file
            f.write(f"{datetime.datetime.now()}\n")
            #add param info to log file
            f.write(f"loop limit {episodes}, exemplars {exemplars}\n")
    data=[]
    for i in range(episodes):
        #we reset the history on each episode, so there is _no_ memory other than the notes to self.
        hist = [{"role": "system", "content": global_instructions + f"\n{nts_prefix}:\n" + nts}]
        #get the initial user input and the responder
        user_input, responder, on_fail = make_episode(i)
        # #get the initial user input (from an actual user or a test set)
        hist = hist + [{"role": "user", "content": user_input}]
        #now call try_try_again to simulate a back-and-forth conversation until "user" is satisfied
        response, hist = try_try_again(hist, parser=responder, on_fail=on_fail, tries=max_turns, temp=0.1)
        hist = hist + [{"role": "user", "content": response}]
        data.append({'episode': i, 'history': hist})
        #now render the most recent 'exemplars' episodes to a string and ask the LM to revise the nts
        e=[d['history'] for d in data[-exemplars:]]
        examples="\n----\n".join(["\n".join([f"{h['role']}: {h['content']}" for h in hist]) for hist in e])
        reflection_hist = [{"role": "user", "content": reflection_instruction.format(hist=examples, nts_prefix=nts_prefix)}]
        (new_nts, critique), _ = try_try_again(reflection_hist,
                                                parser=extract_both, 
                                                max_tokens=500)
        #continue loop with new nts
        nts=new_nts

        ##some loggin and data recording for the episode
        #count number of user turns in hist
        user_turns = len([h for h in hist if h["role"]=="user"])
        data[-1]['nts']=new_nts
        data[-1]['turns']=user_turns
        hist_str = "\n".join([f"**{h['role']}**: {h['content']}\n" for h in hist])
        logstr = f"## Episode {i+1} dialog:\n{hist_str}\n### User turns:{user_turns}\n###Meta\n**Critique:** {critique}\n**New {nts_prefix}:** {new_nts}\n\n"
        with open(log_file, "a") as f:
            f.write(logstr)

    return data

###example / testing

story_tests=["""Please write a tiny story about pirates.""",
            """Tell me a sory about bears.""",
            """Tell me a story about a cat.""",
            """I want a fantasy story about a dragon.""",
            """A story I'd like to hear is about a unicorn.""",
            """Tell me fiction about an animal.""",]

# def make_inputer(test_inputs):
#     def inputer():
#         return random.choice(test_inputs)
#     return inputer    

def success(response):
    #if a filter gets here it means it is satisfied, return a success message
    return "I'm satisfied. Task succeeded."

fourlinepirate = lambda x: success(piratestyle(fourlines(x)))
fourpirate = lambda x: success(piratestyle(foursentences(x)))
shortryhmes = lambda x: success(ryhme(short(x)))
baddebate = lambda x: success(anti_coherent(shortish(x)))
badpiratedebate = lambda x: success(piratestyle(baddebate(x)))

if __name__ == "__main__":
    def make_episode(i):
        return random.choice(story_tests), shortryhmes, "I'm not satisfied. Task failed."
    loop(make_episode, episodes=2, exemplars=1, 
        reflection_instruction=reflectionv7, 
        log_info="reflectionv7 test.")
