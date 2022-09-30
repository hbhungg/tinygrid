/*
param: button_num - An integer value associated with elements.
html associations:
id, id, id, id, button_num
left_heading_1, left_text_1, content_1, content_1_sup, 1
left_heading_2, left_text_2, content_2, content_2_sup, 2
left_heading_3, left_text_3, content_3, content_3_sup, 3
left_heading_4, left_text_4, content_4, content_4_sup, 4
left_heading_5, left_text_5, content_5, content_5_sup, 5
*/

// Globals
var current_left_btn_selected = 1;

/**
 * Hides text of current button, reverts css of current button to default, 
 * changes text and heading of button_num to selected.
 * @param {int} button_num - *Refer to the top of this file*
 * @return {null}
 */
function left_btn_selected_helper(button_num) {
  // Check to do nothing
  if (button_num == current_left_btn_selected) {
    return;
  }
  // Get all required elements in the document by id
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

/**
 * Scrolls user to button_num's associated element height.
 * @param {int} button_num - *Refer to the top of this file*
 * @return {null}
 */
function left_btn_selected(button_num) {
  // Get content_(button_num)_sup element
  content_id = "content_" + button_num.toString() + "_sup";
  el = document.getElementById(content_id);
  // Scroll to the selected element
  window.scrollTo({
    top: el.offsetTop,
    behavior: 'smooth'
  });
}

/**
 * Checks all content regions, based on user scroll height, and calls left_btn_selected_helper 
 * for user is in region bound.
 * @param {int} button_num - *Refer to the top of this file*
 * @return {null}
 */
function scroll_content_effect() {
  // List content ids
  var lst_ids = [1,2,3,4,5];
  // For each id get associated id region, each if user scroll height is in region, then if true call left_btn_selected_helper 
  for (let i=0; i<lst_ids.length; i++) {
    var el = document.getElementById("content_" + lst_ids[i].toString());
    if (window.scrollY < el.offsetTop + el.offsetHeight && window.scrollY > window.pageYOffset + el.getBoundingClientRect().top) {
      left_btn_selected_helper(lst_ids[i]);
    }
  };

}

// Window event listeners
window.addEventListener("scroll", function() {scroll_content_effect();}, {passive: true});