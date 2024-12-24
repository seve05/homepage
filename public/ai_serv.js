/* var x = document.getElementById("mic");   this selects the elemtn with the id mic which is my h2*/ 
/*.innerHTML="Heyy";changes the contents between the p tags in this case*/


/*------Query Selectors----(inquiring a selector)-*/
/*.querySelector('#myID'oder '.myClass') kann man benutzen wenn man nach spezifischem Element an Hand von * Css Selektor suchen moechte. Nimmt nur das ERSTE matching Element 
 * 
 *.querySelectorAll('.myClass'oder'#myId') nimmt ALLE matching Elemente an Hand von CSSSelektorName
 * Diese oberen beiden werden genutzt wenn performance nicht wichtig ist.
 *
 * -------Select by ID---------
 * .getElementByID('myId') (siehe oben) ist schnellster querySelector um  element mit spez ID zu 
 * bekommen. Ist gut um SPEZIFISCHES ELEMENT an Hand von ID zu finden
 */

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


function sendFunction(){
var alert_sent= alert("Prompt was sent to server, please wait for the image to generate.");
}
/* hat onclick als attribut in dem form_field, also on click macht es die function sendFunction()*/
