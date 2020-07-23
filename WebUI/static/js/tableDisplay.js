//Reference: https://dennis-sourcecode.herokuapp.com/7/
var state = {
  'querySet': tableDataTmp,
  'page': 1,
  'rows': 10,
  'window': 5,
}
last100Display()

// send request, get data, store data, and build table
function last100Display(){
  $.ajax({
      url: '/replicatesLatest100',
      type: 'POST',
      success: function(result) {
        tableDataTmp = result.rowsList
        state.querySet = tableDataTmp
        buildTable()
      }
    });
}

// pagination
function pagination(querySet, page, rows) {
  var trimStart = (page - 1) * rows
  var trimEnd = trimStart + rows
  var trimmedData = querySet.slice(trimStart, trimEnd)
  var pages = Math.round(querySet.length / rows);
  return {
    'querySet': trimmedData,
    'pages': pages,
  }
}

// add pagination buttons
function pageButtons(pages) {
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

    buildTable()
  })
}

// build table dynamically
function buildTable() {
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
              <td>${myList[i][4]}</td>
              <td>${myList[i][5]}</td>
              `
    table.append(row)
  }
  pageButtons(data.pages)
}