last100Display()
function last100Display(){
    $.ajax({
        url: '/replicatesLatest100',
        type: 'POST',
        success: function(result) {
            var runningTimeListFinished = result.runningTimeListFinished
            var ReplicateID = result.ReplicateID
            var runningTimeListUnfinished = result.runningTimeListUnfinished
            var runningTimeListWorth = result.runningTimeListWorth
            let last100Chart = document.getElementById('last100Chart').getContext('2d');
            let runningTimeChart = new Chart(last100Chart, {
              type: 'line',
                data: {
                    datasets: [{
                        label: 'Last 100 Replicates Finished',
                        data: runningTimeListFinished,
                        fill: false,
                        borderColor: "rgb(0,255,0,1)",
                        pointBorderColor: "black",
                        pointBackgroundColor: "white",
                        spanGaps: true,
                    },{
                        label: 'Last 100 Replicates Unfinished',
                        data: runningTimeListUnfinished,
                        fill: false,
                        borderColor: "rgba(0,0,255,1)",
                        pointBorderColor: "black",
                        pointBackgroundColor: "white",
                        pointStyle:'triangle',
                        spanGaps: true
                    },{
                        label: 'Last 100 Replicates Worth to Notice',
                        data: runningTimeListWorth,
                        fill: false,
                        borderColor: "rgba(255,0,0,1)",
                        pointBorderColor: "black",
                        pointBackgroundColor: "white",
                        pointStyle:'rect',
                        spanGaps: true
                    }],
                    labels: ReplicateID
                },
                options: {}
            });
        }
    });
}