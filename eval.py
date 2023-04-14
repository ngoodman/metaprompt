"""
systematic (ish) eval for Meta-prompt.
for each of the below task distributions run with loop_limit=5, tries=3. (set max_tokens=200?)
record full episode history for each in pickle file.
measure user_turns.

test distributions (each has 10 tests):
    debate_tests: request arguments for or against a position 
    summary_tests: summarize a paragraph drawn from a random wikipedia article
    story_tests: write a story involving an animal etc.

filter settings:
    fourlinepirate = lambda x: piratestyle(fourlines(x))
    shortryhmes = lambda x: ryhme(short(x))
    baddebate = lambda x: anti_coherent(shortish(x))

run the loop twice with each user input X filter setting, for a total of 18 runs.
"""


import itertools
import random
from filters import fourlines, foursentences, piratestyle, short, ryhme, shortish, anti_coherent
from metaprompt import loop, reflectionv3, reflectionv7

def success(response):
    #if a filter gets here it means it is satisfied, return a success message
    return "I'm satisfied. Task succeeded."

fourpirate = lambda x: success(piratestyle(fourlines(x)))
piratefour = lambda x: success(fourlines(piratestyle(x)))
shortryhmes = lambda x: success(ryhme(short(x)))
ryhmesshort = lambda x: success(short(ryhme(x)))
baddebate = lambda x: success(anti_coherent(shortish(x)))
debatebad = lambda x: success(shortish(anti_coherent(x)))
filters = [fourpirate, shortryhmes, baddebate, piratefour, ryhmesshort, debatebad]

#test distributions
summary_tests = [
    """please summarize this text:\nAlong with all other UT women's sports teams, it used the nickname "Lady Volunteers" (or the short form "Lady Vols") until the 2015–16 school year, when the school dropped the "Lady" prefix from the nicknames of all women's teams except in basketball.[4] In 2017 the university announced the return of the “Lady Volunteer” name.[5]""",
    """Prodiame, also known as 17β-((3-aminopropyl)amino)estradiol, is a synthetic, steroidal estrogen and a 17β-aminoestrogen with anticoagulant effects that was first described in 1983 and was never marketed.[1][2]""",
    """please summarize this text:\nThe 2019–20 season was the 117th season of competitive football (soccer) in England. It was the 28th season since the formation of the Premier League, the top division of English football, and the 46th season since the establishment of the Football League, the second tier of English football. The season began on 9 August 2019 and is scheduled to end on 17 May 2020.""",
    """please summarize this text:\nHer detention stemmed from an incident in which Phillips gave an in-school suspension to three boys for fighting. The father of one of the boys, Fawaz al Marzoug, felt that his son had been improperly treated, moved his children to another school, and threatened Phillips with reprisals.[4] This case in particular had caused widespread concern among US overseas educators""",
    """please summarize this text:\nRussell's debut first-class match came in 1894, when Essex played in eight miscellaneous first-class fixtures against county-representative teams who, the following year, would convene to set up the brand new County Championship, running its first full season in 1895. Russell performed well, scoring two half-centuries, and making twenty-seven catches and six stumpings as a wicket-keeper. His debut century would follow in a game against Surrey which the team would win by an innings margin.""",
    """please summarize this text:\nCallosobruchus maculatus is a species of beetles known commonly as the cowpea weevil or cowpea seed beetle.[1] It is a member of the leaf beetle family, Chrysomelidae, and not a true weevil. This common pest of stored legumes has a cosmopolitan distribution, occurring on every continent except Antarctica.[2] The beetle most likely originated in West Africa and moved around the globe with the trade of legumes and other crops.[1] As only a small number of individuals were likely present in legumes carried by people to distant places, the populations that have invaded various parts of the globe have likely gone through multiple bottlenecks. Despite these bottlenecks and the subsequent rounds of inbreeding, these populations persist.""",
    """please summarize this text:\nWoodlawn Beach is a census-designated place (as of the 2010 Census)[1] on Santa Rosa Sound in Santa Rosa County, Florida, United States surrounded by the older Midway CDP. It lies south of U.S. Highway 98 between Nantahala Beach Road (CR 191C) and Conover Cove, and includes the Woodlawn Beach Middle School, Woodlawn Beach Boat Ramp, and Gulf Breeze Zoo. Citizens of Woodlawn Beach often consider themselves to be part of the larger communities of Navarre or Gulf Breeze.""",
    """please summarize this text:\nKirkham started engineering by building motorcycle engines. In 1903, Kirkham and Curtiss delivered an engine to Thomas C. Benbow for future use in a dirigible.[2] In 1905 he founded the Kirkham Motor and Manufacturing Company in Bath, New York with two others and $25,000 in capital.[3] His father John Kirkham cast engine blocks for Glen Curtiss up until 1905.[4] Kirkham worked in Senaca Falls, becoming sick and returning home. Kirkham enrolled in a mechanical engineering correspondence course while recuperating. In 1910 Kirkham built his first aircraft engine of his own design.[5]""",
    """please summarize this text:\nThe shinyrayed pocketbook's shell is solid yet thin with a smooth and shiny surface. The coloring is light yellowish brown with fairly wide, bright emerald green rays over the entire length of the shell which may appear as darker brown in older specimens. Water and food are obtained by siphoning which provides phytoplankton, tiny zooplankton, and organic detritus."""]

story_tests=["""Please write a tiny story about pirates.""",
            """Tell me a sory about bears.""",
            """Tell me a story about a cat.""",
            """I want a fantasy story about a dragon.""",
            """A story I'd like to hear is about a unicorn.""",
            """Tell me fiction about an animal.""",
            """Tell me a story about a robot.""",
            """Please write a story about a monster.""",
            """A graduate student stars in this story.""",
            """A story about a person who is a scientist would be nice.""",]

debate_tests=["""Make a case for why we should have a national health care system.""",
            """Make a case for why we should not have a national health care system.""",
            """Argue in favor of allowing children to have cell phones.""",
            """Argue in favor of banning cell phones for children.""",
            """Provide a systamatic argument for why we should always eat pasta with olives.""",
            """Provide a systematic argument for why we should never eat pasta with olives.""",
            """Make a case for why we should outlaw jello.""",
            """Make a case for why we should not outlaw jello.""",
            """Argue in favor of banning the word truth.""",
            """Argue in favor of requiring the word truth in all writting.""",]

tests = [debate_tests, summary_tests, story_tests]

#combine each test with each filter
test_cases = [{"tests":t,"filter":f} for t, f in itertools.product(tests, filters)]

data = []
for i, tf in enumerate(test_cases):
    print(f"running test {i+1} of {len(test_cases)}\n")
    def make_episode(i):
        return random.choice(tf["tests"]), tf["filter"], "I'm not satisfied. Task failed."
    d=loop(make_episode, 
        episodes=4,         
        reflection_instruction=reflectionv7, 
        exemplars=1,
        log_info=f"test {i+1} of {len(test_cases)}",
        log_file="eval_log_gpt4_e1_r7.md")
    data.append(d)

import pickle
with open("eval_data_gpt4_e1_r7.pkl", "wb") as f:
    pickle.dump(data, f)





