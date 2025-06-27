#@ File   (label = "Input directory", style = "directory") srcFile
#@ File   (label = "Output directory", style = "directory") dstFile
#@ String (label = "File extension", value=".tif") ext
#@ String (label = "File name contains", value = "") containString
#@ boolean(label = "Keep directory structure when saving", value = true) keepDirectories
#@ String (label = "Save format", choices={"Standard ImageJ TIF", "OME-TIF"}, style="listBox") saveType

import os
from ij import IJ, ImagePlus, ImageStack
from loci.plugins.in import ImporterOptions
from loci.plugins import BF

def run():
    srcDir = srcFile.getAbsolutePath()
    dstDir = dstFile.getAbsolutePath()
    for root, directories, filenames in os.walk(srcDir):
        filenames.sort()
        for filename in filenames:
            if not filename.endswith(ext):
                continue
            if containString not in filename:
                continue
            process(srcDir, dstDir, root, filename, keepDirectories)

def process(srcDir, dstDir, currentDir, fileName, keepDirectories):
    print("Processing:", fileName)
    options = ImporterOptions()
    options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
    options.setOpenAllSeries(True)
    options.setVirtual(True)
    options.setId(os.path.join(currentDir, fileName))
    
    imps = BF.openImagePlus(options)
    for i, imp in enumerate(imps):
        outname, _ = os.path.splitext(fileName)
        outname = outname + "_" + str(i+1)
        
        saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        
        output_path = os.path.join(saveDir, outname + ".ome.tif") if saveType == "OME-TIF" else os.path.join(saveDir, outname + ".tif")
        print("Saving to:", output_path)

        # Duplicate pixel data to a clean ImagePlus (strips metadata)
        stack = ImageStack(imp.getWidth(), imp.getHeight())
        for s in range(1, imp.getStackSize() + 1):
            stack.addSlice(imp.getStack().getProcessor(s))
        blank_imp = ImagePlus(imp.getTitle(), stack)
        blank_imp.setDimensions(imp.getNChannels(), imp.getNSlices(), imp.getNFrames())

        # Save
        try:
            if saveType == "Standard ImageJ TIF":
                IJ.saveAs(blank_imp, "Tiff", output_path)
            elif saveType == "OME-TIF":
                IJ.run(blank_imp, "Bio-Formats Exporter", "save=[" + output_path + "] compression=Uncompressed")
        except Exception as e:
            print("Failed to save:", e)
        
        blank_imp.close()
        imp.close()

run()
