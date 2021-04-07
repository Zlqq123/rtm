var theme='essos';

var data={
    charging_times:[
        {name: "Lavida BEV 53Ah", value: 20},
        {name: "Tiguan L PHEV", value: 10},
        {name: "Passat L PHEV", value: 9.5}
    ],
    charge_mode:{
        lavida: [
            {name: "模式二",value:11.45},
            {name: "模式三(3.6kW)",value:10.80},
            {name: "模式三(7.2kW)",value:38.30},
            {name: "直流充电",value:39.45},
        ],
        tiguan: [
            {name: "模式二",value:26.65},
            {name: "模式三(3.6kW)",value:73.35}
        ],
        passat: [
            {name: "模式二",value:21.61},
            {name: "模式三(3.6kW)",value:78.39}
        ]
    }
};

var myChart1 = echarts.init(document.getElementById('char_overview_f1'),theme);
var option1 = {
        title: {text:'平均每月每辆车充电次数', left: '50%', textAlign: 'center'},
        grid:{x:"5%",y:'15%',x2:"5%",y2:'5%',containLabel: true},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: {type: 'value',min: 0, interval: 2,},
        yAxis: { type: 'category', data: ['Lavida BEV 53Ah', "Tiguan L PHEV","Passat L PHEV"]},
        series:{type: 'bar', barWidth : 20, data:[20,10,9.5]}
};
myChart1.setOption(option1);

var myChart2 = echarts.init(document.getElementById('char_overview_f2'),theme);
var option2 ={
    title:[
         {text: 'Lavida BEV',left: '16.67%',textAlign: 'center'},
         {text: 'Tiguan L PHEV',left: '50%',textAlign: 'center'},
         {text: 'Passat PHEV',left: '83.33%',textAlign: 'center' },
            ],
  //  legend: { type: 'scroll',orient: 'vertical',right: 5,top: 20,
  //          data: ["模式二", "模式三(3.6kW)","模式三(7.2kW)","直流充电"]  },
    tooltip: {trigger: 'item'},
    toolbox: {show: true,orient : 'vertical',left: '95%',top: '75%',
            feature : { mark : {show: true},
                    restore : {show: true, title:'重置'},
                    saveAsImage : {show: true, title:'保存为图片图'}}
                    },
    series:[{type:'pie',radius: '50%',center: ['16.67%', '50%'],
            data:data.charge_mode.lavida,
            animation: false,
            label: {position: 'outer',alignTo: 'none',bleedMargin: 5},
            left: 0,
            right: '66.6667%',
            top: 0,
            bottom: 0
            },
            {type:'pie',radius: '50%',center: ['50%', '50%'],
            data:data.charge_mode.tiguan,
            animation: false,
            label: {position: 'outer',alignTo: 'none',bleedMargin: 5},
            left: '33.3333%',
            right: '33.3333%',
            top: 0,
            bottom: 0
            },
            {type:'pie',radius: '50%',center: ['80%', '50%'],
            data:data.charge_mode.passat,
            animation: false,
            label: {position: 'outer',alignTo: 'none',bleedMargin: 5},
            left: '66.6667%',
            right: 0,
            top: 0,
            bottom: 0
            }
            ]
    };
myChart2.setOption(option2);