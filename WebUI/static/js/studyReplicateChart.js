function studyReplicateChart(targetURL) {
    $.ajax({
        url: targetURL,
        type: 'POST',
        success: function(result) {

            // Load is complete, toggle elements
            $('#pageLoading').hide();
            $('#chartMessage').show();

            // Parse the results for the chart
            var runningTimeListFinished = result.runningTimeListFinished;
            var runningTimeListUnfinished = result.runningTimeListUnfinished;
            var runningTimeListWorth = result.runningTimeListWorth;
            var filesName = result.filesName;
            var units = result.units;
            var ReplicateID = result.ReplicateID;
            var studyName = result.studyname;
            var allRunningTime = result.allRunningTime;

            statistics(runningTimeListFinished.filter(function (element) {return element != null;}), studyName, units, result.finishedCount);

            let last100Chart = document.getElementById('studyReplicateChart').getContext('2d');
            new Chart(last100Chart, {
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
                        fontSize:18,
                        display: true,
                        text: '\'' + studyName + '\'' + " - replicates"
                    },
                    scales:{
                        yAxes: [{
                            gridLines: { display: true },
                            barPercentage: 0.2, maintainAspectRatio: false,
                            scaleLabel: {
                                fontSize: 15,
                                display: true,
                                labelString: 'running time ('+units+')'
                            },
                            ticks:{
                                fontSize: 15,
                            }
                        }],
                        xAxes: [{
                            gridLines: {display: false},
                            ticks:{
                                display: false,
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

function statistics(allRunningTime, studyname, units, finishedCount){
    // Get the basic statistics on everything
    var standard = math.round(math.std(allRunningTime, 'uncorrected'), 2);
    var max = math.round(math.max(allRunningTime), 2);
    var min = math.round(math.min(allRunningTime), 2);
    var mean = math.round(math.mean(allRunningTime), 2);
    var sum = math.round(math.sum(allRunningTime), 2);

    // Generate the HTML and place it
    var statisticsPlace = $('#statistics');
    var rows = `<p>Statistics of Replicates from \'${studyname}\' </p>
                Completed Replicates: ${finishedCount} / ${sum} ${units} total CPU time<br /><br />
                Mean: ${mean} (${units}) (Standard Deviation: ${standard})<br /><br />
                Range: ${min} to ${max} (${units})`
    statisticsPlace.append(rows);
}