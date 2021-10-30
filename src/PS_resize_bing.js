var target_width = 1920;
var target_height = 1080;

var input_relative_folder = "../api/US/images/source";
var output_relative_folder = "../api/US/images/1080p";


// ===================================================================================================

#target photoshop
app.preferences.rulerUnits = Units.PIXELS;

// ===================================================================================================

function stripExtention(filename) {
    filename = filename.split(".");
    if (filename.length > 1) {
        fileType = filename[filename.length - 1];
        filename.length--;
        filename = filename.join(".");
    }
    return filename;
}

var input_path = $.fileName + "/../" + input_relative_folder,
    output_path = $.fileName + "/../" + output_relative_folder,

    input_folder = new Folder(input_path),
    output_folder = new Folder(output_path),

    input_files = input_folder.getFiles();


for (var i = 0; i < input_files.length; ++i) {
    var input_file  = new File(input_files[i]),
        output_file = new File(output_folder + "/" + stripExtention(input_files[i].fsName.replace(/^.*[\\\/]/, '')) + ".jpg");

    if (output_file.exists) continue;

    var doc = app.open(input_file);

    // ===================================================================================================


    var cur_width = doc.width, cur_height = doc.height;

    // Test height resize
    var height_resize_new_height = target_height;
    var height_resize_new_width = Math.round(cur_width * height_resize_new_height / cur_height);


    // Test width resize
    var width_resize_new_width = target_width;
    var width_resize_new_height = Math.round(cur_height * width_resize_new_width / cur_width);


    if (height_resize_new_width >= target_width) {
        doc.resizeImage(null, UnitValue(target_height, "px"), null, ResampleMethod.AUTOMATIC);
    } else {
        doc.resizeImage(UnitValue(target_width, "px"), null, null, ResampleMethod.AUTOMATIC);
    }

    doc.resizeCanvas(UnitValue(target_width, "px"), UnitValue(target_height, "px"));


    // ===================================================================================================

    saveOptions = new JPEGSaveOptions();
    saveOptions.embedColorProfile = true;
    saveOptions.formatOptions = FormatOptions.OPTIMIZEDBASELINE;
    saveOptions.matte = MatteType.NONE;
    saveOptions.quality = 12;
    doc.saveAs(output_file, saveOptions, true, Extension.LOWERCASE);
    doc.close(SaveOptions.DONOTSAVECHANGES);

    // break;
}
