$(function () {
    $("#string-pattern").on('keyup', function (event) {
        var files = $("#csv-file").get(0).files;
        if (event.key === "Enter" && files.length !== 0) {
            createPivotFromFile(files[0]);
        }
    })
});

$(function () {
    $("#csv-file").change(handleFileSelect);
});

function handleFileSelect(evt) {
    createPivotFromFile(evt.target.files[0]);
}

function createPivotFromFile(file) {
    var patterns = $("#string-pattern").val().split(',');
    var filter = patterns[0] === "" ? getSameValue : getGroupingValue;
    Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        transform: function (value, index) {
            return filter(patterns, value);
        },
        complete: function (results) {
            $("#output").pivotUI(results.data);
        }
    });
}

function getSameValue(patterns, value) {
    return value;
}

function getGroupingValue(patterns, value) {
    for (var i = 0; i < patterns.length; i++) {
        var pattern = patterns[i];
        if (value.indexOf(pattern) !== -1) {
            return pattern;
        }
    }
    return value;
}
