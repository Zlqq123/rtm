var theme='essos';


var myChart1 = echarts.init(document.getElementById('s2_r1_1'),theme);
//异步调用，lavida车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
     myChart1.setOption({
           title : {text: 'lavida BEV 53Ah 分布',left: 'center'},
           tooltip : {trigger: 'item'},
           visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
           toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                     feature : { mark : {show: true},
                                 dataView : {show: true, readOnly: false, title:'查看数据'},
                                 restore : {show: true, title:'重置'},
                                 saveAsImage : {show: true, title:'保存为图片图'}}
                       },
           series : [{name: 'lavida',type: 'map',mapType: 'china',roam: false,
               label: {normal: {show: false},emphasis: {show: true}},
               data:data.Lavida}]
     })
  },'json');

var myChart2 = echarts.init(document.getElementById('s2_r1_2'),theme);
//异步调用，tiguan车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
myChart2.setOption({
        title : {text: 'Tiguan L PHEV 分布',left: 'center'},
        tooltip : {trigger: 'item'},
        visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
        toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                feature : { mark : {show: true},
                                dataView : {show: true, readOnly: false, title:'查看数据'},
                                restore : {show: true, title:'重置'},
                                saveAsImage : {show: true, title:'保存为图片图'}}
                        },
        series : [{name: 'Tiguan',type: 'map',mapType: 'china',roam: false,
                label: {normal: {show:false},emphasis: {show: true}},
                data:data.Tiguan}]
        })
        },'json');

var myChart3 = echarts.init(document.getElementById('s2_r1_3'),theme);
//异步调用，passat车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
        myChart3.setOption({
                title : {text: 'Passat PHEV 分布',left: 'center'},
                tooltip : {trigger: 'item'},
                visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
                toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                        feature : { mark : {show: true},
                                        dataView : {show: true, readOnly: false, title:'查看数据'},
                                        restore : {show: true, title:'重置'},
                                        saveAsImage : {show: true, title:'保存为图片图'}}
                                },
                series : [{name: 'passat',type: 'map',mapType: 'china',roam: false,
                        label: {normal: {show: false},emphasis: {show: true}},
                        data:data.Passat}]
                })
        },'json');




