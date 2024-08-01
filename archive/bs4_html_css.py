import os
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import aiohttp

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in ' .-_']).rstrip()

async def download_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()
            return content


async def download_blog_post(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Path to Brave browser executable (adjust if necessary)
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    browser = await launch(executablePath=brave_path, headless=True)
    page = await browser.newPage()

    try:
        await page.goto(url, {'waitUntil': 'networkidle0'})

        # Scroll to load all content
        last_height = await page.evaluate('document.body.scrollHeight')
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.waitFor(2000)
            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        # Get the page content
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the main content
        article = soup.select_one('article')
        if article is None:
            print("Couldn't find the main content. Adjust the selector.")
            return

        async def main(urls):
            tasks = [download_file(url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results

            # Extract and save CSS
            styles = soup.find_all('style')
            for i, style in enumerate(styles):
                css_filename = f'style_{i}.css'
                css_path = os.path.join(output_dir, css_filename)
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(style.string)

            # Wait for all downloads to complete
            await asyncio.gather(*tasks)

        # Create HTML file with references to downloaded CSS
        html_content = f"""
        <html>
        <head>
            {''.join(f'<link rel="stylesheet" href="{css_filename}">' for i in range(len(styles)))}
        </head>
        <body>
            {article}
        </body>
        </html>
        """

        # Save the HTML file
        with open(os.path.join(output_dir, 'blog_post.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

    finally:
        await browser.close()

# Usage
asyncio.get_event_loop().run_until_complete(
    download_blog_post('https://medium.com/@edwindoit/killer-apps-to-organize-your-digital-workspace-2024-edition-b9b4281971f9', 'output_folder')
)