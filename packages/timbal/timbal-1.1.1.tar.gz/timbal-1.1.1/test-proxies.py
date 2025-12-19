import asyncio
import os

from timbal import Agent

os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ["TIMBAL_APP_ID"] = "172"

agent = Agent(name="test-proxies", model="anthropic/claude-haiku-4-5", model_params={"max_tokens": 1024})


async def main():
    await agent(prompt="hello there").collect()


if __name__ == "__main__":
    asyncio.run(main())
