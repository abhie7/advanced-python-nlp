const puppeteer = require("puppeteer")
const fs = require("fs").promises
const path = require("path")
const axios = require("axios")

const sanitizeFilename = (filename) => {
    return filename.replace(/[^a-z0-9]/gi, "_").toLowerCase()
}

const downloadFile = async (url, outputPath) => {
    try {
        const response = await axios({
            method: "get",
            url: url,
            responseType: "arraybuffer",
        })
        await fs.writeFile(outputPath, response.data)
        console.log(`Downloaded: ${url} to ${outputPath}`)
    } catch (error) {
        console.error(`Error downloading ${url}: ${error.message}`)
    }
}

const processUrl = async (url, browser) => {
    console.log(`Processing URL: ${url}`)
    const page = await browser.newPage()
    const urlFolder = sanitizeFilename(url)
    const outputDir = path.join(__dirname, urlFolder)

    try {
        await fs.mkdir(outputDir, { recursive: true })
        console.log(`Created output directory: ${outputDir}`)

        await page.goto(url, { waitUntil: "networkidle0" })
        console.log("Page loaded")

        // Scroll to load all content
        await page.evaluate(async () => {
            await new Promise((resolve) => {
                let totalHeight = 0
                const distance = 100
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight
                    window.scrollBy(0, distance)
                    totalHeight += distance
                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer)
                        resolve()
                    }
                }, 100)
            })
        })
        console.log("Finished scrolling")

        const content = await page.content()
        console.log("Retrieved page content")

        // Extract and save CSS
        const styles = await page.evaluate(() => {
            return Array.from(document.getElementsByTagName("style")).map(
                (style) => style.innerHTML
            )
        })
        console.log(`Found ${styles.length} style tags`)

        for (let i = 0; i < styles.length; i++) {
            const cssFilename = `style_${i}.css`
            const cssPath = path.join(outputDir, cssFilename)
            await fs.writeFile(cssPath, styles[i])
            console.log(`Saved CSS file: ${cssPath}`)
        }

        // Download images and update their src
        const images = await page.evaluate(() => {
            const imgs = Array.from(document.getElementsByTagName("img"))
            return imgs.map((img) => ({
                src: img.src,
                alt: img.alt,
            }))
        })
        console.log(`Found ${images.length} images`)

        for (const img of images) {
            if (img.src) {
                const imgFilename = sanitizeFilename(path.basename(img.src))
                const imgPath = path.join(outputDir, imgFilename)
                await downloadFile(img.src, imgPath)
                content = content.replace(img.src, imgFilename)
            } else {
                console.log(`Image without src: ${img.alt}`)
            }
        }

        // Create and save HTML file
        const htmlContent = `
        <html>
        <head>
            ${styles
                .map((_, i) => `<link rel="stylesheet" href="style_${i}.css">`)
                .join("\n")}
        </head>
        <body>
            ${content}
        </body>
        </html>
        `
        const htmlPath = path.join(outputDir, "blog_post.html")
        await fs.writeFile(htmlPath, htmlContent)
        console.log(`Saved HTML file: ${htmlPath}`)
    } catch (error) {
        console.error(`Error processing ${url}: ${error.message}`)
    } finally {
        await page.close()
    }
}

const main = async (urls) => {
    const browser = await puppeteer.launch({
        headless: true,
        executablePath:
            "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    })

    try {
        for (const url of urls) {
            await processUrl(url, browser)
        }
    } finally {
        await browser.close()
    }
}

const urls = [
    "https://medium.com/aiguys/prompt-engineering-is-dead-dspy-is-new-paradigm-for-prompting-c80ba3fc4896",
    "https://medium.com/@edwindoit/killer-apps-to-organize-your-digital-workspace-2024-edition-b9b4281971f9",
]

main(urls).catch(console.error)
