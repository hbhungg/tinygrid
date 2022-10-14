const fetch = require('node-fetch')
const math = require('mathjs')



function dothis() {
async function fetchMoviesAndCategories() {
  const [moviesResponse, categoriesResponse] = await Promise.all([
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/test_schedule.txt'),
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/phase1_instance_small_0.txt')
  ]);
  const movies = await moviesResponse.text();
  const categories = await categoriesResponse.text();
  return [movies, categories];
}
fetchMoviesAndCategories().then(([movies, categories]) => {
        
        var csv_array = parse_schedule(movies,categories)
        console.log(csv_array)

        
        
        
       

}).catch(error => {
  // /movies or /categories request failed
});



function parse_schedule(schedule,instance,sl_val){
    var charge_level = 420
  
  const schedule_array = schedule.split(/\n/)
  const instance_array = instance.split(/\n/)
  
  var day_num = sl_val
  var grid_load = 0
  var gridload_array = []
  var charge_array = []
  var load_list_rec = []
  var duration_list_rec = []
  var load_list_a = []
  var duration_list_a = []
  
  //Initialise vaues from instance
  for (var j = 0;j < instance_array.length; j++){
    var row = instance_array[j];
    var row_arr = row.split(/ /)
    if (row_arr[0] == "r"){
      load_list_rec.push(parseInt(row_arr[4]))
      
      duration_list_rec.push(parseInt(row_arr[5]))}
      
    if (row_arr[0] == "a"){
      load_list_a.push(parseInt(row_arr[4]))
      
      duration_list_a.push(parseInt(row_arr[5]))}
  }
  

  
  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    var day = math.floor(math.floor(parseInt(row_arr[2])/4)/24);
      if((day == day_num ||day == day_num -1) && row_arr[0] == "c"){
         var time_int = parseInt(row_arr[2])
         var hours = math.floor((time_int % 96)/4) 
         var minutes = (time_int * 15) %60
         var day = math.floor(math.floor(time_int/4)/24)
         if (hours < 10){hours = "0" + hours}
         if (minutes == 0){minutes = "00"}
         
         if(row_arr[3] == 0){var grid_load = 19.36;
                             var charge_level = charge_level + 15}
         }
         if(row_arr[3] == 2){var grid_load = -11.62
                             var charge_level =charge_level - 15}

         var gridload_row = {
           "time": hours + ":" + minutes,
           "load": math.floor(grid_load,2)}
         var charge_row = {
           "time": hours + ":" + minutes,
           "charge_level": charge_level};
          
        if(day == day_num){gridload_array.push(gridload_row)} ;
        charge_array.push(charge_row)}
        

  arr = [{a: 'C', b: 4},
         {a: 'C', b: 7},
         {a: 'C', b: 4},
         {a: 'D', b: 1},
         {a: 'D', b: 2},
         {a: 'D', b: 6},
         {a: 'E', b: 8},
         {a: 'E', b: 4},
         {a: 'E', b: 7}]
          

  
  
     
  
  return(arr)}


 
function make_chart(schedule,instance,day_num){
  var charge_level = 420
  
  const schedule_array = schedule.split(/\n/)
  const instance_array = instance.split(/\n/)
  
  var day_num = 4
  var grid_load = 0
  var gridload_array = []
  var charge_array = []
  var load_list_rec = []
  var duration_list_rec = []
  var load_list_a = []
  var duration_list_a = []
  
  //Initialise vaues from instance
  for (var j = 0;j < instance_array.length; j++){
    var row = instance_array[j];
    var row_arr = row.split(/ /)
    if (row_arr[0] == "r"){
      load_list_rec.push(parseInt(row_arr[4]))
      
      duration_list_rec.push(parseInt(row_arr[5]))}
      
    if (row_arr[0] == "a"){
      load_list_a.push(parseInt(row_arr[4]))
      
      duration_list_a.push(parseInt(row_arr[5]))}
  }
  

  
  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    var day = math.floor(math.floor(parseInt(row_arr[2])/4)/24);
     
     
     
     
     if ((day == day_num ||day == day_num -1) && row_arr[0] == "r"){
       
       duration = duration_list_rec[row_arr[1]];
       for (var h = 0;h < 4;h++){
         for (var j = 0; j < parseInt(row_arr[3]);j++){
           for (var k = 0; k < duration;k++ ){
            var time_int = parseInt(row_arr[2]) + 672 * h + k
            var hours = math.floor((time_int % 96)/4) 
            var minutes = (time_int * 15) %60
            var day = math.floor(math.floor(time_int/4)/24)
            
            if (hours < 10){hours = "0" + hours}
            if (minutes == 0){minutes = "00"}
            var gridload_row = {
              "time": hours + ":" + minutes,
              "load":load_list_rec[row_arr[1]]
            }
            if(day == day_num){gridload_array.push(gridload_row)}             
            
         
       }}}}
       
       if((day == day_num ||day == day_num -1) && row_arr[0] == "a"){
       duration = duration_list_a[row_arr[1]];
       for (var j = 0; j < parseInt(row_arr[3]);j++){
         for (var k = 0; k < duration;k++){
           var time_int = parseInt(row_arr[2]) + k
           var hours = math.floor((time_int % 96)/4) 
           var minutes = (time_int * 15) %60
           var day = math.floor(math.floor(time_int/4)/24)
           if (hours < 10){hours = "0" + hours}
           
           if (minutes == 0){minutes = "00"}
           var gridload_row = {
             "time": hours + ":" + minutes,
             "load":load_list_rec[row_arr[1]]
            }
            if(day == day_num){gridload_array.push(gridload_row)} 
       }}}
       
       
       

         
       if((day == day_num ||day == day_num -1) && row_arr[0] == "c"){
         var time_int = parseInt(row_arr[2])
         var hours = math.floor((time_int % 96)/4) 
         var minutes = (time_int * 15) %60
         var day = math.floor(math.floor(time_int/4)/24)
         if (hours < 10){hours = "0" + hours}
         if (minutes == 0){minutes = "00"}
         
         if(row_arr[3] == 0){var grid_load = 19.36;
                             var charge_level = charge_level + 15
         }
         if(row_arr[3] == 2){var grid_load = -11.62
                             var charge_level =charge_level - 15}

         var gridload_row = {
           "time": hours + ":" + minutes,
           "load": math.floor(grid_load,2)}
         var charge_row = {
           "time": hours + ":" + minutes,
           "charge_level": charge_level};
          
        if(day == day_num){gridload_array.push(gridload_row)} ;
        charge_array.push(charge_row)}
        
  }
  

        
       
    
  console.log("dalkgjdfakg")  
     
  return(gridload_array.length)
  
  }
      
      



}

dothis()