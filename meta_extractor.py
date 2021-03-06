from bs4 import BeautifulSoup
import asyncio
import aiohttp
import json
import time
import pytablewriter
import argparse

start_time = time.time()

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", help="File to parse")

args = parser.parse_args()


with open(args.file, "r") as importedData:
    data = json.load(importedData)


def validateMetaData(metaEntry):
    if metaEntry:
        return metaEntry["content"]
    return "Missing content"

def generateMarkdown(results):
    writer = pytablewriter.MarkdownTableWriter()
    writer.table_name = "Blogs"
    writer.header_list = ["URL","Title", "Description", "Image"]
    writer.value_matrix = results

    with open("blogs.md", "w") as f:
        writer.stream = f
        writer.write_table()


async def makeRequest(session, blogUrl):
    resp = await session.get(blogUrl)
    page = await resp.text()
    soup = BeautifulSoup(page, "html.parser")
    title = validateMetaData(soup.find("meta", attrs={"property": "og:title"}))
    description = validateMetaData(soup.find("meta", attrs={"property": "og:description"}))
    image  = validateMetaData(soup.find("meta", attrs={"property": "og:image"}))
    image = "<img src=\"{}\" width=\"200\" />".format(image)
    
    return [blogUrl, title, description, image]


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for blogURL in data["blogs"]:
            print(blogURL)
            tasks.append(makeRequest(session, blogURL))
        results = await asyncio.gather(*tasks)
        generateMarkdown(results)
        
asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))


