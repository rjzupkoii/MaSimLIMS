document.onload = last100;
var tableDataTmp = []
function last100(){
  $.ajax({
      url: '/replicatesLatest100',
      type: 'POST',
      success: function(result) {
        tableDataTmp = result.rowsList
        location.replace('/replicatesLatest100')
      }
    });
}