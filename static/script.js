const convert_text = document.getElementById("convert_text");
const startBtn = document.getElementById("click_to_convert");
const stopBtn = document.getElementById("stop_recording");

let recognition;
let mediaRecorder;
let audioChunks = [];
let finalTranscript = "";

startBtn.addEventListener("click", async () => {
  window.SpeechRecognition = window.webkitSpeechRecognition;
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

  recognition.start();

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = (e) => {
    audioChunks.push(e.data);
  };

  mediaRecorder.start();

  startBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", async () => {
  recognition.stop();
  mediaRecorder.stop();

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", audioBlob, "voice.webm");
    formData.append("transcript", finalTranscript);

    const response = await fetch("/save", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    alert(result.message);

    startBtn.disabled = false;
    stopBtn.disabled = true;
    convert_text.value = ""; // Optional: reset text box
  };
});
