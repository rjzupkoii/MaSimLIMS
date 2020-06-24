const Notes = document.getElementById('notes');
const Remaining = document.getElementById('remaining');
var saveNotes = document.getElementById('saveNotes');
/* disable the input button*/
saveNotes.disabled = true
const max = 32;
notes.addEventListener('input',() =>{
    const r = max - Notes.value.length;
    const total = Notes.value.length;
    if(r <= 0){
        Remaining.textContent = `total ${total} characters`;
        document.getElementById('saveNotes').disabled = false;
    }
    else{
        Remaining.textContent = `${r} characters remaining`;
    }
})
