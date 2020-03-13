var form = document.getElementById("editProfileForm");
var editButton = document.getElementById("editProfileButton");
var closeButton = document.getElementsByClassName("close")[0];

// Display the Edit Profile Form
editButton.onclick = function() {
  form.style.display = "block";
}

// Close the form if user clicks on the close button
closeButton.onclick = function() {
  form.style.display = "none";
}

// Clicking outside the form closes it
window.onmousedown = function(event) {
  if (event.target == form) {
    form.style.display = "none";
  }
}