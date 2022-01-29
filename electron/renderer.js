// preload.js

// All of the Node.js APIs are available in the preload process.
// It has the same sandbox as a Chrome extension.
let value = 0;


function start_code_function()
{
	fetch(`http://127.0.0.1:5001/check`).then((data)=>{      
		return data.text();
		
	}).then((text)=>{
	  console.log("data: ", text);
		value = text;
	}).catch(e=>{
	  console.log(e);
	})
	document.getElementById("test").innerHTML = `${value}`;

	setTimeout(start_code_function, 1000);
}

function attention_check()
{
	// document.getElementById("status").innerHTML = "running";
	fetch(`http://127.0.0.1:5001/atten`).then((data)=>{      
		return data.text();
		
	}).then((text)=>{
	  console.log("data: ", text);
		value = text;
	}).catch(e=>{
	  console.log(e);
	})
	document.getElementById("status").innerHTML = `${value}`;
	if(value == "True")
		return;
	setTimeout(attention_check, 1000);
}

function toggle_button_label()
{
	if(document.getElementById("start_button").innerHTML == "START")
		document.getElementById("start_button").innerHTML = "STOP";
	else
		document.getElementById("start_button").innerHTML = "START";
}

function start_attention_check()
{
	toggle_button_label();
	document.getElementById("status").innerHTML = "starting";
	fetch(`http://127.0.0.1:5001/stop`, {method: "POST"});
	attention_check();
	// setTimeout(start_attention_check, 1000);
}

window.addEventListener('DOMContentLoaded', () => {
	const replaceText = (selector, text) => {
	  const element = document.getElementById(selector)
	  if (element) element.innerText = text
	}
  
	for (const dependency of ['chrome', 'node', 'electron']) {
	  replaceText(`${dependency}-version`, process.versions[dependency])
	}

	start_code_function();
	document.getElementById("start_button").addEventListener("click", start_attention_check);
  })