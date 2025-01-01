/* var x = document.getElementById("mic");   this selects the elemtn with the id mic which is my h2*/ 


/*.innerHTML="Heyy";changes the contents between the p tags in this case also tags etc*/
/* .textContent = "something" changes the text in the element as well as in every element*/
/* .innerText = "something" changes the text but only human readable text*/

/*------Query Selectors----(inquiring a selector)-*/
/*.querySelector('#myID'oder '.myClass') kann auch element aussuchen also 'h1' 'p'kann man benutzen wenn man nach spezifischem Element an Hand von * Css Selektor suchen moechte. Nimmt nur das ERSTE matching Element 
 * ->  to get a specific element you can .querySelector("li a") um z.B. das erste anchor element in einer untergeordneten 
 * Liste zu bekommen
 * oder .querySelector("#some_list a") um ein untergeordnetes anchor Element zu nehmen
 *
 *
 *.querySelectorAll('.myClass'oder'#myId') nimmt ALLE matching Elemente an Hand von CSSSelektorName
 * Diese oberen beiden werden genutzt wenn performance nicht wichtig ist.
 *
 * -------Select by ID---------
 * .getElementById('myId') (siehe oben) ist schnellster querySelector um  element mit spez ID zu 
 * bekommen. Ist gut um SPEZIFISCHES ELEMENT an Hand von ID zu finden
 * IDs sollten nur einmal vergeben werden daher ist getElementbyID() singular
 * /

/*----Multiple Elements--(selecting an entire ELement)---*/
/*.getElementsByTagName('p') kann man benutzen um eine HTMLCollection der tags mit p zu bekommen
 *.getElementsByClassName('classname') nimmt alle mit dem selben classname als HTMLCollection
 *---------------------------------------------------------------------/
/*Bsp.: document.getElementsByTagName("p")[1].style.width = "50%";
 * hier fetchen wir alle Elemente mit "p" tag und waehlen das 2. Element aus dem array aus um 
 * das Style Element "width" zu 50% zu aendern.
 *Bsp.: document.getElementsByTagName("p").length;  returns the length of the array(n of elemnts)
 * 	- the .length property is part of the HTML DOM
 * /


/* <tag> Content </closing_tag> }the entire thing is called an HTML ELEMENT */
/* everything inside the tag is an attribute like id="" or href="https...." or src="/FOLDER/FILE"
 * document.querySelector("a").getAttribute("href","https://www.bing.com"/); 
 * will return the href of the document using the JS+ DOM and change it to the specified value as 2nd arg
 * */

/*---------Prompt---generation--Functions----*/
/* hat onclick als attribut in dem form_field, also on click macht es die function sendFunction()*/


function sendPicAlert(){
	alert("Prompt was sent to server, please wait for the image to generate.");
}

// function embedded in the argument of addEventListener()
document.getElementById('submit_button').addEventListener('click', function() {
	sendPicAlert()
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
	// gets turned into Json string bc its 0s and 1s which can be sent over the web
	// json is used to send 0s and 1s over the web, it highly compatible across world
	alert(jsonStringData);
	// XMLHttpRequest is an API in the form of a js object with
	// methods to transmit HTTP requests to a server from browser
	const xhr = new XMLHttpRequest();
	xhr.open("POST", "localhost:3000",true); //true for async processing
	xhr.setRequestHeader("Content-Type","iapplication/json");
	xhr.onload = function(){
		if(xhr.status >=200 && shr.status <300){
			console.log("success, no error",xhr.responseText);
		}else{
			console.error("Request failed. Status:" +xhr.status);
		}
	};
	xhr.send(jsonStringData);

});

var random = Math.random()

// HIER FEHLT NOCH DIE SERVERKOMPONENTE, IN EXPRESS.JS, DANN AUF SERVER JSON PARSING
// DANN WIEDER STRINGIFY ? ZURUECKSENDEN AUF WEBPAGE DECODING UND IMAGE ANZEIGEN
// DIRECT IMAGE SERVING: THE SERVER CAN GENERATE THE IMAGE AND SEND 
// IT BACK DIRECTLY AS A RESOPNSE TO THIS HTTP REQUEST.
// ENABLE SERVER SIDE COMPRESSION LIKE GZIP TO REDUZE THE IMAGE FILE
//

