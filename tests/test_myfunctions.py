import spookyai

spookyai.api_key = "W0jY4BtoMKX9HDXoCYHfWImECZu1"
spookyai.agent_id = "5f9b1b4e4f9b4a0007f1e2a9"
spookyai.agent_name = "Jack's AI Agent"

def test_query_human():
    
    spookyai.query_human("What is the weather like today?")
    
    assert spookyai.query_human("What is the weather like today?") == "Hello World, this is my first Python library!"
    