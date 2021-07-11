from bs4 import BeautifulSoup
import asyncio
import aiohttp
import json
import time
import pytablewriter
import io

start_time = time.time()

with open("data.json", "r") as importedData:
    data = json.load(importedData)


async def makeRequest(session, blogUrl):
    resp = await session.get(blogUrl)
    page = await resp.text()
    soup = BeautifulSoup(page, "html.parser")
    title = soup.find("meta", attrs={"property": "og:title"})
    description = soup.find("meta", attrs={"property": "og:description"})
    if title:
        title = title["content"]
    else:
        title = "Missing Title"
    if description:
        description = description["content"]
    else:
        description = "Missing Description"
    return [blogUrl, title, description]


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for blogURL in data["blogs"]:
            print(blogURL)
            tasks.append(makeRequest(session, blogURL))
        results = await asyncio.gather(*tasks)
        # print(results)
        writer = pytablewriter.MarkdownTableWriter()
        writer.table_name = "Blogs"
        writer.header_list = ["URL","Title", "Description"]
        writer.value_matrix = results

        with open("blogs.md", "w") as f:
            writer.stream = f
            writer.write_table()
        


asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))
