const convert_text = document.getElementById("convert_text");
const startBtn = document.getElementById("click_to_convert");
const stopBtn = document.getElementById("stop_recording");
const cameraFeed = document.getElementById("camera_feed");

let recognition;
let mediaRecorder;
let audioChunks = [];
let finalTranscript = "";

// Disable Start button until camera loads
startBtn.disabled = true;

// Prompt for camera access immediately on page load
window.addEventListener("load", async () => {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      cameraFeed.srcObject = stream;
      cameraFeed.style.display = "block";
      startBtn.disabled = false;
    } catch (error) {
      alert("Camera access is required to use this app. Please enable camera access and reload the page.");
      startBtn.disabled = true;
    }
  } else {
    alert("Your browser does not support accessing the camera. Please try a different browser.");
    startBtn.disabled = true;
  }
});

startBtn.addEventListener("click", async () => {
  if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
    alert("Speech recognition is not supported in your browser. Please use Chrome.");
    return;
  }

  window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.interimResults = true;
  recognition.continuous = true;

  recognition.onresult = (e) => {
    const transcript = Array.from(e.results)
      .map(result => result[0])
      .map(result => result.transcript)
      .join('');
    finalTranscript = transcript;
    convert_text.value = transcript;
  };

  recognition.onerror = (e) => {
    alert(`Speech recognition error: ${e.error}`);
  };

  recognition.start();

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data);
    };

    mediaRecorder.start();

    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (error) {
    alert("Failed to start audio recording. Please check your microphone permissions.");
  }
});

stopBtn.addEventListener("click", async () => {
  if (recognition) {
    recognition.stop();
  }
  if (mediaRecorder) {
    mediaRecorder.stop();
  }

  mediaRecorder.onstop = async () => {
    try {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", audioBlob, "voice.webm");
      formData.append("transcript", finalTranscript);

      const response = await fetch("/save", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to save audio and transcript.");
      }

      const result = await response.json();
      alert(result.message);
    } catch (error) {
      alert(`Error saving data: ${error.message}`);
    } finally {
      startBtn.disabled = false;
      stopBtn.disabled = true;
      convert_text.value = "";
    }
  };
});



