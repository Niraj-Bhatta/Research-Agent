import sys, os
sys.path.insert(0, 'd:/Researching-Agent')

from dotenv import load_dotenv
load_dotenv('d:/Researching-Agent/.env', override=True)

import app.config
import app.llm
import importlib
importlib.reload(app.config)
app.llm._client = None
importlib.reload(app.llm)

from app.config import settings
print(f"Provider: {settings.provider}")
print(f"Model:    {settings.model}")
print(f"Base URL: {settings.base_url}")
print(f"Key:      {settings.api_key[:12]}...")
print(f"Tavily:   {settings.tavily_api_key[:12]}...")

from app.graph import graph

print("\n--- Starting End-to-End Pipeline Test ---")
state = {
    "job_id": "test_e2e",
    "topic": "Quantum Computing in Drug Discovery"
}

for update in graph.stream(state, stream_mode="updates"):
    for node, delta in update.items():
        state.update(delta)
        stage = delta.get("stage", node)
        print(f"✅ Stage completed: {node:12} -> stage: {stage}")
        if node == "planner":
            print(f"   Title: {state.get('title')}")
            print(f"   Tasks count: {len(state.get('plan', []))}")
        elif node == "researcher":
            print(f"   Raw search results: {len(state.get('raw_results', []))}")
        elif node == "dedup":
            print(f"   Sources after dedup: {len(state.get('sources', []))} (removed {state.get('duplicates_removed', 0)})")
        elif node == "summariser":
            print(f"   Notes generated for tasks: {list(state.get('notes', {}).keys())}")
        elif node == "writer":
            print(f"   Draft length: {len(state.get('draft', ''))} chars")
        elif node == "reviewer":
            review = state.get("review", {})
            print(f"   Review approved: {review.get('approved')}, score: {review.get('score')}")
        elif node == "export":
            print(f"   MD path:  {state.get('md_path')}")
            print(f"   PDF path: {state.get('pdf_path')}")

print("\n🎉 PIPELINE FINISHED SUCCESSFULLY!")
print(f"Report length: {len(state.get('report', ''))} characters")
