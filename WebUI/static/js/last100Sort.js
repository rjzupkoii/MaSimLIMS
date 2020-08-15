var tableData = [];
var targetURL;
var previousHeaderInder = 0;
var state = {
  'querySet': tableData,
  'page': 1,
  'rows': 20,
  'window': 5,
};
var currentIsAscending = false;

// Transfer table date to string type
function tableDataToString(){
  for(var i = 0; i < tableData.length;i++){
    for(var n = 0; n < tableData[i].length;n++){
      tableData[i][n] = String(tableData[i][n])
    }
  }
}

// sort table data based upon parameter "asc"
function Sort(column, orignal,asc=true) {
  var bIndex = 1
  var track = bIndex
  var aIndex = 0
  for(bIndex; bIndex <= (orignal.length-1);bIndex++){
    track = bIndex
    for(aIndex=bIndex-1; aIndex >= 0; aIndex--){
      var returnVal = compare(tableData[aIndex][column].trim(),tableData[track][column].trim())
      if(asc){
        if(returnVal){
          var tmp = tableData[aIndex]
          tableData[aIndex] = tableData[track]
          tableData[track] = tmp
          track = aIndex
        }else{
          break
        }
      }else{
        if(!returnVal){
          var tmp = tableData[aIndex]
          tableData[aIndex] = tableData[track]
          tableData[track] = tmp
          track = aIndex
        }else{
          break
        }
      }
    }
  }
}

// Compare the two values, return true if if A > B
function compare(a, b) {
  // Is this an integer?
  if (!(isNaN(parseInt(a)) && isNaN(parseInt(b)))) {
    return a > b;
  }

  // Is this a running time?
  if (/\d{2}\.\d{6}/.test(a) && /\d{2}\.\d{6}/.test(b)) {
    return compareRunning(a, b);
  }

  // Is this a Date
  if (!(isNaN(Date.parse(a)) && isNaN(Date.parse(b)))) {
    return Date.parse(a) > Date.parse(b);
  }

  // Must be two strings
  return a > b;
}

// Compare two running times, return true if A > B
function compareRunning(a, b) {
    // Do either have a day?
    if (/^\d* days, .*$/.test(a) || /^\d* days, .*$/.test(b)) {
      
      // Capture the groups
      one = a.match(/^(\d*) days, (.*)$/);
      two = b.match(/^(\d*) days, (.*)$/);

      // Does only one option have a day group?
      if (one === null || two === null) {
        return one !== null;
      }

      // Are the days equal?
      if (one[0] === two[0]) {
        return Date.parse(one[1]) > Date.parse(two[1]);
      }

      // Compare as two times
      return parseInt(one[0]) > parseInt(two[0]);
    }

    // Compare as two times
    return Date.parse(a) > Date.parse(b);
}

// If headers are clicked, clear table and pagination features
$(".content-table th").click(function() {
  $("#table-body").empty();
  $("#pagination-wrapper").empty();
});

// ajax code to send request, get data, sort, build table.
// ajax has its own range, value changes only works within ajax code range
function tableSort(headerIndex){
  $.ajax({
      url: targetURL,
      type: 'POST',
      success: function(result) {
        // Fix here
        tableData = result.rowsList
        tableDataToString()
        Sort(headerIndex,tableData,currentIsAscending)
        state.querySet = tableData
        buildTable(targetURL)
      }
    });
}


function setTargetURL(urlInput){
  targetURL = urlInput;
}


// header click event listener
document.querySelectorAll(".content-table th").forEach(headerCell => {
  headerCell.addEventListener("click", () => {
      const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
      // Check previous header index
      if(previousHeaderInder == headerIndex){
        currentIsAscending = !currentIsAscending
      }else{
        previousHeaderInder = headerIndex
        currentIsAscending = true
      }
      // sort data and clear tableData
      tableSort(headerIndex)
      tableData=[]
  });
});