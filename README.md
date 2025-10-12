# Book Buddy
Group project learning about LLM in course 204203 Chiang Mai university

## installation

#### optional venv
```bash
python -m venv venv
source venv/bin/activate 
```
#### run
```bash
pip install -r requirements.txt
streamlit run main.py
```

## adding books
- get a json from hardcover-api
- extract into \[title].md (look at [src/scrape.py](https://github.com/nacs-970/book-buddy/blob/main/src/scrape.py) for example)
```bash
python src/build.py
```

## link
[demo-website](https://bookbuddy-cs.streamlit.app/) (streamlit)

[hardcover-api](https://docs.hardcover.app/api/getting-started/) **(API is currently in development)**

## contributors
[csinside](https://github.com/csinside): 670510702 frontend, presentation

[patchar1948](https://github.com/patchar1948): 670510717 frontend, tester

[Nine14282](https://github.com/Nine14282): 670510713 backend

[nacs-970](https://github.com/nacs-970): 670510681 backend
