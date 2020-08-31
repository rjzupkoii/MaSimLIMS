// site.js
//
// JavaScript functions used by the MaSim LIMS.

// ---------------------------------------------------------------------------
// Common functions of use on most / all of the MaSim LIMS pages.
// ---------------------------------------------------------------------------

// used to adjust the width of message box
function messageBoxAdjust(boxID, tableID){
    var offsetWidth = document.getElementById(tableID).offsetWidth;
    document.getElementById(boxID).style.width = String(offsetWidth).concat("px");
}


// Redirect to a new page
function pageRedirection(targetURL){
    $.ajax({
        url: targetURL,
        type: 'POST',
        success: function(result) {
          // define new page open style
          if(targetURL.includes('Study/Chart/')){
            var redirectWindow = window.open(targetURL, '_blank');
            redirectWindow.location;
          }else{
            window.location.assign(targetURL)
          }
        }
      });
}


// ---------------------------------------------------------------------------
// Functions that are specific to given pages.
// ---------------------------------------------------------------------------

// From record.js replicatesList = []; is removed to html file
// store selected long running replicates
function record(param,valueID){
  if(param.checked){
    replicatesList.push(valueID);
  }else{
    replicatesList = replicatesList.filter(function(value, index, arr){ return value != valueID;});
  }
}


// pass replicate list to view
function passReplicateList(){
  if (confirm("Are you sure you wish to delete these replicates?")) {
    $.ajax({
      url: '/longRunningDelete',
      type: 'POST',
      data: {'tasks[]':replicatesList},
      success: function(result) {
        if(result.success){
          alert("Replicates deleted!");
        }else{
          alert("Replicates Delete Operation Fail!");
        }
        location.reload();
      }
    });
  }
}


// Used for creating study replicate chart
function studyReplicateChart(targetURL) {
  $.ajax({
      url: targetURL,
      type: 'POST',
      success: function(result) {
          // Load is complete, toggle elements
          $('#pageLoading').hide();
          $('#chartMessage').show();
          // Parse the results for the chart
          var runningTimeListFinished = result.runningTimeListFinished;
          var runningTimeListUnfinished = result.runningTimeListUnfinished;
          var runningTimeListWorth = result.runningTimeListWorth;
          var filesName = result.filesName;
          var units = result.units;
          var ReplicateID = result.ReplicateID;
          var studyName = result.studyname;
          var allRunningTime = result.allRunningTime;
          // Send value to statistics for computation
          statistics(runningTimeListFinished.filter(function (element) {return element != null;}), studyName, units, result.finishedCount);
          // Get canvas
          let last100Chart = document.getElementById('studyReplicateChart').getContext('2d');
          // Create chart
          new Chart(last100Chart, {
            type: 'line',
              data: {
                  datasets: [{
                      // for finished replicates
                      label: 'Replicates Finished',
                      data: runningTimeListFinished,
                      fill: true,
                      borderColor:"rgb(11,102,35,1)",
                      backgroundColor:"rgb(11,102,35,1)",
                      pointBorderColor: "rgb(11,102,35,1)",
                      pointBackgroundColor: "rgb(11,102,35,1)",
                      pointStyle:'triangle',
                      pointRadius:4,
                      spanGaps: false,
                      showLine: false
                  },{
                      // for unfinished replicates
                      label: 'Replicates Unfinished',
                      data: runningTimeListUnfinished,
                      fill: true,
                      borderColor: "rgba(0,0,255,1)",
                      backgroundColor:"rgba(0,0,255,1)",
                      pointBorderColor: "rgba(0,0,255,1)",
                      pointBackgroundColor: "rgba(0,0,255,1)",
                      pointStyle:'circle',
                      pointRadius:4,
                      spanGaps:false,
                      showLine: false
                  },{
                      // for replicates that is worth to notice
                      label: 'Replicates Worth to Notice',
                      data: runningTimeListWorth,
                      fill: true,
                      borderColor: "rgba(255,0,0,1)",
                      backgroundColor:"rgba(255,0,0,1)",
                      pointBorderColor: "rgba(255,0,0,1)",
                      pointBackgroundColor: "rgba(255,0,0,1)",
                      pointStyle:'crossRot',
                      pointRadius:4,
                      spanGaps:false,
                      showLine: false
                  }],
                  labels: ReplicateID
              },
              options: {
                  // title attributes
                  title: { 
                      fontSize:18,
                      display: true,
                      text: '\'' + studyName + '\'' + " - replicates"
                  },
                  scales:{
                      // y axes attributes
                      yAxes: [{
                          gridLines: { display: true },
                          barPercentage: 0.2, maintainAspectRatio: false,
                          scaleLabel: {
                              fontSize: 15,
                              display: true,
                              labelString: 'running time ('+units+')'
                          },
                          ticks:{
                              fontSize: 15,
                          }
                      }],
                      // x axes attributes
                      xAxes: [{
                          gridLines: {display: false},
                          ticks:{
                              display: false,
                          }
                      }]
                  },
                  tooltips: {
                      callbacks: {
                          // Second line
                          label: function(tooltipItem, data) {
                              // var label = data.datasets[tooltipItem.datasetIndex].label || '';
                              var label ='running time ('+units+')';
                              if (label) {
                                  label += ': ';
                              }
                              // second line
                              // Can be used as index
                              label += allRunningTime[tooltipItem.xLabel-1];
                              return label;
                          },
                          // First line
                          title: function(tooltipItem){
                              var title = "Name: " + filesName[tooltipItem[0].xLabel-1];
                              return title
                          }
                      }
                  }
              }
          });
      }
  });
}


