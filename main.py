from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HackerNews API endpoints
HACKER_NEWS_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HACKER_NEWS_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

async def fetch_story_details(story_id: int):
    """Fetch details for a single story using its story ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(HACKER_NEWS_ITEM_URL.format(story_id))
            response.raise_for_status()
            story_data = response.json()  # JSON response does not need await
            return {
                "title": story_data.get("title", "No Title"),
                "author": story_data.get("by", "Unknown"),
                "url": story_data.get("url", "No URL"),
                "score": story_data.get("score", 0),
                "time": datetime.fromtimestamp(story_data.get("time", 0)).strftime('%Y-%m-%d %H:%M:%S')
            }
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail="Failed to fetch story details from HackerNews.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching story details: {e}")

@app.get("/top-10-stories")
async def get_top_10_stories():
    """Fetch and return the top 10 stories from HackerNews."""
    try:
        async with httpx.AsyncClient() as client:
            # Fetch the top stories IDs
            response = await client.get(HACKER_NEWS_TOP_STORIES_URL)
            response.raise_for_status()
            top_story_ids = response.json()  # JSON response does not need await

            # Fetch the top 10 stories details concurrently
            tasks = [fetch_story_details(story_id) for story_id in top_story_ids[:10]]
            top_10_stories = await asyncio.gather(*tasks)

            return {"top_10_stories": top_10_stories}

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail="HackerNews API is unreachable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching top stories: {e}")
