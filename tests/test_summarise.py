import json, sys, os
sys.path.append('d:/Researching-Agent')
from app.agents.researcher import summarize_node
state = {
    'plan': [{'id':1,'question':'What is AI?','search_queries':['test']}],
    'sources':[{'id':1,'title':'Dummy','content':'Artificial intelligence is a field of computer science that...','task_id':1}]
}
result = summarize_node(state)
print(json.dumps(result, indent=2))
