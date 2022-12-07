$(document).ready(function () {
    $("#editorBody").summernote({
        height: 300,                 // set editor height
        minHeight: 100,              // set minimum height of editor
        maxHeight: 600,              // set maximum height of editor
        focus: false,                // don"t focus editable area after initialization
        disableDragAndDrop: true,    // prevent drag and drop for files
        tabDisable: false,           // enable tabbing out of the field

        toolbar: [
            ["style", ["style"]],
            ["font", ["bold", "italic", "underline", "strikethrough", "superscript", "subscript", "clear"]],
            ["color", ["color"]],
            ["para", ["ul", "ol", "paragraph"]],
            ["table", ["hr", "table"]],
            ["insert", ["link", "codeview"]],
        ],

        styleTags: [
            {
                title: "Heading",
                value: "h5"
            },
            {
                title: "Subheading",
                value: "h6"
            }
        ],
    });

    // below doesn't really work as expected, on closer inspection
    $("#editorBody").on("summernote.enter", function(we, e) { $(this).summernote("pasteHTML", "<br><br>"); e.preventDefault(); });
});
