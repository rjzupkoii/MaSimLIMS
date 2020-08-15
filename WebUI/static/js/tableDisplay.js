//Reference: https://dennis-sourcecode.herokuapp.com/7/
var tableDataTmp;
var state = {
  'querySet': tableDataTmp,
  'page': 1,
  'rows': 20,
  'window': 5,
}

// send request, get data, store data, and build table
function tableDisplay(targetURL,boxID, tableID){
  $.ajax({
      url: targetURL,
      type: 'POST',
      success: function(result) {
        tableDataTmp = result.rowsList
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
  for (var page = maxLeft; page <= maxRight; page++) {
    wrapper.innerHTML += `<button value=${page} class="page pageNum">${page}</button>`
  }

  if (state.page != 1) {
    wrapper.innerHTML = `<button value=${1} class="page pageNum">&#171; First</button>` + wrapper.innerHTML
  }

  if (state.page != pages) {
    wrapper.innerHTML += `<button value=${pages} class="page pageNum">Last &#187;</button>`
  }

  $('.page').on('click', function() {
    $('#table-body').empty()

    state.page = Number($(this).val())

    buildTable(targetURL)
  })
}

// TODO Clean this function up so that it takes a JavaScript function as a parameter, that function should then
//      pass the current myList[i] to the function and it will return the HTML row. This allows for better 
//      separation of concerns since the code for how to create the table row can be maintained with the .html
function buildTable(targetURL) {
  const LONG_RUNNING = 96 * 3600; // Time in seconds
  
  var table = $('#table-body')
  var data = pagination(state.querySet, state.page, state.rows)
  var myList = data.querySet

  for (var i = 1 in myList) {
    //Keep in mind we are using "Template literal's to create rows"
    var row = `<tr>
              <td>${myList[i][0]}</td>
              <td>${myList[i][1]}</td>
              <td>${myList[i][2]}</td>
              <td>${myList[i][3]}</td>`;

    if (targetURL == '/worthToNotice'){
      console.log(myList[i][5])
      if(myList[i][5] >= LONG_RUNNING){
<<<<<<< HEAD
        // working
        // row = row + `<td>
        //               <button id="ReplicateBtn" onclick="return deleteReplicate('${myList[i][4]}');">[DELETE]</button>
        //             </td>`
        row = row + `<td><input type="checkbox" id="checks" name="checks" value="delete_${myList[i][4]}" onclick="savedRows()">Delete</td>`
        // <input type="checkbox" id="checks" name="checks" value="delete_${myList[i][4]}">
        // <label for="checks">Delete?</label>
      }else{
        row = row + `<td> </td>`
=======
        row = row + `<td><button id="ReplicateBtn" onclick="return deleteReplicate('${myList[i][4]}');">[DELETE]</button></td>`;
      } else{
        row = row + `<td> </td>`;
>>>>>>> upstream/master
      }

    } else if(targetURL == '/replicatesLatest100'){
      row +=  `<td>${myList[i][4]}</td><td>${myList[i][5]}</td>`;

    } else if(targetURL.includes('/StudyReplicate') || targetURL.includes('/ConfigReplicate')){
      row += `<td>${myList[i][4]}</td>`;

    } else if(targetURL.includes('/StudyConfig')){
      var row = `<tr>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${myList[i][3]}');" id="ReplicateBtn">${myList[i][0]}</button></td>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${myList[i][3]}');" id="ReplicateBtn">${myList[i][1]}</button></td>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${myList[i][3]}');" id="ReplicateBtn">${myList[i][2]}</button></td>`;

    } else if(targetURL.includes('/study')){
      row = studyRowBuilder(myList[i]);

    } else if(targetURL.includes('/Study/Notes/')){
      // working
      var row = `<tr>
                  <td><a style="text-decoration:none; color:#000000">${myList[i][0]}</a></td>
                  <td><a style="text-decoration:none; color:#000000">${myList[i][1]}</a></td>
                  <td><a style="text-decoration:none; color:#000000">${myList[i][2]}</a></td>
                  <td><button id="delete" onclick="return deleteNote(${myList[i][4]}, ${myList[i][3]});">[DELETE]</button></td>`;

    } else if(targetURL.includes('/Study/Chart/')){
      row += `<td>${myList[i][4]}</td>`

    } else{
      console.log(targetURL)
    }

    table.append(row)
  }
  pageButtons(data.pages, targetURL)
}

// Example of row builder function - this would go in the .html file
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
    row += `<td><button onclick="pageRedirection('/Study/Notes/'+'${data[1]}');" id="ReplicateBtn">[NOTES]</button>
                     <button onclick="pageRedirection('/Study/Chart/'+'${data[1]}');" id="ReplicateBtn">[CHART]</button>`;

    // If there are no replicates or configurations, we can delete
    if(parseInt(data[2])==0 &&  parseInt(data[3])==0) {
      row += `<button id="delete" onclick="return deleteNote('${data[1]}');">[DELETE]</button>`;
    }

    // Close out the element
    row += `</td>`;
  } else {
    // No study id means this is the catch all
    row += `<td><a style="text-decoration:none; color:#000000">No Notes Available</a></td>`
  }

  return row;
}