const Jimp = require("jimp");
const Zip = require("node-zip")();
const fs = require("fs");

class ImageProcessor {
    constructor(filename) {
        this.filename = filename;
    }

    async processAndGenerate() {
        try {
            // Read the image
            const image = await Jimp.read(this.filename);

            // Upscale and save the images in memory
            const sizes = [512, 1024, 2048, 4096]; // Large sizes to consume memory
            const images = [];

            for (let size of sizes) {
                const buffer = await image.clone().resize(size, size).getBufferAsync(Jimp.MIME_PNG);
                images.push({
                    size: `${size}x${size}`,
                    data: buffer,
                });
            }

            // Add images to ZIP
            for (let img of images) {
                Zip.file(`${img.size}/image.png`, img.data);
            }

            // Generate ZIP file
            const zipData = Zip.generate({ base64: false, compression: "DEFLATE" });

            // Save ZIP file to disk (or return it)
            fs.writeFileSync("output.zip", zipData, "binary");

            return {
                statusCode: 200,
                body: "ZIP file generated successfully",
            };
        } catch (error) {
            return {
                statusCode: 500,
                body: `Error processing image: ${error.message}`,
            };
        }
    }
}

module.exports = async function (event, context = null) {
    try {
        const filename = "input.png"; // Ensure this file exists
        const processor = new ImageProcessor(filename);
        return await processor.processAndGenerate();
    } catch (error) {
        return {
            statusCode: 500,
            body: `Error: ${error.message}`,
        };
    }
};

