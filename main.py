import httpx
import asyncio
from pympler.tracker import SummaryTracker
import os
import psutil
import gc

client = httpx.AsyncClient()

tracker = SummaryTracker()


async def getImgUrl(url):
    og_line = None
    found = False
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', url) as response:
            async for chunk in response.aiter_lines():
                if "og:image" in chunk and not found:
                    og_line = chunk
                    found = True
                    break


async def main():
    process = psutil.Process(os.getpid())

    content = readUrls("leaking-links.txt")

    for chunk in batch(content, 60):
        tasks = []

        for line in chunk:
            tasks.append(asyncio.create_task(getImgUrl(line)))
        await asyncio.gather(*tasks)
        print("Memory: " + str(process.memory_info().rss))
        tracker.print_diff()

    input("Press Enter to continue...")

def readUrls(file):
    with open(file) as f:
        content = f.readlines()
    return [x.strip() for x in content]


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


if __name__ == "__main__":
    asyncio.run(main())
