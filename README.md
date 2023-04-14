# Metaprompt
[Meta-prompt: a simple self-improving language agent](https://open.substack.com/pub/noahgoodman/p/meta-prompt-a-simple-self-improving?r=n88hp&utm_campaign=post&utm_medium=web)

![image](https://user-images.githubusercontent.com/461193/232054201-e06b399c-79f4-4b68-8648-550b6a4f1f3e.png)

## Code organization

metaprompt.py has core code, `loop` is the main function. `reflectionv1` (etc.) are various versions of the meta-prompt I have tried. (Currently only `reflectionv7` works because I changed the setup to extract "Critique: ..." and "Instructions: ..." parts from the response.

tryryagain.py llm.py and filters.py have helper code to interface with language models and simulate "users". In particular, the `try_try_again` helper is used to have a conversation between the LM assistant and the `parser` "user" -- if the parser throws a `Complaint` the LM is prompted with this complaint to try again.

eval.py has the simple base evaluation. eval_analysis.py makes a plot.

20Qs.py uses metaprompt to play 20 Questions.

(Further documentation to come..)
