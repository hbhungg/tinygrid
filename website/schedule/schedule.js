
  var XMLHttpRequest = require('xhr2');
  var request = new XMLHttpRequest();
  request.open('GET','https://raw.githubusercontent.com/hbhungg/tinygrid/main/website/schedule/schedule_small.txt',true);
  request.send(null);
  request.onreadystatechange = get_data
  function get_data(){
  var schedule = request.responseText
  const schedule_array = schedule.split(/\n/);
  var csv_array = []

  var no_buildings = schedule_array[1];
  for (var i = 0; i < schedule_array.length; i++) {
   var row = schedule_array[i];
   var row_arr = row.split(/ /)
   if (row_arr[0] == "r"){
      
      var num_rooms = parseInt(row_arr[3]);
      
      for (var j = 0; j < num_rooms;j++){
        var building_no = row_arr[4+j].charAt(0);
        var new_row = {activity_type:row_arr[0],
                       activity_id:row_arr[1],
                       time:row_arr[2],
                       building_id:building_no};
        csv_array.push(new_row)
    
        
      }}
    
}
  console.log(csv_array)
  
  return request.responseText;}







