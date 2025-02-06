# langchain

first of all: `cd langchain`

## run model locally

build and run
```sh
docker build -t deepseek-r1-container .
docker run --rm -it -p 11434:11434 deepseek-r1-container
```

call the model
```sh
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:8b",
  "prompt": "Explain quantum mechanics in simple terms"
}'
```


## run script
```sh
python3 -m venv .venv
source .venv/bin/activate

# deepseek
pip3 install -qU langchain-deepseek
python3 test_deepseek.py

# groq
pip3 install -qU langchain-groq
python3 test_groq.py

# openai
pip3 install -qU langchain-openai
python3 test_open_ai.py
```


### References
- https://python.langchain.com/docs/introduction/