// Used for computing standard deviation, maximum, minimum, mean, and sum of running time.
function statistics(allRunningTime, studyname, units, finishedCount){
  // Get the basic statistics on everything
  var standard = math.round(math.std(allRunningTime, 'uncorrected'), 2);
  var max = math.round(math.max(allRunningTime), 2);
  var min = math.round(math.min(allRunningTime), 2);
  var mean = math.round(math.mean(allRunningTime), 2);
  var sum = math.round(math.sum(allRunningTime), 2);

  // Generate the HTML and place it
  var statisticsPlace = $('#statistics');
  var rows = `<p>Statistics of Replicates from \'${studyname}\' </p>
              Completed Replicates: ${finishedCount} / ${sum} ${units} total CPU time<br /><br />
              Mean: ${mean} (${units}) (Standard Deviation: ${standard})<br /><br />
              Range: ${min} to ${max} (${units})`
  statisticsPlace.append(rows);
}


// Used for the display of the last 100 replicates
function last100DisplayChart(){
  $.ajax({
      url: '/replicatesLatest100',
      type: 'POST',
      success: function(result) {
          // Load is complete, toggle elements
          $('#pageLoading').hide();
          $('#chartMessage').show();
          // Get data
          var runningTimeListFinished = result.runningTimeListFinished;
          var ReplicateID = result.ReplicateID;
          var runningTimeListUnfinished = result.runningTimeListUnfinished;
          var runningTimeListWorth = result.runningTimeListWorth;
          var filesName = result.filesName;
          var units = result.units;
          var last100Time = result.last100Time;
          let last100Chart = document.getElementById('last100Chart').getContext('2d');
          let runningTimeChart = new Chart(last100Chart, {
            type: 'line',
              data: {
                  datasets: [{
                      // for data finished
                      label: 'Last 100 Replicates Finished',
                      data: runningTimeListFinished,
                      fill: true,
                      borderColor:"rgb(11,102,35,1)",
                      backgroundColor:"rgb(11,102,35,1)",
                      pointBorderColor: "rgb(11,102,35,1)",
                      pointBackgroundColor: "rgb(11,102,35,1)",
                      pointStyle:'triangle',
                      pointRadius:4,
                      spanGaps: false,
                      showLine: false
                  },{
                      // for data unfinished
                      label: 'Last 100 Replicates Unfinished',
                      data: runningTimeListUnfinished,
                      fill: true,
                      borderColor: "rgba(0,0,255,1)",
                      backgroundColor:"rgba(0,0,255,1)",
                      pointBorderColor: "rgba(0,0,255,1)",
                      pointBackgroundColor: "rgba(0,0,255,1)",
                      pointStyle:'circle',
                      pointRadius:4,
                      spanGaps:false,
                      showLine: false
                  },{
                      // for data that is worth to notice
                      label: 'Last 100 Replicates Worth to Notice',
                      data: runningTimeListWorth,
                      fill: true,
                      borderColor: "rgba(255,0,0,1)",
                      backgroundColor:"rgba(255,0,0,1)",
                      pointBorderColor: "rgba(255,0,0,1)",
                      pointBackgroundColor: "rgba(255,0,0,1)",
                      pointStyle:'crossRot',
                      pointRadius:4,
                      spanGaps:false,
                      showLine: false
                  }],
                  labels: ReplicateID
              },
              options: {
                  // title of the chart
                  title: {
                      fontSize:18,
                      display: true,
                      text: "Lastest 100 replicates"
                  },
                  scales:{
                      // y axes attributes
                      yAxes: [{
                          gridLines: { display: true },
                          barPercentage: 0.2, maintainAspectRatio: false,
                          scaleLabel: {
                              fontSize: 15,
                              display: true,
                              labelString: 'running time ('+units+')'
                          },
                          ticks:{
                              fontSize: 15,
                          }
                      }],
                      // x axes attributes
                      xAxes: [{
                          gridLines: {display: false},
                          ticks:{
                              display: false,
                          }
                      }]
                  },
                  tooltips: {
                      callbacks: {
                          // Second line
                          label: function(tooltipItem, data) {
                              // var label = data.datasets[tooltipItem.datasetIndex].label || '';
                              var label ='running time ('+units+')';
          
                              if (label) {
                                  label += ': ';
                              }
                              // second line
                              // Can be used as index
                              label += last100Time[tooltipItem.xLabel-1];
                              return label;
                          },
                          // First line
                          title: function(tooltipItem){
                              var title = "Name: " + filesName[tooltipItem[0].xLabel-1];
                              return title;
                          }
                      }
                  }
              }
          });
      }
  });
}


