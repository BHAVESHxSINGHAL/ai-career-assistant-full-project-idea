import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Bot,
  BriefcaseBusiness,
  CheckCircle2,
  ClipboardCopy,
  FileText,
  Gauge,
  GraduationCap,
  Home,
  Loader2,
  Mail,
  MessageSquareText,
  Send,
  Sparkles,
  Target,
  Upload,
  UserRound,
} from "lucide-react";
import { analyzeFile, analyzeText, askCareerBot, getCoverLetter, getInterview } from "./api";
import "./styles.css";

const sampleText = `Priya Sharma
Data Analyst Intern

Education
Bachelor of Technology in Computer Science

Experience
1.5 years of experience through internships and academic analytics projects.

Skills
Python, SQL, Excel, Pandas, NumPy, Statistics, Data Visualization, Power BI, Git

Projects
Built a sales dashboard in Power BI using SQL queries and Excel cleaning workflows.
Created a Python analysis notebook with pandas and NumPy to identify customer churn patterns.`;

const navItems = [
  { id: "home", label: "Home", icon: Home },
  { id: "profile", label: "Resume", icon: UserRound },
  { id: "jobs", label: "Jobs", icon: BriefcaseBusiness },
  { id: "chat", label: "Chatbot", icon: Bot },
  { id: "interview", label: "Interview", icon: GraduationCap },
  { id: "cover", label: "Cover Letter", icon: Mail },
];

