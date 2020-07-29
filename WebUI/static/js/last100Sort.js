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
      var returnVal = compareFunc(tableData[aIndex][column].trim(),tableData[track][column].trim())
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

// compare two inputs: if aColText > bColText, return true, else return false.
function compareFunc(aColText,bColText){
  var index;
  const aTime = new Date(aColText);
  const bTime = new Date(bColText);
  // Time
  if(!isNaN(aTime) && aColText.includes('-')){
      return aTime >= bTime ? true : false;
  }
  else{
      // If it is not a time, separate by ":"
      // For running time
      if(aColText.includes(':')){
          var idA = aColText.split(":");
          var idB = bColText.split(":");
          // A has day, B does not have. A > B
          if(idA[0].includes('day') && !idB.includes('day')){
            return true;
          }
          // A does not have day, B has day. B > A
          else if(!idA[0].includes('day') && idB.includes('day')){
            return false;
          }
          // Both have day
          else if(idA[0].includes('day') && idB.includes('day')){
            var splitBySpaceA = idA[0].split(' ');
            var splitBySpaceB = idB[0].split(' ');
            // day in A > day in B.
            if(parseFloat(splitBySpaceA[0]) > parseFloat(splitBySpaceB[0])){
              return true;
            }else if(parseFloat(splitBySpaceA[0]) < parseFloat(splitBySpaceB[0])){
              return false;
            }
            // day in A == day in B
            else{
              // hour in A > hour in B
              if(parseFloat(splitBySpaceA[2]) > parseFloat(splitBySpaceB[2])){
                return true;
              }else if(parseFloat(splitBySpaceA[2]) < parseFloat(splitBySpaceB[2])){
                return false;
              }
              // idA[0] = idB[0] (both same day and same hour) --> continue comparison
              else{
                index = 1;
              }
            }
          }
          // Both does not have day
          else{
            index = 0
          }
          // Fetch each part and compare.
          for(index; index < idA.length; index++){
              if(parseFloat(idA[index]) > parseFloat(idB[index])){
                  return true;
              }else if(parseFloat(idA[index]) < parseFloat(idB[index])){
                  return false
              }
          }
          // If two values are the same
          return true;
      }
      // Not an integer and not a running time
      else if(isNaN(parseInt(aColText))){
          return aColText >= bColText ? true : false;
      }else{
          // Integer
          return parseInt(aColText) >= parseInt(bColText) ? true : false;
      }
  }
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