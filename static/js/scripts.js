

var addPlot = function (plotData) {
    
    [yLabel, scaledYData] = getScaledYData(plotData.yData)
    var scatterData = []
    for (i = 0; i < plotData.xData.length; i++) {
        scatterData.push({ x: plotData.xData[i], y: scaledYData[i] })
    }
    var title = plotData.occupationName + ' in ' + plotData.locationName
    var config = {
        type: 'scatter',
        data: {
            // labels: xData_str,
            datasets: [{
                label: 'Number of jobs',
                backgroundColor: '#0000FF',
                borderColor: '#0000FF',
                showLine: true,
                data: scatterData,
                fill: false,
                lineTension: 0,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: title,
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Year'
                    },
                    gridLines: {
                        display: false
                    },
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: yLabel
                    },
                    ticks: {
                        suggestedMax: Math.max(...scaledYData)*1.025,
                        suggestedMin: Math.min(...scaledYData)*0.8,
                        // stepSize: 500,
                    },
                    gridLines: {
                        display: false
                    },
                }]
            },
            legend: {
                display: false,
            },
        }
    };

    addLoadEvent(function () {
        var ctx = document.getElementById(plotData.selector).getContext('2d');
        window.myLine = new Chart(ctx, config);
    }
    )
}

var getScaledYData = function(yData){
    if (Math.max(...yData) > 10000) {
        scaledYData = yData.map( function(x) { return x/1000 } )
        return ['Number of Jobs, 1000s', scaledYData]
    } else {
        return ['Number of Jubs', yData]
    }
}

class PlotDataHolder {
    constructor(xData, 
                yData,
                occupationName,
                locationName,
                selector) {
        this.xData = xData;
        this.yData = yData;
        this.occupationName = occupationName;
        this.locationName = locationName;
        this.selector = selector;
    }
}


function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
        window.onload = func;
    } else {
        window.onload = function () {
            if (oldonload) {
                oldonload();
            }
            func();
        }
    }
}