function App() {
  const [activeView, setActiveView] = useState("home");
  const [resumeText, setResumeText] = useState(sampleText);
  const [analysis, setAnalysis] = useState(null);
  const [activeRole, setActiveRole] = useState("");
  const [chatInput, setChatInput] = useState("What jobs fit my profile?");
  const [messages, setMessages] = useState([]);
  const [interview, setInterview] = useState(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [company, setCompany] = useState("Hiring Team");
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  const topRole = analysis?.recommended_roles?.[0];
  const selectedRole = activeRole || topRole?.role || "Data Analyst";
  const selectedRoleDetails = analysis?.recommended_roles?.find((role) => role.role === selectedRole) || topRole;

  const scoreTone = useMemo(() => {
    const score = analysis?.score || 0;
    if (score >= 75) return "strong";
    if (score >= 55) return "medium";
    return "low";
  }, [analysis]);

  async function runAnalysis() {
    setError("");
    setLoading("analysis");
    try {
      const result = await analyzeText(resumeText);
      applyAnalysis(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function uploadResume(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError("");
    setFileName(file.name);
    setLoading("analysis");
    try {
      const result = await analyzeFile(file);
      setResumeText(result.profile.resume_text);
      applyAnalysis(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
      event.target.value = "";
    }
  }

  function applyAnalysis(result) {
    setAnalysis(result);
    setActiveRole(result.recommended_roles?.[0]?.role || "");
    setInterview(null);
    setCoverLetter("");
    setActiveView("profile");
  }

  async function sendMessage(event, preset) {
    event?.preventDefault();
    const text = (preset || chatInput).trim();
    if (!text) return;

    setMessages((current) => [...current, { role: "user", content: text }]);
    setChatInput("");
    setLoading("chat");
    try {
      const response = await askCareerBot(text, analysis);
      setMessages((current) => [...current, { role: "assistant", content: response.answer, source: response.source }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function buildInterview() {
    setLoading("interview");
    setError("");
    try {
      setInterview(await getInterview(selectedRole, true));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function buildCoverLetter() {
    if (!analysis) return;
    setLoading("cover");
    setError("");
    try {
      const result = await getCoverLetter(selectedRole, company, analysis.profile);
      setCoverLetter(result.cover_letter);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function copyCoverLetter() {
    if (!coverLetter || !navigator.clipboard) return;
    await navigator.clipboard.writeText(coverLetter);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <button className="brand-button" onClick={() => setActiveView("home")}>
          <span className="brand-mark"><Sparkles size={19} /></span>
          <span>
            <strong>AI Career Assistant</strong>
            <small>{topRole ? `${topRole.role} match ready` : "Resume intelligence"}</small>
          </span>
        </button>

        <nav className="nav-tabs" aria-label="Primary navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                className={activeView === item.id ? "active" : ""}
                key={item.id}
                onClick={() => setActiveView(item.id)}
                title={item.label}
              >
                <Icon size={17} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </header>

      <section className="workspace">
        {error && (
          <div className="error-box">
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {activeView === "home" && (
          <HomeView
            analysis={analysis}
            fileName={fileName}
            loading={loading}
            resumeText={resumeText}
            scoreTone={scoreTone}
            topRole={topRole}
            onAnalyze={runAnalysis}
            onResumeText={setResumeText}
            onUpload={uploadResume}
            onViewProfile={() => setActiveView("profile")}
          />
        )}

        {activeView === "profile" && (
          <ProfileView analysis={analysis} scoreTone={scoreTone} topRole={topRole} onHome={() => setActiveView("home")} />
        )}

        {activeView === "jobs" && (
          <JobsView
            analysis={analysis}
            selectedRole={selectedRole}
            selectedRoleDetails={selectedRoleDetails}
            onHome={() => setActiveView("home")}
            onRole={setActiveRole}
            onAsk={(prompt) => {
              setActiveView("chat");
              setChatInput(prompt);
            }}
          />
        )}

        {activeView === "chat" && (
          <ChatView
            analysis={analysis}
            chatInput={chatInput}
            loading={loading}
            messages={messages}
            onChatInput={setChatInput}
            onHome={() => setActiveView("home")}
            onSend={sendMessage}
          />
        )}

        {activeView === "interview" && (
          <InterviewView
            analysis={analysis}
            interview={interview}
            loading={loading}
            selectedRole={selectedRole}
            onBuild={buildInterview}
            onHome={() => setActiveView("home")}
            onRole={setActiveRole}
          />
        )}

        {activeView === "cover" && (
          <CoverLetterView
            analysis={analysis}
            company={company}
            coverLetter={coverLetter}
            loading={loading}
            selectedRole={selectedRole}
            onBuild={buildCoverLetter}
            onCompany={setCompany}
            onCopy={copyCoverLetter}
            onHome={() => setActiveView("home")}
            onRole={setActiveRole}
          />
        )}
      </section>
    </main>
  );
}

function HomeView({ analysis, fileName, loading, resumeText, scoreTone, topRole, onAnalyze, onResumeText, onUpload, onViewProfile }) {
  return (
    <div className="view-stack">
      <section className="home-hero">
        <div className="home-copy">
          <span className="eyebrow"><Sparkles size={15} /> Career workspace</span>
          <h1>Analyze your resume and turn it into a job plan.</h1>
          <p>Upload a resume or edit the sample text, then generate matches, skill gaps, interview practice, and a cover letter.</p>
          <div className="hero-actions">
            <button className="primary-action" onClick={onAnalyze} disabled={loading === "analysis"}>
              {loading === "analysis" ? <Loader2 className="spin" size={18} /> : <Gauge size={18} />}
              Analyze Resume
            </button>
            {analysis && (
              <button className="ghost-action" onClick={onViewProfile}>
                <FileText size={18} />
                View Results
              </button>
            )}
          </div>
        </div>

        <div className="score-card">
          <div className={`score-ring ${scoreTone}`}>
            <span>{analysis?.score ?? "--"}</span>
            <small>/100</small>
          </div>
          <div>
            <strong>{topRole ? topRole.role : "No analysis yet"}</strong>
            <span>{topRole ? `${topRole.match_percentage}% role match` : "Ready when you are"}</span>
          </div>
        </div>
      </section>

      <section className="home-grid">
        <div className="panel upload-panel">
          <div className="section-title">
            <Upload size={18} />
            <h2>Resume Uploader</h2>
          </div>

          <label className="upload-zone">
            <Upload size={24} />
            <span>{fileName || "Drop in PDF or text resume"}</span>
            <input type="file" accept=".txt,.pdf" onChange={onUpload} />
          </label>

          <label className="field-label" htmlFor="resume-text">Resume text</label>
          <textarea
            id="resume-text"
            value={resumeText}
            onChange={(event) => onResumeText(event.target.value)}
            spellCheck="false"
          />
        </div>

        <div className="home-side">
          <FeatureTile icon={FileText} title="Resume score" value={analysis ? `${analysis.score}/100` : "Pending"} />
          <FeatureTile icon={BriefcaseBusiness} title="Best role" value={topRole?.role || "Pending"} />
          <FeatureTile icon={Target} title="Skill gaps" value={analysis?.missing_skills?.slice(0, 2).join(", ") || "Pending"} />
        </div>
      </section>
    </div>
  );
}

function ProfileView({ analysis, scoreTone, topRole, onHome }) {
  if (!analysis) return <NoAnalysis onHome={onHome} />;

  return (
    <div className="view-stack">
      <SummaryBand analysis={analysis} scoreTone={scoreTone} topRole={topRole} />
      <section className="two-column">
        <div className="panel">
          <div className="section-title">
            <UserRound size={18} />
            <h2>Resume Profile</h2>
          </div>
          <div className="metric-strip">
            <Stat label="Skills" value={analysis.profile.skills.length} />
            <Stat label="Experience" value={`${analysis.profile.experience_years}y`} />
            <Stat label="Education" value={analysis.profile.education.length || 0} />
          </div>
          <h3>Detected skills</h3>
          <ChipList items={analysis.profile.skills} empty="No skills detected" />
          <h3>Education</h3>
          <ChipList items={analysis.profile.education} empty="No education detected" variant="neutral" />
        </div>

        <div className="panel">
          <div className="section-title">
            <Gauge size={18} />
            <h2>Score Breakdown</h2>
          </div>
          <ul className="compact-list check-list">
            {analysis.score_explanation.map((item) => <li key={item}>{item}</li>)}
          </ul>
          <h3>Improvements</h3>
          <ul className="compact-list action-list">
            {analysis.suggestions.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </section>
    </div>
  );
}

function JobsView({ analysis, selectedRole, selectedRoleDetails, onAsk, onHome, onRole }) {
  if (!analysis) return <NoAnalysis onHome={onHome} />;

  return (
    <section className="jobs-layout">
      <div className="panel role-menu">
        <div className="section-title">
          <BriefcaseBusiness size={18} />
          <h2>Job Matches</h2>
        </div>
        {analysis.recommended_roles.map((role) => (
          <button
            className={`role-row ${selectedRole === role.role ? "active" : ""}`}
            key={role.role}
            onClick={() => onRole(role.role)}
          >
            <span>
              <strong>{role.role}</strong>
              <small>{role.category}</small>
            </span>
            <b>{role.match_percentage}%</b>
          </button>
        ))}
      </div>

      <div className="panel role-detail">
        <div className="role-heading">
          <div>
            <span className="eyebrow"><Target size={15} /> Selected role</span>
            <h1>{selectedRoleDetails.role}</h1>
            <p>{selectedRoleDetails.description}</p>
          </div>
          <strong className="match-badge">{selectedRoleDetails.match_percentage}%</strong>
        </div>

        <div className="skill-columns">
          <div>
            <h3>Matched skills</h3>
            <ChipList items={selectedRoleDetails.matched_skills} empty="No matched skills yet" />
          </div>
          <div>
            <h3>Missing skills</h3>
            <ChipList items={selectedRoleDetails.missing_skills} empty="No major gaps" variant="gap" />
          </div>
        </div>

        <h3>Roadmap</h3>
        <ol className="roadmap">
          {selectedRoleDetails.roadmap.map((step) => <li key={step}>{step}</li>)}
        </ol>

        <button className="primary-action inline-action" onClick={() => onAsk(`Create a roadmap for ${selectedRoleDetails.role}`)}>
          <MessageSquareText size={18} />
          Ask Chatbot
        </button>
      </div>
    </section>
  );
}

function ChatView({ analysis, chatInput, loading, messages, onChatInput, onHome, onSend }) {
  const prompts = [
    "What jobs fit my profile?",
    "Improve my resume",
    "What skills am I missing?",
    "Generate interview questions",
  ];

  return (
    <section className="panel chat-view">
      <div className="section-title">
        <Bot size={19} />
        <h2>Career Chatbot</h2>
      </div>
      {!analysis && <NoAnalysis compact onHome={onHome} />}

      <div className="prompt-row">
        {prompts.map((prompt) => (
          <button className="prompt-chip" key={prompt} onClick={(event) => onSend(event, prompt)}>
            {prompt}
          </button>
        ))}
      </div>

      <div className="chat-log">
        {messages.length === 0 && (
          <div className="empty-state">
            <MessageSquareText size={20} />
            <strong>Career answers will appear here</strong>
          </div>
        )}
        {messages.map((message, index) => (
          <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
            <pre>{message.content}</pre>
            {message.source && <small>{message.source}</small>}
          </div>
        ))}
        {loading === "chat" && <div className="message assistant">Thinking...</div>}
      </div>

      <form className="chat-form" onSubmit={onSend}>
        <input
          value={chatInput}
          onChange={(event) => onChatInput(event.target.value)}
          placeholder="Ask a career question"
        />
        <button aria-label="Send message" disabled={loading === "chat"}>
          <Send size={18} />
        </button>
      </form>
    </section>
  );
}

function InterviewView({ analysis, interview, loading, selectedRole, onBuild, onHome, onRole }) {
  if (!analysis) return <NoAnalysis onHome={onHome} />;

  return (
    <section className="panel prep-view">
      <div className="section-title">
        <GraduationCap size={19} />
        <h2>Interview Prep</h2>
      </div>
      <div className="control-bar">
        <RoleSelect analysis={analysis} selectedRole={selectedRole} onRole={onRole} />
        <button className="primary-action" onClick={onBuild} disabled={loading === "interview"}>
          {loading === "interview" ? <Loader2 className="spin" size={18} /> : <BookOpen size={18} />}
          Generate Questions
        </button>
      </div>

      {interview ? (
        <div className="question-grid">
          {interview.questions.map((item) => (
            <article className="question-card" key={item.question}>
              <span>{item.kind}</span>
              <h3>{item.question}</h3>
              {item.answer && <p>{item.answer}</p>}
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state large">
          <GraduationCap size={26} />
          <strong>{selectedRole} practice set</strong>
        </div>
      )}
    </section>
  );
}

function CoverLetterView({ analysis, company, coverLetter, loading, selectedRole, onBuild, onCompany, onCopy, onHome, onRole }) {
  if (!analysis) return <NoAnalysis onHome={onHome} />;

  return (
    <section className="cover-layout">
      <div className="panel cover-controls">
        <div className="section-title">
          <Mail size={19} />
          <h2>Cover Letter</h2>
        </div>
        <RoleSelect analysis={analysis} selectedRole={selectedRole} onRole={onRole} />
        <label className="field-label" htmlFor="company">Company</label>
        <input id="company" value={company} onChange={(event) => onCompany(event.target.value)} />
        <button className="primary-action" onClick={onBuild} disabled={loading === "cover"}>
          {loading === "cover" ? <Loader2 className="spin" size={18} /> : <FileText size={18} />}
          Generate Letter
        </button>
      </div>

      <div className="panel letter-preview">
        <div className="preview-header">
          <span className="eyebrow"><FileText size={15} /> Draft</span>
          <button className="ghost-action icon-action" onClick={onCopy} disabled={!coverLetter} title="Copy">
            <ClipboardCopy size={18} />
          </button>
        </div>
        {coverLetter ? (
          <pre>{coverLetter}</pre>
        ) : (
          <div className="empty-state large">
            <Mail size={26} />
            <strong>{selectedRole} cover letter</strong>
          </div>
        )}
      </div>
    </section>
  );
}

function SummaryBand({ analysis, scoreTone, topRole }) {
  return (
    <section className="summary-band">
      <div className={`score-ring ${scoreTone}`}>
        <span>{analysis.score}</span>
        <small>/100</small>
      </div>
      <div className="summary-copy">
        <span className="eyebrow"><CheckCircle2 size={15} /> Analysis complete</span>
        <h1>{topRole ? `${topRole.role} is your strongest match` : "Resume analysis complete"}</h1>
        <p>{topRole?.description || "Your profile is ready for review."}</p>
      </div>
      <div className="quick-stats">
        <Stat label="Skills" value={analysis.profile.skills.length} />
        <Stat label="Experience" value={`${analysis.profile.experience_years}y`} />
        <Stat label="Roles" value={analysis.recommended_roles.length} />
      </div>
    </section>
  );
}

function NoAnalysis({ compact = false, onHome }) {
  return (
    <div className={`empty-state ${compact ? "" : "large"}`}>
      <FileText size={compact ? 18 : 28} />
      <strong>No resume analysis yet</strong>
      <button className="ghost-action" onClick={onHome}>
        <Upload size={17} />
        Go Home
      </button>
    </div>
  );
}

function FeatureTile({ icon: Icon, title, value }) {
  return (
    <div className="feature-tile">
      <span><Icon size={18} /></span>
      <div>
        <small>{title}</small>
        <strong>{value}</strong>
      </div>
      <ArrowRight size={17} />
    </div>
  );
}

function RoleSelect({ analysis, selectedRole, onRole }) {
  return (
    <label className="field-label role-select" htmlFor="target-role">
      Target role
      <select id="target-role" value={selectedRole} onChange={(event) => onRole(event.target.value)}>
        {analysis.recommended_roles.map((role) => (
          <option key={role.role} value={role.role}>{role.role}</option>
        ))}
      </select>
    </label>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

function ChipList({ items, empty, variant = "" }) {
  if (!items?.length) return <p className="muted">{empty}</p>;
  return (
    <div className={`chip-list ${variant}`}>
      {items.map((item) => <span key={item}>{item}</span>)}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
