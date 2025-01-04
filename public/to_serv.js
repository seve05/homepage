function sendPicAlert(){
	let contents = document.getElementById("sent");
	contents.innerHTML = "Prompt was sent to server, please wait..";
}

function done_processing(){
	let contents = document.getElementById("sent");
	contents.innerHTML = "Processing done. You can view the Image now.";
	showImg();
	toggleSendB(1);
}

function toggleSendB(T){
	let contents = document.getElementById("submit_button");
	if (T === 1) {
		contents.style.display = "block";
	}
	else {
		contents.style.display = "none";
	}
}

function showImg(){
	let contents = document.getElementById("gendImg");
	contents.src = "http://localhost:3000/imageDownload"; 
}

function delImg(){
	let contents = document.getElementById("gendImg");
	contents.src = "";
}

document.getElementById('submit_button').addEventListener('click', function() {
	delImg();
	sendPicAlert();
	toggleSendB(0);
	let prompt_t= document.getElementById('prompt_text').value;
	let inference = document.getElementById('inference_s').value;
	let seed = document.getElementById('man_seed').value;
	console.log(prompt_t,inference,seed);
	const data_to_send = {
		"prompt":prompt_t,			
		"inference":inference,
		"seed":seed
	}; // ein JS object
	const jsonStringData = JSON.stringify(data_to_send);
	console.log(jsonStringData);
	console.log(typeof(jsonStringData));
	// XMLHttpRequest is an API in the form of a js object with
	// methods to transmit HTTP requests to a server from browser
	const xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:3000",true); //true for async processing
	xhr.setRequestHeader("Content-Type","application/json");
	xhr.onload = function(){    // .onload gets executed after the send method is complete !
		if(xhr.status >=200 && xhr.status <300){
			done_processing();
		}else{
			console.error("Request failed. Status:" +xhr.status);
		}
	};
	xhr.send(jsonStringData);
	
});

var random = Math.random()
