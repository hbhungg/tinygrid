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
  /*
  var content_selected = document.getElementById("content_" + button_num.toString());
  // Send viewport to element height
  window.scrollTo({top: window.pageYOffset + content_selected.getBoundingClientRect().top});

  // Change left button style
  left_btn_selected_helper(button_num);
  */
}

function scroll_content_effect() {
  var lst_ids = [1,2,3,4,5];
  for (let i=0; i<lst_ids.length; i++) {
    var el = document.getElementById("content_" + lst_ids[i].toString());
    if (window.scrollY <= el.offsetTop + el.offsetHeight && window.scrollY >= window.pageYOffset + el.getBoundingClientRect().top) {
      left_btn_selected_helper(lst_ids[i]);
    }
  };

}

// Window event listeners
window.addEventListener("scroll", function() {scroll_content_effect();}, {passive: true});
window.addEventListener("load", function() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});

