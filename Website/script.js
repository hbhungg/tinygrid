// Globals
var current_left_btn_selected = 1;

function left_btn_selected_helper(button_num) {
  // Check to do nothing
  if (button_num == current_left_btn_selected) {
    return;
  }
  var button_selected_id = document.getElementById("left_heading_" + button_num.toString());
  var button_current_id = document.getElementById("left_heading_" + current_left_btn_selected.toString());

  var button_selected_text_id = document.getElementById("left_text_" + button_num.toString());
  var button_current_text_id = document.getElementById("left_text_" + current_left_btn_selected.toString());

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

function left_btn_selected(button_num) {
  // Check to do nothing
  if (button_num == current_left_btn_selected) {
    return;
  }
  // Send viewport to element height
  var content_selected = document.getElementById("content_" + button_num.toString());
  window.scrollTo({
    top: window.pageYOffset + content_selected.getBoundingClientRect().top,
    behavior: 'smooth'
  });
  left_btn_selected_helper(button_num);
}

/*
window.addEventListener("scroll", function() {
  const current_element = document.getElementById("content_" + current_left_btn_selected.toString());
  const above_element = document.getElementById("content_" + (current_left_btn_selected - 1).toString());
  const bellow_element = document.getElementById("content_" + (current_left_btn_selected + 1).toString());
  
  if (bellow_element != null) {
    if (window.scrollY > (bellow_element.offsetTop + bellow_element.offsetHeight - bellow_element.clientHeight) && window.scrollY > (current_element.offsetTop + current_element.offsetHeight)) {
      left_btn_selected_helper(current_left_btn_selected + 1);
    }
  }
  if (above_element != null) {
    if (window.scrollY < (above_element.offsetTop + above_element.offsetHeight - above_element.clientHeight) && window.scrollY < (current_element.offsetTop + current_element.offsetHeight)) {
      left_btn_selected_helper(current_left_btn_selected - 1);
    }
  }
});
*/

window.addEventListener("load", function() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});