// ---------------------------------------------------------------------------
// The following functions are for tables and may be capable of being adopted 
// for multiple websites
// ---------------------------------------------------------------------------

// Send request, get data, store data, and build table
// Reference: https://dennis-sourcecode.herokuapp.com/7/
function tableDisplay(targetURL,boxID, tableID){
  $.ajax({
      url: targetURL,
      type: 'POST',
      success: function(result) {
        var tableDataTmp = result.rowsList
        state.querySet = tableDataTmp
        buildTable(targetURL)
        messageBoxAdjust(boxID, tableID)
        const loader = document.querySelector(".pageLoading");
        $(".pageLoading").fadeOut();
      }
    });
}


// pagination
function pagination(querySet, page, rows) {
  var trimStart = (page - 1) * rows
  var trimEnd = trimStart + rows
  var trimmedData = querySet.slice(trimStart, trimEnd)
  var pages = Math.ceil(querySet.length / rows);
  return {
    'querySet': trimmedData,
    'pages': pages,
  }
}


// add pagination buttons
function pageButtons(pages, targetURL) {
  var wrapper = document.getElementById('pagination-wrapper')
  wrapper.innerHTML = ``
  // max left and max right used for show left most, right most page number
  var maxLeft = (state.page - Math.floor(state.window / 2))
  var maxRight = (state.page + Math.floor(state.window / 2))
  if (maxLeft < 1) {
    maxLeft = 1
    maxRight = state.window
  }
  if (maxRight > pages) {
    maxLeft = pages - (state.window - 1) 
    if (maxLeft < 1){
      maxLeft = 1
    }
    maxRight = pages
  }
  // Add button to corresponding place
  for (var page = maxLeft; page <= maxRight; page++) {
    wrapper.innerHTML += `<button value=${page} class="page pageNum">${page}</button>`
  }
  // If current page is not first page, add First button
  if (state.page != 1) {
    wrapper.innerHTML = `<button value=${1} class="page pageNum">&#171; First</button>` + wrapper.innerHTML
  }
  // If current page is not last page, add Last button
  if (state.page != pages) {
    wrapper.innerHTML += `<button value=${pages} class="page pageNum">Last &#187;</button>`
  }
  // If go to new page, clean table and rebuild it
  $('.page').on('click', function() {
    $('#table-body').empty()
    state.page = Number($(this).val())
    buildTable(targetURL)
  })
}


// Build up table (Although this function contains some html code, it is better for js code to stay inside .js file)
function buildTable(targetURL) {
  const LONG_RUNNING = 96 * 3600; // Time in seconds
  var table = $('#table-body')
  // Hide the pagination controls when there is only one page for the table
  // rows can be showed in one page
  if(state.querySet.length <= state.rows){
    $('#pagination-wrapper').hide();
  }
  var data = pagination(state.querySet, state.page, state.rows)
  var myList = data.querySet
  for (var i = 1 in myList) {
    //Keep in mind we are using "Template literal's to create rows"
    if (targetURL == '/worthToNotice'){
      row = longRunningRowBuilder(myList[i]);
    } else if(targetURL == '/replicatesLatest100'){
      row = sixDataRowBuilder(myList[i]);
    } else if(targetURL.includes('/StudyReplicate')){
      row = sixDataRowBuilder(myList[i]);
    } else if(targetURL.includes('/ConfigReplicate')){
      row = fiveDataRowBuilder(myList[i]);
    } else if(targetURL.includes('/StudyConfig')){
      row = studyConfigRowBuilder(myList[i]);
    } else if(targetURL.includes('/study')){
      row = studyRowBuilder(myList[i]);
    } else if(targetURL.includes('/Study/Notes/')){
      row = studyNotesRowBuilder(myList[i]);
    } else if(targetURL.includes('/Study/Chart/')){
      row = fiveDataRowBuilder(myList[i]);
    } else if(targetURL == '/'){
      row = fiveDataRowBuilder(myList[i]);
    } else{
      var row = `<tr>
              <td>${myList[i][0]}</td>
              <td>${myList[i][1]}</td>
              <td>${myList[i][2]}</td>
              <td>${myList[i][3]}</td>`;
    }
    table.append(row)
  }
  pageButtons(data.pages, targetURL)
}


