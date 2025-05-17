#target photoshop

// Function to add a background color
function addBackgroundColor(hexColor) {
    var color = new SolidColor();
    color.rgb.hexValue = hexColor;

    // Create a new background layer
    var backgroundLayer = app.activeDocument.artLayers.add();
    backgroundLayer.name = "Background Color";

    // Fill the background with the selected color
    app.activeDocument.selection.selectAll();
    app.activeDocument.selection.fill(color);
    app.activeDocument.selection.deselect();

    // Move the background layer to the bottom
    backgroundLayer.move(app.activeDocument.artLayers[app.activeDocument.artLayers.length - 1], ElementPlacement.PLACEBEFORE);
}

// Function to replace black pixels with a new color
function replaceBlackWithColor(hexColor) {
    var color = new SolidColor();
    color.rgb.hexValue = hexColor;

    // Select black pixels
    var black = [0, 0, 0];
    app.activeDocument.selection.selectColorRange(black, 0); // Select pure black

    // Fill the selected area with the new color
    app.activeDocument.selection.fill(color);
    app.activeDocument.selection.deselect();
}

// Function to resize an image to specified width, height, and resolution
function resizeImage(width, height, resolution) {
    app.activeDocument.resizeImage(
        width,       // New width
        height,      // New height
        resolution,  // New resolution
        ResampleMethod.BICUBIC // Resampling method
    );
}

// Function to process all images in a directory
function processFolder(inputFolder, outputFolder, width, height, resolution) {
    var fileList = inputFolder.getFiles(/\.(jpg|jpeg|png|tiff|bmp|gif)$/i); // Supported image formats

    for (var i = 0; i < fileList.length; i++) {
        var file = fileList[i];

        if (file instanceof File) {
            open(file);

            // Check if image has an alpha channel (transparent background)
            var hasAlpha = app.activeDocument.channels.length > 3; // Alpha channel present?

            // Resize the image
            resizeImage(UnitValue(width, "px"), UnitValue(height, "px"), resolution);

            // If the image is a PNG with alpha, prompt for optional background and color replacement
            if (file.name.match(/\.png$/i) && hasAlpha) {
                var addBg = confirm("This image has transparency. Do you want to add a background color?");
                if (addBg) {
                    // Prompt user to choose a background color using hex
                    var bgColor = prompt("Enter the hex code for the background color (e.g., FFFFFF for white)", "FFFFFF");
                    addBackgroundColor(bgColor);
                }

                var replaceBlack = confirm("Do you want to replace black pixels with a new color?");
                if (replaceBlack) {
                    // Prompt user to choose a replacement color
                    var newBlackColor = prompt("Enter the hex code to replace black (e.g., FF0000 for red)", "FF0000");
                    replaceBlackWithColor(newBlackColor);
                }
            }

            // Flatten the image to merge all layers for output
            app.activeDocument.flatten();

            // Save the resized image in the output folder
            var outputFile = new File(outputFolder + "/" + file.name);
            if (file.name.match(/\.png$/i)) {
                var pngOptions = new PNGSaveOptions();
                pngOptions.compression = 9; // Maximum compression
                app.activeDocument.saveAs(outputFile, pngOptions, true);
            } else {
                var saveOptions = new JPEGSaveOptions();
                saveOptions.quality = 8; // moderate quality
                app.activeDocument.saveAs(outputFile, saveOptions, true);
            }

            // Close the document without saving
            app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
        }
    }
}

// Main function
function main() {
    // Prompt the user to select the input folder
    var inputFolder = Folder.selectDialog("Select the folder containing images to resize");
    if (!inputFolder) return; // User canceled

    // Prompt the user to select the output folder
    var outputFolder = Folder.selectDialog("Select the folder to save resized images");
    if (!outputFolder) return; // User canceled

    // Prompt the user to define the desired width, height, and resolution
    var width = prompt("Enter the desired width in pixels", "1920");
    var height = prompt("Enter the desired height in pixels", "1080");
    var resolution = prompt("Enter the desired resolution (DPI)", "72");

    // Validate input
    if (!width || !height || !resolution) {
        alert("Please provide valid width, height, and resolution.");
        return;
    }

    // Process the folder
    processFolder(inputFolder, outputFolder, parseInt(width), parseInt(height), parseInt(resolution));

    alert("Batch resize complete.");
}

// Run the script
main();
