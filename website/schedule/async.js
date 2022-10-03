
async function getUserDataWithPromise() {
  var xhr = new XMLHttpRequest();
  return new Promise(function(resolve, reject) {
   xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        if (xhr.status >= 300) {
          reject("Error, status code = " + xhr.status)
        } else {
                var schedule = xhr.responseText
                const schedule_array = schedule.split(/\n/);
                var csv_array = []
                var no_buildings = schedule_array[1];
                for (var i = 0; i < schedule_array.length; i++) {
                  var row = schedule_array[i];
                  var row_arr = row.split(/ /)
                  if (row_arr[0] == "r"){var num_rooms = parseInt(row_arr[3]);
                    for (var j = 0; j < num_rooms;j++){
                      var building_no = row_arr[4+j].charAt(0);
                      var hours = math.floor((row_arr[2] % 96)/4) 
                      var minutes = (row_arr[2] * 15) %60
                      var days = math.floor(math.floor(row_arr[2] /4) /7)
                      var new_row = {activity_type:row_arr[0],
                          activity_id:row_arr[1],
                          time: "OCT" + days +" " +(hours)+ ":" + minutes,                     
                          building_id:building_no};
                      csv_array.push(new_row)}}}
          
          
          
          resolve(csv_array);
        }
      }
    }
    xhr.open('GET','https://raw.githubusercontent.com/hbhungg/tinygrid/main/website/schedule/schedule_small.txt',true)
    
    
    xhr.send();
  });
}
async function show_table() {
  document.getElementById("demo").innerHTML = "code ran"
  try {
    let user = await getUserDataWithPromise()
    document.getElementById("demo").innerHTML = "code ran"

  } catch (err) {
    console.log(err)
  }
}
