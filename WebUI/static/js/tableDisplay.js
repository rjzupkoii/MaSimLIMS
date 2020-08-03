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
      }
    });
}


function messageBoxAdjust(boxID, tableID){
  // Spread
  var offsetWidth = document.getElementById(tableID).offsetWidth;
  document.getElementById(boxID).style.width = String(offsetWidth).concat("px");
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

// build table dynamically
function buildTable(targetURL) {
  console.log("IN")
  var table = $('#table-body')
  var data = pagination(state.querySet, state.page, state.rows)
  var myList = data.querySet
  for (var i = 1 in myList) {
    //Keep in mind we are using "Template Litterals to create rows"
    var row = `<tr>
              <td>${myList[i][0]}</td>
              <td>${myList[i][1]}</td>
              <td>${myList[i][2]}</td>
              <td>${myList[i][3]}</td>
              `
    if(targetURL == '/replicatesLatest100'){
      row =  row +  `
                    <td>${myList[i][4]}</td>
                    <td>${myList[i][5]}</td>
                    `
    }else if(targetURL.includes('/StudyReplicate') || targetURL.includes('/ConfigReplicate')){
      row = row + `
                      <td>${myList[i][4]}</td>
                      `
    }else if(targetURL.includes('/StudyConfig')){
      var row = `<tr>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${myList[i][3]}');" id="ReplicateBtn">${myList[i][0]}</button></td>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${myList[i][3]}');" id="ReplicateBtn">${myList[i][1]}</button></td>
                  <td><button onclick="pageRedirection('/ConfigReplicate/'+'${myList[i][3]}');" id="ReplicateBtn">${myList[i][2]}</button></td>`
    }else if(targetURL.includes('/study')){
      var studyID;
      if(myList[i][1]){
        studyID = myList[i][1]
      }else{
        studyID = 'None'
      }
      console.log(studyID)
      var row = `
              <tr>
              <td><button onclick="pageRedirection('/StudyConfig/'+'${studyID}');" id="ConfigBtn">${myList[i][0]}</button></td> 
              <td><button onclick="pageRedirection('/StudyConfig/'+'${studyID}');" id="ConfigBtn">${myList[i][1]}</button></td> 
              <td><button onclick="pageRedirection('/StudyConfig/'+'${studyID}');" id="ConfigBtn">${myList[i][2]}</button></td>
              <td><button onclick="pageRedirection('/StudyReplicate/'+'${studyID}');" id="ReplicateBtn">${myList[i][3]}</button></td>
              `
      if(parseInt(myList[i][2])==0 &&  parseInt(myList[i][3])==0 && myList[i][1]){
        // myList[i][1] is id
        row = row + `<td>
                      <button onclick="pageRedirection('/Study/Notes/'+'${myList[i][1]}');" id="ReplicateBtn">[NOTES]</button>
                      <button onclick="pageRedirection('/Study/Chart/'+'${myList[i][1]}');" id="ReplicateBtn">[CHART]</button>
                      <button id="delete" onclick="return deleteNote('${myList[i][1]}');">[DELETE]</button>
                      </td>`
      }else if(myList[i][1]){
        row = row + `<td>
                      <button onclick="pageRedirection('/Study/Notes/'+'${myList[i][1]}');" id="ReplicateBtn">[NOTES]</button>
                      <button onclick="pageRedirection('/Study/Chart/'+'${myList[i][1]}');" id="ReplicateBtn">[CHART]</button>
                    </td>`
      }else{
        row = row + `<td>
                      <a style="text-decoration:none; color:#000000">No Notes Available</a>
                    </td>`
      }
    }else if(targetURL.includes('/Study/Notes/')){
      // working
      var row = `<tr>
                  <td><a style="text-decoration:none; color:#000000">${myList[i][0]}</a></td>
                  <td><a style="text-decoration:none; color:#000000">${myList[i][1]}</a></td>
                  <td><a style="text-decoration:none; color:#000000">${myList[i][2]}</a></td>
                  <td>
                    <button id="delete" onclick="return deleteNote(${myList[i][4]}, ${myList[i][3]});">[DELETE]</button>
                  </td>`
    }else if(targetURL.includes('/Study/Chart/')){
      row += `<td>${myList[i][4]}</td>`
    }else{
      console.log(targetURL)
    }
    table.append(row)
  }
  pageButtons(data.pages, targetURL)
}