const fetch = require('node-fetch')
const math = require('mathjs')

function parse_schedule(schedule,day_num){
  var min_step = (day_num) * 24 * 4
  var max_step = (day_num+1) *24 *4
  var num_batteries = 2
  var charge_arr = []
  for (var i = 0; i < num_batteries;++i){charge_arr.push(100)}
  var schedule = schedule
  const schedule_array = schedule.split(/\n/);
  var csv_array = []
  var no_buildings = schedule_array[1];
  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    var hours = math.floor((row_arr[2] % 96)/4) 
    var minutes = (row_arr[2] * 15) %60
    var days = math.floor(math.floor(row_arr[2] /4) /24)
    if (row_arr[0] == "r"){var num_rooms = parseInt(row_arr[3]);
      for (var j = 0; j < num_rooms;j++){
        var building_no = row_arr[4+j].charAt(0);


        var new_row = {activity_type:row_arr[0],
                      activity_id:row_arr[1],
                      time: "OCT" + days +" " +(hours)+ ":" + minutes,
                      day:days,
                      building_id:building_no};
                      
                      csv_array.push(new_row)}}
    
    if (row_arr[0] == "c"){
      if(row_arr[3] == 0){charge_arr[row_arr[1]] = charge_arr[row_arr[1]]- 10}
      if(row_arr[3] == 2){charge_arr[row_arr[1]] = charge_arr[row_arr[1]]+ 10}
      
      var new_row = {activity_type: "Charge",
                     time: "OCT" + days +" " +(hours)+ ":" + minutes,
                     day: days,
                     battery_id:row_arr[1],
                     charge_dec: row_arr[3],
                     battery_level: charge_arr[row_arr[1]]
                     }      
      csv_array.push(new_row)
    }
    
  }
          
          
        return(csv_array)};



function fetch_schedule(){
  
  fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/test_schedule.txt')
  .then((response) => response.text())
  .then((data) => {var schedule_array = parse_schedule(data,7);
  make_table(schedule_array);
  })
  
}
  
  
  
function make_table(schedule_array){console.log(schedule_array)}


fetch_schedule()
