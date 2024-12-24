var hello = "hello world";
alert(hello);
// function keywork declares the function
// myFunction(); calls it
function getGot(){
	console.log("aaaaaooooiii");
}
function Addition(a,b){
	return a+b;
}
// since we used return above we can now assign this function to variables 


getGot();
var someSome = Addition(5,9);

for(let i = 0; i<4;i++){
	alert(i);
}

// 'let' is a re-assignable variable in Javascript, meaning it can change state without programmers intervention

var n = Math.random();
console.log(n);
var guestlist = ['jack','michael','mick'];
console.log(guestlist[0]);
//Arrays in JS
//
// JSON = JavaScript Object Notation is an open standard file format and data-interchange
// format that uses human-readable text to store an dtransmit data objects consisting
// of name-value-pairs and arrays (or other serialized values). It is a commonly used data
// format with diverse uses in electronic data interchange, including that of 
// web applications with servers.
//
// serialization: is the process of translating a data structure or object state into
// a format that can be stored(file) in a secondary storage device (aka local storage)
// like ram.
//
if (guestlist.includes('jack')===true){
	console.log('okey it includes');
}
// Object.includes(looks for) is a method that traverses the array and returns 
// true if it find the data in the array.
//

