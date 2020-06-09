// Get DOM Elements
const popUpWindow = document.querySelectorAll('.popUp');
const popUpButton = document.querySelectorAll('.button');
const closeButton = document.querySelectorAll('.close');
var i;
// Add listener
window.addEventListener('click', outsideClick);
for(i = 0; i < popUpButton.length; i++){
    popUpButton[i].addEventListener('click', openPopUp);
}
for(i = 0; i < closeButton.length; i++){
    closeButton[i].addEventListener('click', closePopUp);
}
// Open
function openPopUp() {
    var j;
    var id = this.id.split("-");
    for(j = 0; j < popUpWindow.length;j++){
        if(popUpWindow[j].id.split("-")[1] == id[1]){
            popUpWindow[j].style.display = 'block';
            console.log("openPopUp " + popUpWindow[j]);
        }
    }
}

// Close
function closePopUp() {
    var j;
    var id = this.id.split("-");
    console.log(popUpWindow[0]);
    for(j = 0; j < popUpWindow.length;j++){
        if(popUpWindow[j].id.split("-")[1] == id[1]){
            popUpWindow[j].style.display = 'none';
            console.log("OK");
        }
    }
}

// Close If Outside Click
function outsideClick(e) {
    var j;
    for(j = 0; j < popUpWindow.length;j++){
        if (e.target == popUpWindow[j]) {
            popUpWindow[j].style.display = 'none';
        }
    }
  //console.log("fails outsideclose");
}
