last100DisplayChart()
function last100DisplayChart(){
    $.ajax({
        url: '/replicatesLatest100',
        type: 'POST',
        success: function(result) {
            var runningTimeListFinished = result.runningTimeListFinished
            var ReplicateID = result.ReplicateID
            var runningTimeListUnfinished = result.runningTimeListUnfinished
            var runningTimeListWorth = result.runningTimeListWorth
            var filesName = result.filesName
            var units = result.units
            var last100Time = result.last100Time
            let last100Chart = document.getElementById('last100Chart').getContext('2d');
            let runningTimeChart = new Chart(last100Chart, {
              type: 'line',
                data: {
                    datasets: [{
                        label: 'Last 100 Replicates Finished',
                        data: runningTimeListFinished,
                        fill: true,
                        borderColor:"rgb(11,102,35,1)",
                        backgroundColor:"rgb(11,102,35,1)",
                        pointBorderColor: "rgb(11,102,35,1)",
                        pointBackgroundColor: "rgb(11,102,35,1)",
                        pointStyle:'triangle',
                        pointRadius:4,
                        spanGaps: false,
                        showLine: false
                    },{
                        label: 'Last 100 Replicates Unfinished',
                        data: runningTimeListUnfinished,
                        fill: true,
                        borderColor: "rgba(0,0,255,1)",
                        backgroundColor:"rgba(0,0,255,1)",
                        pointBorderColor: "rgba(0,0,255,1)",
                        pointBackgroundColor: "rgba(0,0,255,1)",
                        pointStyle:'circle',
                        pointRadius:4,
                        spanGaps:false,
                        showLine: false
                    },{
                        label: 'Last 100 Replicates Worth to Notice',
                        data: runningTimeListWorth,
                        fill: true,
                        borderColor: "rgba(255,0,0,1)",
                        backgroundColor:"rgba(255,0,0,1)",
                        pointBorderColor: "rgba(255,0,0,1)",
                        pointBackgroundColor: "rgba(255,0,0,1)",
                        pointStyle:'crossRot',
                        pointRadius:4,
                        spanGaps:false,
                        showLine: false
                    }],
                    labels: ReplicateID
                },
                options: {
                    title: { 
                        display: true,
                        text: "Lastest 100 replicates"
                    },
                    scales:{
                        yAxes: [{
                            gridLines: { display: true },
                            barPercentage: 0.2, maintainAspectRatio: false,
                            scaleLabel: {
                                display: true,
                                labelString: 'running time ('+units+')'
                            }
                        }],
                        xAxes: [{
                            gridLines: {display: false},
                        }]
                    },
                    tooltips: {
                        callbacks: {
                            // Second line
                            label: function(tooltipItem, data) {
                                // var label = data.datasets[tooltipItem.datasetIndex].label || '';
                                var label ='running time ('+units+')';
            
                                if (label) {
                                    label += ': ';
                                }
                                // second line
                                // Can be used as index
                                label += last100Time[tooltipItem.xLabel-1];
                                return label;
                            },
                            // First line
                            title: function(tooltipItem){
                                var title = "Name: " + filesName[tooltipItem[0].xLabel-1];
                                return title
                            }
                        }
                    }
                }
            });
        }
    });
}