// five data row builder
function fiveDataRowBuilder(data){
  var row = `<tr>
              <td>${data[0]}</td>
              <td>${data[1]}</td>
              <td>${data[2]}</td>
              <td>${data[3]}</td>
              <td>${data[4]}</td>`;
  return row;
}


// six data row builder
function sixDataRowBuilder(data){
  var row = fiveDataRowBuilder(data);
  row += `<td>${data[5]}</td>`;
  return row;
}


// data = myList[i]
// long running replicates row builder
function longRunningRowBuilder(data){
  const LONG_RUNNING = 96 * 3600;
  var row = `<tr>
              <td>${data[0]}</td>
              <td>${data[1]}</td>
              <td>${data[2]}</td>
              <td>${data[3]}</td>`;
  if(data[5] >= LONG_RUNNING){
    row = row + `<td><input type="checkbox" name="checkboxs" value="${data[4]}" onclick="record(this, value)">Delete</td>`
  } else{
    row = row + `<td> </td>`;
  }
  return row;
}


// study notes row builder
function studyNotesRowBuilder(data){
  var row = `<tr>
              <td><a style="text-decoration:none; color:#000000">${data[0]}</a></td>
              <td><a style="text-decoration:none; color:#000000">${data[1]}</a></td>
              <td><a style="text-decoration:none; color:#000000">${data[2]}</a></td>
              <td><button id="delete" onclick="return deleteNote(${data[4]}, ${data[3]});">[DELETE]</button></td>`;
  return row;
}


// study configuration table row builder 
function studyConfigRowBuilder(data){
  var configurationID = data[3]
  var row = `<tr>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${configurationID}');" id="ReplicateBtn">${data[0]}</button></td>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${configurationID}');" id="ReplicateBtn">${data[1]}</button></td>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${configurationID}');" id="ReplicateBtn">${data[2]}</button></td>`;
  return row
}


// Study row builder 
function studyRowBuilder(data) {
  var studyID = 'None'
  if(data[1]){
    studyID = data[1]
  }
  var row = `<tr><td><button onclick="pageRedirection('/StudyConfig/'+'${studyID}');" id="ConfigBtn">${data[0]}</button></td> 
                 <td><button onclick="pageRedirection('/StudyConfig/'+'${studyID}');" id="ConfigBtn">${data[1]}</button></td> 
                 <td><button onclick="pageRedirection('/StudyConfig/'+'${studyID}');" id="ConfigBtn">${data[2]}</button></td>
                 <td><button onclick="pageRedirection('/StudyReplicate/'+'${studyID}');" id="ReplicateBtn">${data[3]}</button></td>`;

  // If there is a study id we can add common functions
  if (data[1]) {
    row += `<td><button onclick="pageRedirection('/Study/Notes/'+'${data[1]}');" id="ReplicateBtn">[NOTES]</button>`;
    // If there are no replicates and configurations, we can delete
    if(parseInt(data[2])==0 &&  parseInt(data[3])==0) {
      row += `<button id="delete" onclick="return deleteNote('${data[1]}');">[DELETE]</button>`;
    }
    // Only provide chart service when they have replicates
    if(parseInt(data[3])!=0){
      row += `<button onclick="pageRedirection('/Study/Chart/'+'${data[1]}');" id="ReplicateBtn">[CHART]</button>`
    }
    // Close out the element
    row += `</td>`;
  } else {
    // No study id means this is the catch all
    row += `<td><a style="text-decoration:none; color:#000000">No Notes Available</a></td>`
  }
  return row;
}


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
  var bIndex = 1;
  var track = bIndex;
  var aIndex = 0;
  for(bIndex; bIndex <= (orignal.length-1);bIndex++){
    track = bIndex;
    for(aIndex=bIndex-1; aIndex >= 0; aIndex--){
      var returnVal = compare(tableData[aIndex][column].trim(),tableData[track][column].trim());
      // If asc is true, returnVal is true when a (previous) > b (next), so we need to switch and make small one on top
      if(asc){
        if(returnVal){
          // swap and keep tracking
          var tmp = tableData[aIndex];
          tableData[aIndex] = tableData[track];
          tableData[track] = tmp;
          track = aIndex;
        }else{
          break;
        }
      }
      // If asc is false, returnVal is not true, swap.
      else{
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


// Compare date
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


// Compare running time and return true if A > B (format of running time, i.e. -> 0:18:47.639582)
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

// set global variable targetURL value, we use it a lot
function setTargetURL(urlInput){
  targetURL = urlInput;
}


// header click event listener
$(document).ready(function() {
  // Select targets
  document.querySelectorAll(".content-table th").forEach(headerCell => {
    // click event
    headerCell.addEventListener("click", () => {
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        // Check previous header index each header has its separate "asc" value
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