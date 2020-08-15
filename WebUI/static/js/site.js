// site.js
//
// Common functions of use on most / all of the MaSim LIMS pages.

function messageBoxAdjust(boxID, tableID){
    var offsetWidth = document.getElementById(tableID).offsetWidth;
    document.getElementById(boxID).style.width = String(offsetWidth).concat("px");
}

function pageRedirection(targetURL){
    $.ajax({
        url: targetURL,
        type: 'POST',
        success: function(result) {
          var redirectWindow = window.open(targetURL, '_blank');
          redirectWindow.location;
        }
      });
}