import asyncio
from pyppeteer import launch
import tracemalloc
import json
import time
import random

# start tracing memory allocations
tracemalloc.start()

async def fetch_data(search_string):
    brave_path = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'  # update to your path

    # launch the Brave browser
    browser = await launch(executablePath=brave_path, headless=True)
    page = await browser.newPage()

    # go to the lightcast website
    await page.goto('https://lightcast.io/open-skills', waitUntil='networkidle0')

    # type the search string into the search bar
    search_bar = await page.querySelector('#widget-input-search')
    if search_bar:
        await search_bar.type(search_string)
        await search_bar.press('Enter')
    else:
        print(f"Search bar not found for {search_string}")
        await browser.close()
        return

    # monitor network requests to capture the token
    token_found = asyncio.Future()

    async def intercept_response(response):
        if token_found.done():
            return  # prevent setting the result if the token is already found

        # check if the response URL contains the token
        if 'skills' in response.url and response.status == 200:
            request = response.request
            headers = request.headers
            token = headers.get('authorization', None)
            if token:
                token_found.set_result(token)

    page.on('response', lambda response: asyncio.ensure_future(intercept_response(response)))

    try:
        token = await asyncio.wait_for(token_found, timeout=10)
        print(f"Token found: {token}")

        # Fetch data using the captured token
        api_url = f"https://emsiservices.com/emsi-open-proxy-service/skills/versions/latest/skills?q={search_string}"
        response_data = await page.evaluate('''(api_url, token) => {
            return fetch(api_url, {
                method: 'GET',
                headers: {
                    'Authorization': token,
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://lightcast.io/'
                }
            }).then(response => response.json().then(data => data.data));  // only extract the `data` array
        }''', api_url, token)

        # save to json
        output_path = f'output/{search_string}.json'
        with open(output_path, 'w') as f:
            json.dump(response_data, f, indent=4)
        print(f"Data saved to {output_path}")

    except asyncio.TimeoutError:
        print(f"Token not found for {search_string}, skipping this search string.")

    await browser.close()

search_strings = ['aa', 'bb', 'cc']
for search_string in search_strings:
    print(f"Processing search string: {search_string}")
    asyncio.get_event_loop().run_until_complete(fetch_data(search_string))

    # add random delay between 2 to 10 minutes
    delay = random.randint(120, 600)
    print(f"Sleeping for {delay} seconds before next search string...\n")
    time.sleep(delay)
