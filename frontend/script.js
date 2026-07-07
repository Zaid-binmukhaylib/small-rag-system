// =========================================================
// Configuration
// =========================================================
// Base URL of the FastAPI backend. Empty means "same origin" — the frontend
// is served by the backend, so requests go to the same host (works locally
// and through a public tunnel).
const API_BASE_URL = "";

// =========================================================
// Element references
// =========================================================
const resumeFileInput = document.getElementById("resumeFile");
const uploadDropzone = document.getElementById("uploadDropzone");
const fileNameLabel = document.getElementById("fileName");
const uploadBtn = document.getElementById("uploadBtn");

const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const chatWindow = document.getElementById("chatWindow");
const chatEmpty = document.getElementById("chatEmpty");

// In-memory conversation history. Lives only in the page — a refresh clears it.
const conversationHistory = [];

const alertBanner = document.getElementById("alertBanner");

const tabQA = document.getElementById("tabQA");
const tabMatch = document.getElementById("tabMatch");
const qaSection = document.getElementById("qaSection");
const matchSection = document.getElementById("matchSection");

const matchResumeFilesInput = document.getElementById("matchResumeFiles");
const matchFileNamesLabel = document.getElementById("matchFileNames");
const matchUploadBtn = document.getElementById("matchUploadBtn");

const jobDescriptionInput = document.getElementById("jobDescriptionInput");
const matchBtn = document.getElementById("matchBtn");
const matchLoadingIndicator = document.getElementById("matchLoadingIndicator");
const matchFilename = document.getElementById("matchFilename");
const matchText = document.getElementById("matchText");

// =========================================================
// Alert helper
// =========================================================
// Shows a temporary success/error banner at the top of the page.
let alertTimeoutId = null;

function showAlert(message, type = "success") {
  clearTimeout(alertTimeoutId);

  alertBanner.textContent = message;
  alertBanner.className = `alert ${type}`;
  alertBanner.classList.remove("hidden");

  alertTimeoutId = setTimeout(() => {
    alertBanner.classList.add("hidden");
  }, 4000);
}

// =========================================================
// Button loading-state helper
// =========================================================
// Toggles a small spinner inside a button and disables it
// while a request is in flight.
function setButtonLoading(button, isLoading) {
  const label = button.querySelector(".btn-label");
  const spinner = button.querySelector(".btn-spinner");

  button.disabled = isLoading;
  spinner.classList.toggle("hidden", !isLoading);
  label.style.opacity = isLoading ? "0.6" : "1";
}

// =========================================================
// Tab switching
// =========================================================
function showTab(tab) {
  const isQA = tab === "qa";

  tabQA.classList.toggle("active", isQA);
  tabMatch.classList.toggle("active", !isQA);
  qaSection.classList.toggle("hidden", !isQA);
  matchSection.classList.toggle("hidden", isQA);
}

tabQA.addEventListener("click", () => showTab("qa"));
tabMatch.addEventListener("click", () => showTab("match"));

// =========================================================
// Upload Resume
// =========================================================

// Update the displayed file name whenever a new file is chosen
resumeFileInput.addEventListener("change", () => {
  const file = resumeFileInput.files[0];
  fileNameLabel.textContent = file ? file.name : "No file selected";
});

uploadBtn.addEventListener("click", async () => {
  const file = resumeFileInput.files[0];

  if (!file) {
    showAlert("Please choose a PDF file before uploading.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setButtonLoading(uploadBtn, true);

  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Upload request failed.");
    }

    showAlert(`"${file.name}" uploaded successfully.`, "success");
  } catch (error) {
    showAlert("Failed to upload resume. Please try again.", "error");
  } finally {
    setButtonLoading(uploadBtn, false);
  }
});

// =========================================================
// Ask a Question (continuous chat)
// =========================================================

// Append a chat bubble to the conversation window and scroll to it.
function addChatMessage(role, text) {
  if (chatEmpty) chatEmpty.classList.add("hidden");

  const bubble = document.createElement("div");
  bubble.className = `chat-message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "chat-avatar";
  avatar.textContent = role === "user" ? "You" : "AI";

  const text_el = document.createElement("p");
  text_el.className = "chat-text";
  text_el.textContent = text;

  bubble.appendChild(avatar);
  bubble.appendChild(text_el);
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return text_el;
}

async function askQuestion() {
  const question = questionInput.value.trim();

  if (!question) {
    showAlert("Please type a question first.", "error");
    return;
  }

  // Show the user's message immediately and clear the input.
  addChatMessage("user", question);
  questionInput.value = "";

  setButtonLoading(askBtn, true);
  loadingIndicator.classList.remove("hidden");

  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      // Send the prior conversation so the model remembers the context.
      body: JSON.stringify({ question, history: conversationHistory })
    });

    if (!response.ok) {
      throw new Error("Ask request failed.");
    }

    const data = await response.json();
    addChatMessage("assistant", data.answer);

    // Remember this turn for the next question.
    conversationHistory.push({ role: "user", content: question });
    conversationHistory.push({ role: "assistant", content: data.answer });
  } catch (error) {
    showAlert("Failed to get an answer. Please try again.", "error");
    addChatMessage("assistant", "Something went wrong while fetching the answer.");
  } finally {
    setButtonLoading(askBtn, false);
    loadingIndicator.classList.add("hidden");
  }
}

askBtn.addEventListener("click", askQuestion);

// Allow pressing Enter in the question field to submit
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    askQuestion();
  }
});

// =========================================================
// Job Matcher — upload resumes to the matching pool
// =========================================================

// Update the displayed file names whenever new files are chosen
matchResumeFilesInput.addEventListener("change", () => {
  const files = matchResumeFilesInput.files;

  matchFileNamesLabel.textContent = files.length
    ? Array.from(files).map((f) => f.name).join(", ")
    : "No files selected";
});

matchUploadBtn.addEventListener("click", async () => {
  const files = matchResumeFilesInput.files;

  if (!files.length) {
    showAlert("Please choose at least one PDF file before uploading.", "error");
    return;
  }

  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));

  setButtonLoading(matchUploadBtn, true);

  try {
    const response = await fetch(`${API_BASE_URL}/match/upload`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Upload request failed.");
    }

    const data = await response.json();
    showAlert(`Uploaded ${data.filenames.length} resume(s) successfully.`, "success");
  } catch (error) {
    showAlert("Failed to upload resumes. Please try again.", "error");
  } finally {
    setButtonLoading(matchUploadBtn, false);
  }
});

// =========================================================
// Job Matcher — find best match
// =========================================================

async function matchJob() {
  const jobDescription = jobDescriptionInput.value.trim();

  if (!jobDescription) {
    showAlert("Please describe the job first.", "error");
    return;
  }

  setButtonLoading(matchBtn, true);
  matchLoadingIndicator.classList.remove("hidden");

  try {
    const response = await fetch(`${API_BASE_URL}/match`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ job_description: jobDescription })
    });

    if (!response.ok) {
      throw new Error("Match request failed.");
    }

    const data = await response.json();
    matchFilename.textContent = `Best match: ${data.filename}`;
    matchText.textContent = data.resume_text;
  } catch (error) {
    showAlert("Failed to find a matching resume. Please try again.", "error");
    matchFilename.textContent = "";
    matchText.textContent = "Something went wrong while matching resumes.";
  } finally {
    setButtonLoading(matchBtn, false);
    matchLoadingIndicator.classList.add("hidden");
  }
}

matchBtn.addEventListener("click", matchJob);

// Allow pressing Enter in the job description field to submit
jobDescriptionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    matchJob();
  }
});
