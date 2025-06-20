#@ File		(label = "Input directory", style = "directory") srcFile
#@ File		(label = "Output directory", style = "directory") dstFile
#@ String	(label = "File extension", value=".tif") ext
#@ String	(label = "File name contains", value = "") containString
#@ boolean (label = "Keep directory structure when saving", value = true) keepDirectories
#@ String (lavbel = "Save format", choices={"Standard ImageJ TIF", "OME-TIF"}, style="listBox") saveType

# This code was based on the Jython template in imageJ for processing folders
# THe only thing that was changed was with respect to loading with bioformats and saving with different formats


import os
from ij import IJ, ImagePlus
from loci.plugins.in import ImporterOptions
from loci.plugins import BF

def run():
	srcDir = srcFile.getAbsolutePath()
	dstDir = dstFile.getAbsolutePath()
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort();
		for filename in filenames:
			# Check for file extension
			if not filename.endswith(ext):
				continue
			# Check for file name pattern
			if containString not in filename:
				continue
			process(srcDir, dstDir, root, filename, keepDirectories)
 
def process(srcDir, dstDir, currentDir, fileName, keepDirectories):
	print "Processing:"
	
	# Opening the image
	print "Open image file", fileName
	#imp = IJ.openImage(os.path.join(currentDir, fileName))
	 
	# open with bioformats
	options = ImporterOptions()
	options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
	options.setOpenAllSeries(True)
	options.setVirtual(True)	
	options.setId(os.path.join(currentDir, fileName))
	imps = BF.openImagePlus(options)
	for i, imp in enumerate(imps):
		outname, ext = os.path.splitext(fileName)
		outname = outname + "_" + str(i+1) 
		
		# Saving the image
		saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		#imp.show()
		if saveType == "Standard ImageJ TIF":
			IJ.saveAs(imp, "Tiff", saveDir + "/" + outname + ".tif");
		elif saveType == "OME-TIF":
			IJ.saveAs(imp, "OME-Tiff", saveDir + "/" + outname + ".ome.tif")
		
		
		imp.close()
run()

