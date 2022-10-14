const fetch = require('node-fetch')
const math = require('mathjs')

function parse_schedule(schedule,instance,day_num){
  var num_batteries = 2
  var charge_level = 420
  
  const schedule_array = schedule.split(/\n/);
  const instance_array = instance.split(/\n/);
  var csv_array = []
  var no_buildings = schedule_array[1];
  var k = 0 
  var load_list_rec = []
  var roomsize_list_rec = []
  var duration_list_rec = []
  var load_list_a = []
  var roomsize_list_a = []
  var duration_list_a = []

  for (var j = 0;j < instance_array.length; j++){
    var row = instance_array[j];
    var row_arr = row.split(/ /)
    if (row_arr[0] == "r"){
      load_list_rec.push(parseInt(row_arr[4]))
      roomsize_list_rec.push(row_arr[3])
      duration_list_rec.push(parseInt(row_arr[5]))}
      
    if (row_arr[0] == "a"){
      load_list_a.push(parseInt(row_arr[4]))
      roomsize_list_a.push(row_arr[3])
      duration_list_a.push(parseInt(row_arr[5]))}
  }
  
  
  

  
  

  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)

    if (row_arr[0] == "r"){
      for (var h = 0; h < 4;h++){
        var time_int = parseInt(row_arr[2]) + 672 * h
        var hours = math.floor((time_int % 96)/4) 
        var minutes = (time_int * 15) %60
        var days = math.floor(math.floor(time_int /4) /24)
        if (hours < 10){hours = "0" + hours}
        if (minutes == 0){minutes = "00"}
        var num_rooms = parseInt(row_arr[3]);
        for (var j = 0; j < num_rooms;j++){
          var building_no = row_arr[4+j].charAt(0);
          var new_row = {activity_type:"Recurring",
                         activity_id:row_arr[1],
                         time: "OCT " + days +" " +hours+ ":" + minutes,
                         timeofday:hours + ":" + minutes,
                         day:days,
                         time_val: time_int,
                         load: load_list_rec[row_arr[1]],
                         duration: duration_list_rec[row_arr[1]],
                         building_id:building_no};
                      
                      csv_array.push(new_row)}}}
                      
                      
      if (row_arr[0] == "a"){
        var time_int = parseInt(row_arr[2])
        var hours = math.floor((time_int % 96)/4) 
        var minutes = (time_int * 15) %60
        var days = math.floor(math.floor(time_int /4) /24)
        if (hours < 10){hours = "0" + hours}
        if (minutes == 0){minutes = "00"}
        var num_rooms = parseInt(row_arr[3]);
        for (var j = 0; j < num_rooms;j++){
          var building_no = row_arr[4+j].charAt(0);
          var new_row = {activity_type:"Once-off",
                         activity_id:row_arr[1],
                         time: "OCT " + days +" " +hours+ ":" + minutes,
                         timeofday:hours + ":" + minutes,
                         time_val: time_int,
                         day:days,
                         load: load_list_rec[row_arr[1]],
                         duration: duration_list_rec[row_arr[1]],
                         building_id:building_no};
                      
                      csv_array.push(new_row)}}
    
    
    
    
    
    
    if (row_arr[0] == "c"){

      
      if(row_arr[3] == 0){var charge_level = charge_level + 15}
      if(row_arr[3] == 2){var charge_level = charge_level - 15}
      var time_int = parseInt(row_arr[2])
      var hours = math.floor((time_int % 96)/4) 
      var minutes = (time_int * 15) %60
      var days = math.floor(math.floor(time_int /4) /24)
      if (hours < 10){hours = "0" + hours}
      if (minutes == 0){minutes = "00"}
      
      var new_row = {activity_type: "Charge",
                     time: "OCT " + days +" " +hours+ ":" + minutes,
                     timeofday: hours + ":" + minutes,
                     day: days,
                     time_val: time_int,
                     battery_id:row_arr[1],
                     charge_dec: row_arr[3],
                     battery_level: charge_level
  
                     }

      csv_array.push(new_row)}
      
      


  }
          
   
        return(csv_array)};



function fetch_schedule(){
  
  fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/test_schedule.txt')
  .then((response) => response.text())
  .then((data) => {
  fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/phase1_instance_small_0.txt')
    .then((response) => response.text())
  .then((data2) => { var schedule_array = parse_schedule(data,data2,7);
    battery_chart(schedule_array,7);
    
    
  })
  
})

}

  

function make_table(schedule_array){console.log(schedule_array)}


function battery_chart(schedule_array,day_num){
  var charge_array = []
  var day_num = 4
  var grid_load = 0

  var gridload_array = []
  
  for (let element in schedule_array){
    var entry = schedule_array[element]
    
     if(entry.day == day_num){
       
       if(entry.activity_type == "Recurring" || entry.activity_type == "Once-off"){
         console.log(entry)
         for (var i = 0; i < entry.duration;i++){
           var time_int = entry.time_val + i
           var hours = math.floor((time_int % 96)/4) 
           var minutes = (time_int * 15) %60
           var days = math.floor(math.floor(time_int /4) /24)
           if (hours < 10){hours = "0" + hours}
           if (minutes == 0){minutes = "00"}
           var gridload_row = {
             "time": hours + ":" + minutes,
             "load": entry.load}
          gridload_array.push(gridload_row)
         }}
         
       if(entry.activity_type == "Charge"){
         
         if(entry.charge_dec == 0){var grid_load = 19.36}
         if(entry.charge_dec == 0){var grid_load = -11.62}
         var gridload_row = {
           "time": entry.timeofday,
           "load": math.floor(grid_load,2)}
         var charge_row = {
           "time": entry.timeofday,
           "charge_level": entry.battery_level};
          
        gridload_array.push(gridload_row);
        charge_array.push(charge_row)}
       
       
     }}
      
      


  
  }


fetch_schedule()

