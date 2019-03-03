$(function(){
    // Get Product Data
    var url_productlikes = "http://127.0.0.1:5000/GetProductLikes"
        $.ajax({
            url: url_productlikes, 
            method:"GET",
            type:"application/json",
            success: function(result){
                // format
                var names = [];
                var types = [];
                var amounts = [];
                var objects = [];                
                var data = JSON.parse(result)
               
                $.each(data, function(key , v){
                   names.push(v.name);
                   types.push(v.type);
                   amounts.push(v.amount);
                });

                $.each(data, function(key , v){
                    objects.push([v.name , v.amount])
                 });
                 console.log(types);
                
                // Generate Chart
                var myChart = Highcharts.chart('container', {
                    chart:{
                        type:'column'
                    },
                    title:{
                        text:'Product Likes'
                    },
                    xAxis:{
                        categories:[],
                        title: {
                            text: null
                        }
                    },
                    yAxis:{
                        title:{
                            text:'Number Of likes'
                        }
                    },
                    legend: {
                        enabled: false
                    },
                    plotOptions: {
                        series: {
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true
                            }
                        }
                    },
                    series:[
                        
                    //     (function (){
                    //     // generate an array of random data
                    //     var res = [];
                        
                    //     $.each(data , function(k , v){
                    //         res.push({
                    //             name: v.name ,
                    //             data : [v.amount ]
                                
                    //         });
                    //     });console.log(res); 
                    //     return res;
                    // }())
                
                ],
                drilldown:{
                    series:[{
                        name: 'Brands',
                        colorByPoint: true,
                    }]
                }
                     
                    
                }
                
            );

            $.each(data, function(key , v){
                myChart.addSeries({
                    data:[{
                        name: v.name , // some id 
                        y : v.amount ,
                        drilldown: v.name
                    }]

                });
             });
            //  $.each(data , function(key , v){
                
            //     var drilldown = ({
            //         name: v.name,
            //         id: v.name,
            //         data: [ v.amount]   

            //     });
            //     myChart.options.drilldown.series = [drilldown];
            //  });
     
            myChart.xAxis[0].setCategories(types);


            },
            error: function(){
                alert('failed');
            }
        });

    // Get Order Data
    var url_orderdata = "http://127.0.0.1:5000/GetOrderData"
    $.ajax({
        url: url_orderdata, 
        method:"GET",
        type:"application/json",
        success: function(result){
            // format

            var data = JSON.parse(result);
            var objects = [];
            var drilldown = [];
  

            // Top Layer Data
            $.each(data, function(key , v){
                /*
                    Month:
                    Month_Total:
                    Orders = [Order_data]
                */
                objects.push({ 
                    name: v.month,
                    y: v.month_total,
                    drilldown: v.month   

                });
             });

            //  Drill Down Data
            // Name , ID & Data
            $.each(data, function(key , v){
                var order_data = [];
                $.each(v.orders , function(i ,j){
                   
                    order_data.push(
                         [ j.order_date , j.order_total]
                    );
                })
                drilldown.push({ 
                    name: v.month,
                    id: v.month,
                    data: order_data
                   
                
                   
                });
             }); 
             console.log(drilldown);
        
             var chart = Highcharts.chart('orderdata', {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
                },
                title: {
                    text: 'Order Data For 2017'
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                        }
                    }
                },
                series:[{
                    name: "Order Total ",
                    colorByPoint: true,
                    data:objects
                }],
                
              drilldown:{
                    series:[{
                        name: 'Order History',
                        colorByPoint: true,
                       
                    }]
                }
            });
            
            // $.each(data , function(key , v){
            //     console.log(v.orders[key].order_date +": "+ v.orders[key].order_total );
                
            //      drill =  ({
            //         name: v.month,
            //         id: v.month,
            //         data: [ {
            //             name: v.orders[key].order_date  ,
            //             y:  v.orders[key].order_total
            //         }]

            //     });
            chart.options.drilldown.series = drilldown;



        },
        error: function(){
            alert('failed');
        }
    });


});