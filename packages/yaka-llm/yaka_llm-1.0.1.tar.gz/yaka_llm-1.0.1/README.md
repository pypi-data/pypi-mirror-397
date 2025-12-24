# YakaLLM 
A smaller, faster and cooler version of LangChain. the repo without `.git` is only 74k. Its like preact for react, but nothing is backward compatible.


## how to install
pip:
```
pip install yaka-llm
# or 
pip3 install yaka-llm
```
uv:
```
uv add yaka-llm
# or 
uv pip install yaka-llm
```

## Usage 
```python
from yaka_llm import GeminiModel
from yaka_llm.core import UserPrompt, ModelPrompt
import os

gm = GeminiModel("gemini-2.5-flash", os.getenv("LLM_API_KEY"))

gm.call(["Hello there"], prompt="What's up?")

# or

history = [UserPrompt("What are the three largest cities in Spain?"),
           ModelPrompt("The three largest cities in Spain are Madrid, Barcelona, and Valencia.")]
print(gm.call(history, prompt="What is the most famous landmark in the second one?"))
```
