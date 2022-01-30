// preload.js

const { stat } = require("original-fs");

// All of the Node.js APIs are available in the preload process.
// It has the same sandbox as a Chrome extension.
let value = 0;
let state = 0;

let stream = null,
	audio = null,
	mixedStream = null,
	chunks = [],
	recorder = null
startButton = null,
	stopButton = null,
	downloadButton = null,
	recordedVideo = null;

async function setupStream() {
	try {
		stream = await navigator.mediaDevices.getDisplayMedia({
			audio: true,
			video: true
		});

		audio = await navigator.mediaDevices.getUserMedia({
			audio: {
				echoCancellation: true,
				noiseSuppression: true,
				sampleRate: 44100,
			},
		});

		setupVideoFeedback();
	} catch (err) {
		console.error(err)
	}
}

function setupVideoFeedback() {
	if (stream) {
		const video = document.querySelector('.video-feedback');
		video.srcObject = stream;
		video.play();
	} else {
		console.warn('No stream available');
	}
}

async function startRecording() {
	// await setupStream();

	if (stream && audio) {
		mixedStream = new MediaStream([...stream.getTracks(), ...audio.getTracks()]);
		recorder = new MediaRecorder(mixedStream);
		recorder.ondataavailable = handleDataAvailable;
		recorder.onstop = handleStop;
		recorder.start(1000);

		startButton.disabled = true;
		stopButton.disabled = false;

		console.log('Recording started');
	} else {
		console.warn('No stream available.');
	}
}

function stopRecording() {
	recorder.stop();

	startButton.disabled = false;
	stopButton.disabled = true;
}

function handleDataAvailable(e) {
	chunks.push(e.data);
}

function handleStop(e) {
	const blob = new Blob(chunks, { 'type': 'video/mp4' });
	chunks = [];

	downloadButton.href = URL.createObjectURL(blob);
	downloadButton.download = 'video.mp4';
	downloadButton.disabled = false;

	recordedVideo.src = URL.createObjectURL(blob);
	recordedVideo.load();
	recordedVideo.onloadeddata = function () {
		const rc = document.querySelector(".recorded-video-wrap");
		rc.classList.remove("hidden");
		rc.scrollIntoView({ behavior: "smooth", block: "start" });

		recordedVideo.play();
	}

	stream.getTracks().forEach((track) => track.stop());
	audio.getTracks().forEach((track) => track.stop());

	console.log('Recording stopped');
}


// Now electron part

async function getSources()
{
	await setupStream();
}


function check_timeout_function()
{
	let notif_flag = "1";
	// let value = 0;
	fetch(`http://127.0.0.1:5001/check`).then((data)=>{      
		return data.text();
		
	}).then((text)=>{
	  	console.log("data: ", text);
		notif_flag = text;
		document.getElementById("test").innerHTML = `${text}`;
	}).catch(e=>{
	  console.log(e);
	})

	if(state > 3)
		return;

	if(document.getElementById("test").innerHTML === "0")
	{
		const NOTIFICATION_TITLE = 'Just Focus';
		const NOTIFICATION_BODY = 'You are not Paying Attention';
		const CLICK_MESSAGE = 'Notification clicked!';

		new Notification(NOTIFICATION_TITLE, { body: NOTIFICATION_BODY })
		.onclick = () => document.getElementById("output").innerText = CLICK_MESSAGE;

		if(state == 2)
		{
			startRecording();
			state = 3;
		}
		setTimeout(check_timeout_function, 5000);	
	}
	else
		setTimeout(check_timeout_function, 1000);
}

function attention_check()
{
	// let value = 0;
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
	{
		state = 1;
		// return;
	}
	else{

		if(state < 3)
			state = 2;
	}
	setTimeout(attention_check, 1000);
}

function toggle_button_label()
{
	if(state == 0)
		document.getElementById("start_button").innerHTML = "STOP";
	else
	{
		document.getElementById("start_button").innerHTML = "START";
		state = 4;
	}
}

function start_attention_check()
{
	// toggle_button_label();
	if(state == -1)
		state = 0;
	else
		state = 4;	
	check_timeout_function();
	// console.log("clickerd");
	toggle_button_label();
	
	document.getElementById("status").innerHTML = "starting";
	fetch(`http://127.0.0.1:5001/stop`, {method: "POST"});
	attention_check();
	// setTimeout(start_attention_check, 1000);
}

function stop_attention_check()
{
	if(state == 3)
		stopRecording();
	state = 4;
	fetch(`http://127.0.0.1:5001/stop`, {method: "POST"});	
}

window.addEventListener('DOMContentLoaded', () => {
	const replaceText = (selector, text) => {
	  const element = document.getElementById(selector)
	  if (element) element.innerText = text
	}
  
	for (const dependency of ['chrome', 'node', 'electron']) {
	  replaceText(`${dependency}-version`, process.versions[dependency])
	}

	state = -1;
	getSources();
	// check_timeout_function();
	// document.getElementById("start_button").addEventListener("click", start_attention_check);
 
	startButton = document.querySelector('.start-recording');
	stopButton = document.querySelector('.stop-recording');
	downloadButton = document.querySelector('.download-video');
	recordedVideo = document.querySelector('.recorded-video');

	startButton.addEventListener('click', start_attention_check);
	stopButton.addEventListener('click', stop_attention_check);

})