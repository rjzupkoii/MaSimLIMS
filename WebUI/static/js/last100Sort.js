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
      tableData[i][n] = String(tableData[i][n]);
    }
  }
}

// sort table data based upon parameter "asc"
function Sort(column, orignal,asc=true) {
  alert(asc)
  var bIndex = 1;
  var track = bIndex;
  var aIndex = 0;
  for(bIndex; bIndex <= (orignal.length-1);bIndex++){
    track = bIndex;
    for(aIndex=bIndex-1; aIndex >= 0; aIndex--){
      var returnVal = compare(tableData[aIndex][column].trim(),tableData[track][column].trim());
      if(asc){
        if(returnVal){
          var tmp = tableData[aIndex];
          tableData[aIndex] = tableData[track];
          tableData[track] = tmp;
          track = aIndex;
        }else{
          break;
        }
      }else{
        if(!returnVal){
          var tmp = tableData[aIndex];
          tableData[aIndex] = tableData[track];
          tableData[track] = tmp;
          track = aIndex;
        }else{
          break;
        }
      }
    }
  }
}

// Compare the two values, return true if if A > B
function compare(a, b) {
  // Check whether it is time first, the check integer. Because of JS problem, time can be transfered into int
  // Is this a running time?
  if (/\d{2}\.\d{6}/.test(a) && /\d{2}\.\d{6}/.test(b)) {
    return compareRunning(a, b);
  }
  
  // Is this a Date
  // Date.parse has problem. When I test it, it works even I input an integer
  if (/\d{4}-\d{2}-\d{2}/.test(a) && /\d{4}-\d{2}-\d{2}/.test(b)) {
    // i.e 2020-04-30 22:42:48
    // a[0] = 2020-04-30, a[1] = 22:42:48
    a = a.split(' ');
    b = b.split(' ');
    // compare date first, if date are equal -> compare time else return the result
    return parseDateAndCompare(a[0],b[0])=="Equal"? parseRunningAndCompare(a[1],b[1]) : parseDateAndCompare(a[0],b[0]);
  }

  // Is this an integer?
  if (!(isNaN(parseInt(a)) && isNaN(parseInt(b)))) {
    return parseInt(a) > parseInt(b);
  }

  // Must be two strings
  return a > b;
}


function parseDateAndCompare(a,b){
  a = a.split('-');
  b = b.split('-');
  for(var i=0;i < a.length;i++){
    if(parseInt(a[i]) > parseInt(b[i])){
      return true;
    }else if(parseInt(a[i]) < parseInt(b[i])){
      return false;
    }
  }
  return "Equal";
}

// return true if A > B
function parseRunningAndCompare(a,b){
  a = a.split(":");
  b = b.split(":");
  for(var i = 0;i < a.length;i++){
    if(parseFloat(a[i]) > parseFloat(b[i])){
      return true;
    }else if(parseFloat(a[i]) < parseFloat(b[i])){
      return false;
    }
  }
  return false;
}

// Compare two running times, return true if A > B
function compareRunning(a, b) {
    // Do either have a day?
    // include special case: 1 day, *
    if (/^\d* days?, .*$/.test(a) || /^\d* days?, .*$/.test(b)) {
      
      // Capture the groups
      one = a.match(/^(\d*) days?, (.*)$/);
      two = b.match(/^(\d*) days?, (.*)$/);

      // Does only one option have a day group?
      if (one === null || two === null) {
        return one !== null;
      }

      // Are the days equal?[index = 1 is day]
      // index    0             1         2 
      // 1 day, 6:22:22.369723, 1, 6:22:22.369723
      if (parseInt(one[1]) === parseInt(two[1])) {
        // Data.parse does not work
        return parseRunningAndCompare(one[2],two[2]);
      }

      // Days are not equal
      // Compare as two times (days)
      return parseInt(one[1]) > parseInt(two[1]);
    }

    // Compare as two times
    return parseRunningAndCompare(a,b);
}

// If headers are clicked, clear table and pagination features
$(document).ready(function() {
  $(".content-table th").click(function() {
    $("#table-body").empty();
    $("#pagination-wrapper").empty();
  });
});

// ajax code to send request, get data, sort, build table.
// ajax has its own range, value changes only works within ajax code range
function tableSort(headerIndex){
  $.ajax({
      url: targetURL,
      type: 'POST',
      success: function(result) {
        tableData = result.rowsList;
        tableDataToString();
        Sort(headerIndex,tableData,currentIsAscending);
        state.querySet = tableData;
        buildTable(targetURL);
      }
    });
}

function setTargetURL(urlInput){
  targetURL = urlInput;
}

// header click event listener
$(document).ready(function() {
  document.querySelectorAll(".content-table th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        // Check previous header index
        if(previousHeaderInder == headerIndex){
          currentIsAscending = !currentIsAscending;
        }else{
          previousHeaderInder = headerIndex;
          currentIsAscending = true;
        }
        // sort data and clear tableData
        tableSort(headerIndex);
        tableData=[];
    });
  });
});