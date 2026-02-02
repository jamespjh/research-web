from bs4 import BeautifulSoup
import requests

def test_fetch_and_content():
    fetch = requests.get('https://research.jh.condenser.arc.ucl.ac.uk')
    model = BeautifulSoup(fetch.text, 'html.parser')
    title = model.find_all("h2",id="introduction")
    assert len(title) == 1
    assert title[0].string == "Introduction"