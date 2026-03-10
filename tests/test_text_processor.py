import pytest
from analyzer.text_processor import clean_text, extract_technologies, get_category, extract_keywords

def test_clean_text():
    raw_text = "# Hello World!\nCheck out [Vue](https://vuejs.org) and `React`."
    cleaned = clean_text(raw_text)
    assert "Hello World" in cleaned
    assert "Vue" in cleaned
    assert "React" in cleaned
    assert "http" not in cleaned
    assert "]" not in cleaned

def test_extract_technologies():
    text = "We use React, node.js, and mongodb."
    topics = ["react", "javascript", "backend"]
    techs = extract_technologies(text, topics)
    assert "react" in techs
    assert "mongodb" in techs

def test_get_category():
    assert get_category("react") == "Web Frontend"
    assert get_category("tensorflow") == "AI/ML"
    assert get_category("unknown_tech") == "Other"

def test_extract_keywords():
    text = "The quick brown fox jumps over the lazy dog. Fox is fast."
    keywords = extract_keywords(text)
    # the, over, is... should be stripped
    words = [kw[0] for kw in keywords]
    assert "fox" in words
    assert "quick" in words
    assert "lazy" in words
