const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

export async function analyzeFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/resume/analyze", {
    method: "POST",
    body: formData,
  });
}

export async function analyzeText(text) {
  return request("/api/resume/analyze-text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export async function askCareerBot(message, analysis) {
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, analysis }),
  });
}

export async function getInterview(role, includeAnswers) {
  return request("/api/interview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, include_answers: includeAnswers }),
  });
}

export async function getCoverLetter(role, company, profile) {
  return request("/api/cover-letter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, company, profile }),
  });
}
