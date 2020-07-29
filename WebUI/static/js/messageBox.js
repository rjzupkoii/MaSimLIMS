function messageBoxAdjust(boxID, tableID){
  // Spread
  var offsetWidth = document.getElementById(tableID).offsetWidth;
  document.getElementById(boxID).style.width = String(offsetWidth).concat("px");
}