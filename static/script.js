const convert_text = document.getElementById("convert_text");
const startBtn = document.getElementById("start_interview");
const stopBtn = document.getElementById("stop_recording");
const cameraFeed = document.getElementById("camera_feed");
const greetingMessage = document.getElementById("greeting_message");
const feedbackSection = document.getElementById("feedback_section");
const submitFeedbackBtn = document.getElementById("submit_feedback");

let recognition;
let mediaRecorder;
let audioChunks = [];
let finalTranscript = "";
let questionCount = 0;
const maxQuestions = 5; // Specify the number of questions

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
  // Disable the button and show greeting
  startBtn.disabled = true;
  greetingMessage.style.display = "block";
  greetingMessage.textContent = "Welcome! Let's begin the interview.";
  
  // System speaks the greeting
  const speech = new SpeechSynthesisUtterance("Welcome! Let's begin the interview.");
  window.speechSynthesis.speak(speech);

  // Wait for the greeting to finish
  speech.onend = () => {
    proceedWithInterview();
  };
});

function proceedWithInterview() {
  if (questionCount < maxQuestions) {
    // Fetch the next question dynamically
    processVoiceInput(finalTranscript);
  } else {
    endInterview();
  }
}

// Send candidate's response to the backend and fetch the next question
async function processVoiceInput(text) {
  try {
    const response = await fetch("/process_voice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, follow_up_questions: {} }) // Add follow-up questions if needed
    });

    if (!response.ok) {
      throw new Error("Failed to process voice input.");
    }

    const result = await response.json();

    // Display the question and explanation
    convert_text.value = `Question: ${result.question}\nScore: ${result.score}/5\nExplanation: ${result.explanation}`;

    // System speaks the next question
    const speech = new SpeechSynthesisUtterance(result.question);
    window.speechSynthesis.speak(speech);

    // Wait for the question to finish before proceeding
    speech.onend = () => {
      questionCount++;
      finalTranscript = ""; // Reset the transcript for the next question
    };
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

function endInterview() {
  // System speaks the thank-you message
  const thankYouMessage = "Thank you for your time. Please proceed to the feedback section.";
  const speech = new SpeechSynthesisUtterance(thankYouMessage);
  window.speechSynthesis.speak(speech);

  // Wait for the thank-you message to finish
  speech.onend = () => {
    greetingMessage.style.display = "none";
    feedbackSection.style.display = "block";
  };
}

submitFeedbackBtn.addEventListener("click", () => {
  alert("Thank you for your feedback!");
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

  if (finalTranscript) {
    processVoiceInput(finalTranscript);
  }
});



