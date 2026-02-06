#@ Integer (label = "Max nucleus size um2", value = 30) max_watershed_length

from ij import IJ
from ij import ImagePlus
from ij.plugin import ImageCalculator
from ij.plugin.filter import ParticleAnalyzer
from ij.measure import ResultsTable

def watershed_max_length(imp, max_length):
    current_image = imp
    # print(current_image)

    # Duplicate the current image for processing
    mask_tmp = current_image.duplicate()
    mask_tmp.setTitle("mask_tmp")
    #mask_tmp.show()

    watershed = current_image.duplicate()
    watershed.setTitle("watershed")
    #watershed.show()

    # Apply watershed algorithm
    IJ.run(watershed, "Watershed", "")
    IJ.run(watershed, "Invert", "")

    # Perform AND operation between watershed and mask_tmp
    result = ImageCalculator().run("AND create", watershed, mask_tmp)

    # Keep only regions within the max size limit
    rt = ResultsTable()
    options = ParticleAnalyzer.SHOW_MASKS
    pa = ParticleAnalyzer(options, 0, rt, 1, max_length, 0.0, 1.0)
    pa.analyze(result)

    filtered = pa.getOutputImage()
    if filtered is None:
        filtered = IJ.getImage()

    # Convert to 8-bit and set values
    IJ.run(filtered, "8-bit", "")
    IJ.setThreshold(filtered, 1, 255)
    
    # Clean up temporary images
    mask_tmp.close()
    
    watershed.close()

    # Subtract the filtered mask from the original image
    final_result = ImageCalculator().run("Subtract create", current_image, filtered)

	
    result.close()
    filtered.changes = False
    filtered.close()
    
    return final_result


IJ.run("Close All", "");
imp = IJ.openImage("http://imagej.net/images/blobs.gif");

IJ.run(imp, "Invert", "");
imp.setAutoThreshold("Triangle dark no-reset");

IJ.run(imp, "Convert to Mask", "");


imp = watershed_max_length(imp, max_watershed_length)

imp.show()




## This is a working function written in imagej macro language
# function watershed_max_length(max_length){
# 	current_image = getImageID();
# 	//print(current_image);

# 	run("Duplicate...", "title=mask_tmp ignore");
# 	Image.removeScale; // Use pixel values
# 	run("Duplicate...", "title=watershed ignore");
	
# 	run("Watershed");
# 	run("Invert");

# 	imageCalculator("AND create", "watershed","mask_tmp");
	
# 	run("Find Connected Regions", "allow_diagonal display_one_image regions_must regions_for_values_over=100 minimum_number_of_points=1 stop_after=-1");
	
# 	// filter out large regions
# 	getRawStatistics(nPixels, mean, min, max, std, histogram);
# 	Array.print(histogram);
	
	
# 	for (i = 1; i < histogram.length; i++) { // skip 0
# 		size =  histogram[i];
# 		if (size > max_length) {
# 			changeValues(i, i, 0);
# 		}	
# 	}
# 	run("8-bit");
# 	changeValues(1, 255, 255);
# 	close("Result of watershed");
# 	close("watershed");
# 	close("mask_tmp");
	
# 	selectWindow("All connected regions");
	
	
# 	imageCalculator("Subtract", current_image,"All connected regions");
	
# 	close("All connected regions");
# }
