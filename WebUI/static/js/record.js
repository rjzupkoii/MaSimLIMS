replicatesList = [];
function record(param,valueID){
  if(param.checked){
    replicatesList.push(valueID);
  }else{
    replicatesList = replicatesList.filter(function(value, index, arr){ return value != valueID;});
  }
}

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