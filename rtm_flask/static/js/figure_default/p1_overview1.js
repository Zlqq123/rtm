
var theme='essos';

var myChart= echarts.init(document.getElementById('r2'),theme);
var option ={
        title:[
             {text: 'Lavida BEV',left: '16.67%',textAlign: 'center'},
             {text: 'Passat PHEV',left: '50%',textAlign: 'center'},
             {text: 'Tiguan L PHEV',left: '83.33%',textAlign: 'center' },
                ],
        legend: { type: 'scroll',orient: 'vertical',right: 5,top: 20,
                data: ['Private', 'Taxi','Fleet']  },
        tooltip: {trigger: 'item'},
        toolbox: {show: true,orient : 'vertical',left: '95%',top: '75%',
                feature : { mark : {show: true},
                        restore : {show: true, title:'重置'},
                        saveAsImage : {show: true, title:'保存为图片图'}}
                        },
        series:[{type:'pie',radius: '60%',center: ['16.67%', '50%'],
                data:[{value: 2438, name: 'Private'},
                        {value: 291, name: 'Taxi'},
                        {value: 4053, name: 'Fleet'}],
                animation: false,
                label: {position: 'outer',alignTo: 'none',bleedMargin: 5},
                left: 0,
                right: '66.6667%',
                top: 0,
                bottom: 0
                },
                {type:'pie',radius: '60%',center: ['50%', '50%'],
                data:[{value: 18856, name: 'Private'},
                        {value: 3519, name: 'Fleet'},],
                animation: false,
                label: {position: 'outer',alignTo: 'none',bleedMargin: 5},
                left: '33.3333%',
                right: '33.3333%',
                top: 0,
                bottom: 0
                },
                {type:'pie',radius: '60%',center: ['80%', '50%'],
                data:[{value: 13760, name: 'Private'}],
                animation: false,
                label: {position: 'outer',alignTo: 'none',bleedMargin: 5},
                left: '66.6667%',
                right: 0,
                top: 0,
                bottom: 0
                }
                ]
        };
myChart.setOption(option);


var myChart6 = echarts.init(document.getElementById('p1_f6'),theme);
var option6 ={
        legend: { right:"10%",top: '10%',orient: 'vertical',
                        data: ['Fleet', 'Private', 'Taxi']
                },
        title:{ text: 'lavida 不同用户类型地理位置分布',x:'center', y: 'top'},
        toolbox: { show: true,
                        feature: {magicType: {show:true,
                                        title:{line:'切换为折线图',bar:'切换为柱状图'},
                                        type: ['line', 'bar']},
                                        saveAsImage: {show:true, title:'保存为图片图'}
                                        }
                },
        xAxis: [{ type: 'category',axisTick:{show:true},
                        data: ['东北', '华北', '华东', '华中', "华南",'西北','西南']
                }],
        yAxis: [{type: 'value',min: 0,name:"车辆数目",
                axisTick:{show:true},
                axisLine:{show:true},
                splitLine:{show:false},
                }],
        tooltip: {trigger: 'axis',
                        axisPointer: { type: 'shadow' }// 坐标轴指示器，坐标轴触发有效// 默认为直线，可选为：'line' | 'shadow'
                        },
        series: [{  name: 'Fleet',type: 'bar',
                        itemStyle:{normal:{barBorderRadius:5}},
                        label: {normal: {show: true,position: 'top'}},
                        data: [1,218,3512,159,67,62,34]  }, 
                        { name: 'Private',type: 'bar',barGap: 0,
                        itemStyle:{normal:{barBorderRadius:5}},
                        label: {normal: {show: true,position: 'top'}},
                        data: [0,701,903,212,355,48,219]  }, 
                        { name: 'Taxi', type: 'bar',
                        itemStyle:{ normal:{ barBorderRadius:5 } },
                        label: {  normal: { show: true, position: 'top' } },
                        data: [0,110,175,1,0,0,5] }
                ]
        }
myChart6.setOption(option6);