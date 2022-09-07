// Globals
var current_left_btn_selected = 1;

function left_btn_selected(button_num) {
  // Check to do nothing
  if (button_num == current_left_btn_selected) {
    return;
  }
  var button_selected_id = document.getElementById("left_heading_" + button_num.toString());
  var button_current_id = document.getElementById("left_heading_" + current_left_btn_selected.toString());

  var button_selected_text_id = document.getElementById("left_text_" + button_num.toString());
  var button_current_text_id = document.getElementById("left_text_" + current_left_btn_selected.toString());

  // Send viewport to element height
  var content_selected_id = document.getElementById("content_" + button_num.toString());
  window.scrollTo({
    top: window.pageYOffset + content_selected_id.getBoundingClientRect().top,
    behavior: 'smooth'
  });

  // Reveal button_selected_text_id element
  button_selected_text_id.classList.remove("hidden");
  // Hide button_current_text_id element
  button_current_text_id.classList.add("hidden");

  // Add selected class to button_selected_id element
  button_selected_id.classList.add("selected");
  // Removed selected class from button_current_id element
  button_current_id.classList.remove("selected");

  // Set current selection as buttom_num
  current_left_btn_selected = button_num;
}


window.addEventListener("scroll", function() {
  const content_ids = ["content_1", "content_2", "content_3", "content_4", "content_5"];
  // For each content_id in content_ids 
  for (let i = 0; i < content_ids.length; i++) {
    var el = document.getElementById(content_ids[i]);
    if (window.scrollY > (el.offsetTop + el.offsetHeight)) {

    }
  }
});


window.addEventListener("load", function() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});