function studyReplicateChart(targetURL){
    $.ajax({
        url: targetURL,
        type: 'POST',
        success: function(result) {
            var runningTimeListFinished = result.runningTimeListFinished
            var runningTimeListUnfinished = result.runningTimeListUnfinished
            var runningTimeListWorth = result.runningTimeListWorth
            var filesName = result.filesName
            var units = result.units
            var ReplicateID = result.ReplicateID
            var studyName = result.studyname
            var allRunningTime = result.allRunningTime
            var finishedCount = result.finishedCount
            statistics(allRunningTime,studyName,units,finishedCount)
            let last100Chart = document.getElementById('studyReplicateChart').getContext('2d');
            let runningTimeChart = new Chart(last100Chart, {
              type: 'line',
                data: {
                    datasets: [{
                        label: 'Replicates Finished',
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
                        label: 'Replicates Unfinished',
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
                        label: 'Replicates Worth to Notice',
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
                        text: '\'' + studyName + '\'' + " - replicates"
                    },
                    scales:{
                        yAxes: [{
                            gridLines: { display: false },
                            barPercentage: 0.2, maintainAspectRatio: false,
                            scaleLabel: {
                                display: true,
                                labelString: 'running time ('+units+')'
                            }
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
                                label += allRunningTime[tooltipItem.xLabel-1];
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

function statistics(allRunningTime,studyname,units,finishedCount){
  // standard deviation for all.
  var standard = math.round(math.std(allRunningTime, 'uncorrected'),2);
  var max = math.round(math.max(allRunningTime),2);
  var min = math.round(math.min(allRunningTime),2);
  var mean = math.round(math.mean(allRunningTime),2);
  var statisticsPlace = $('#statistics');
  var rows = `<p>Statistics of replicates on study (${units}) - \'${studyname}\' </p>
            <p>Number that finished: ${finishedCount};&nbsp&nbspStandard deviation for all data: ${standard};&nbsp&nbspMaximum for all data: ${max};&nbsp&nbspMinimum for all data: ${min};&nbsp&nbspMean for all data: ${mean}</p>`
  statisticsPlace.append(rows);
}