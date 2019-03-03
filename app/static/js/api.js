/* Code for Stock API HERE
var base_url = "http://api.ft.com/content/search/v1";
var apikey = "vzh9x9aru297jvgw7x56mtrt";

function getData(){
    $.ajax({
        beforeSend: function (request)
        {
            request.setRequestHeader("Authorization", "No Auth");
            request.setRequestHeader("x-api-key", "vzh9x9aru297jvgw7x56mtrt");
        },
        headers: {
            "x-api-key": "vzh9x9aru297jvgw7x56mtrt",
            "content-type": "application/json",
            "cache-control": "no-cache",
          },
        url: base_url, 
        method:"POST",
        type:"application/json",
        data: { queryString: "John" },
        success: function(result){
            alert(result)
        },
        error: function(){
            alert('failed');
        }
    });
}
*/

// function getData(){
//     var url = "https://newsapi.org/v1/articles?source=financial-times&sortBy=top&apiKey=6ee64fd295a44f738df66cc1838a73b3";
//     $.ajax({
//         url: url, 
//         method:"GET",
//         type:"application/json",
//         success: function(result){

//             $.each(result.articles, function(key , value){
//                 $("#news").append("<div class='col-md-3'><div class='card'><h3><a href='"+value['url']+"'  >"+value['title']+"</a></h3> <img src='"+value['urlToImage']+"'></img><div class='card-block'></div></div></div>")
//             });
//         },
//         error: function(){
//             alert('failed');
//         }
//     });
// }


$(document).ready(function(){
    getData();


});


