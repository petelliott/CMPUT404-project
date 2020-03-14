/*
 * The function below will validate the content:
 *
 * If current content type is plain text/Markdown, 
 * content cannot be empty.
 * If current content type is image, 
 * image cannot be empty.
*/ 
function validateForm() {
	if (document.getElementById('id_content_type').selectedIndex==0 || document.getElementById('id_content_type').selectedIndex==1){
		var required_field = "content";
		var x = document.forms['p'][required_field].value;
	}
	else{
		var required_field = "image";
		var x = document.forms['p'][required_field].value;
	}
	if (x == "") {
		alert(required_field + " must be filled out");
		return false;
	}
}

/*
 * The function below will hide unnecessary component:
 *
 * hide image field and display content field when we choose to use markdown/plaintext
 * and hide content and display image field when we use image
*/ 
function autohide(){
	console.log(document.getElementById('id_content_type').selectedIndex)
	if (document.getElementById('id_content_type').selectedIndex==0 || document.getElementById('id_content_type').selectedIndex==1){
		//hide image field and display content field 
		document.getElementById('id_content').parentNode.style.display='';
		document.getElementById('id_image').parentNode.style.display='none';
		document.forms['p']['image'].value = ''

	} else {
		// hide content and display image field
		document.getElementById('id_content').parentNode.style.display='none';
		document.getElementById('id_image').parentNode.style.display='';
		document.forms['p']['content'].value = ''
	}
}
document.getElementById('id_content_type').selectedIndex=0
console.log(document.getElementById('id_content_type').selectedIndex);
autohide();
document.getElementById('id_content_type').onchange = autohide;