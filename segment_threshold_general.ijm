#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix
#@ String (label = "Mean filter size csv pr channel", value = "4,4") mean_filter_csv

mean_filter = split(mean_filter_csv, ",");

function processFile(input, output, file) { 
	
	// Load file and prepare for processing
	file_path = input + File.separator + file;
	
	run("Bio-Formats Importer", "open=[" + file_path  + "] color_mode=Grayscale rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack series_1");
	rename("input");
	basename = File.getName(file_path);
	basename_noext = File.getNameWithoutExtension(basename);

	// Threshold the 8bit image
	selectWindow("input");
	
	getDimensions(width, height, channels, slices, frames);
	
	
	for (c = 1; c < channels +1; c++) {
		Stack.setChannel(c);
		
		// run a median filter
		for (z = 1; z < slices+1; z++) {
			Stack.setSlice(z);
			run("Mean...", "radius=" + mean_filter[c-1] + " slice"); // loop keeps as virtualstack
		}
		
		//
		
	}

	
	setAutoThreshold("Huang dark");
	run("Convert to Mask");
	run("Fill Holes");
	
	// Remove very small extrusions
	for (i = 0; i < erode_objects; i++) {
		run("Erode");
	}
	
	for (i = 0; i < erode_objects; i++) {
		run("Dilate");
	}	
	
	n = roiManager('count');
	if (n>0) {
		roiManager("Deselect");
		roiManager("Delete");
	}
	run("Analyze Particles...", "size=" + size + " circularity=" + circularity + " exclude clear add");

	
	
	// The Edge of the FOV will be detected remove cells that touch it
	// Thiss will also fill holes of compleated objects
	// And remove objects that are too small (Not in ROI manager)
	clear_near_fov("fov", "input_8bit");
	
	// Analyze image
	//run("Close All");
	
	
	selectWindow("RGB");
	
	roiManager("Deselect");
	
	run("Set Measurements...", "area mean standard min center shape redirect=None decimal=2");
	run("Clear Results");
		
	// save ROI and mask
	n = roiManager('count');
	if (n>0) {
		roiManager("Measure");
		saveAs("Results", output + File.separator + basename_noext + "_simple_measurements.csv");
		roiManager("Save", output + File.separator + basename_noext + "_rois.zip");
	}
	
	// Process on mask
	selectWindow("input_8bit");
	mask_path = output + File.separator + basename_noext + "_cell_mask.tif";
	print(mask_path);
	saveAs("Tiff",  mask_path);
	
	roiManager("Show All");
	//waitForUser;
	
	run("Close All");	
	
	
	extract_blebs(input_single_channel, mask_path)
	
	
}

// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);

	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix)){
			file_counter++;
			if(file_counter > -1)
				processFile(input, output, list[i]);
		}
			//process_file(path, 250, 10, 10, 200, 5);
	}
}

run("Close All");
//setBatchMode("hide");

//path = "//SCHINKLAB-NAS/data1/Schink/Oyvind/biphub_user_data/6892662 - Gaustad - Hilde Loge - Nilsen -/input/AG27/AG27 21OCT.jpg";
fov_threshold = 5;
erode_fov = 10;
median_filter = 6;
normalize_local_xy = 200;
normalize_local_sd = 5;

circularity="0.00-1.00";
size = "50000-200000";
erode_objects = 2;
connect_objects = 3;
// final_circularity="0.00-1.00"; // Same allways
file_counter = 0;

processFolder(input);
setBatchMode("exit and display");
