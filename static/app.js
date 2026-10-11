/**
 * AI Studio Pro — Desktop Dashboard Application Logic (app.js)
 * Clean, modern vanilla JavaScript connecting to desktop_server.py REST APIs.
 */

// Application State
const AppState = {
  activeTab: "studio",
  activeJobId: null,
  pollTimer: null,
  projects: [],
  selectedProjectId: null,
  currentBlueprint: null,
};

// DOM References
const elements = {
  tabs: document.querySelectorAll(".nav-tab"),
  panes: document.querySelectorAll(".tab-pane"),
  
  // Topic Inputs
  topicInput: document.getElementById("topic-input"),
  refImageInput: document.getElementById("ref-image-input"),
  refVideoInput: document.getElementById("ref-video-input"),
  remodifyBtn: document.getElementById("remodify-btn"),
  suggestBtn: document.getElementById("suggest-btn"),
  
  // Blueprint Preview
  bpPreview: document.getElementById("blueprint-preview"),
  bpTitle: document.getElementById("bp-title"),
  bpTool: document.getElementById("bp-tool"),
  bpRpm: document.getElementById("bp-rpm"),
  bpFormat: document.getElementById("bp-format"),
  bpPoints: document.getElementById("bp-points"),
  
  // Configs
  configFormat: document.getElementById("config-format"),
  configVoice: document.getElementById("config-voice"),
  configLanguage: document.getElementById("config-language"),
  configSubtitles: document.getElementById("config-subtitles"),
  configQuality: document.getElementById("config-quality"),
  configMotion: document.getElementById("config-motion"),
  configSpeechRate: document.getElementById("config-speech-rate"),
  configBroll: document.getElementById("config-broll"),
  configMusic: document.getElementById("config-music"),
  configUploadMode: document.getElementById("config-upload-mode"),
  
  // Generation & Monitor
  startPipelineBtn: document.getElementById("start-pipeline-btn"),
  currentStageLabel: document.getElementById("current-stage-label"),
  progressPercent: document.getElementById("progress-percent"),
  progressBarFill: document.getElementById("progress-bar-fill"),
  consoleStream: document.getElementById("console-stream"),
  
  // Library
  projectsListContainer: document.getElementById("projects-list-container"),
  refreshProjectsBtn: document.getElementById("refresh-projects-btn"),
  libraryVideoPlayer: document.getElementById("library-video-player"),
  libraryAudioPlayer: document.getElementById("library-audio-player"),
  libraryThumbnailImg: document.getElementById("library-thumbnail-img"),
  videoContainer: document.getElementById("video-container"),
  audioContainer: document.getElementById("audio-container"),
  selectedProjectTitle: document.getElementById("selected-project-title"),
  selectedProjectMeta: document.getElementById("selected-project-meta"),
  selectedProjectBadge: document.getElementById("selected-project-badge"),
  libraryYtTitle: document.getElementById("library-yt-title"),
  libraryYtDesc: document.getElementById("library-yt-desc"),
  libraryTagsContainer: document.getElementById("library-tags-container"),
  libUploadBtn: document.getElementById("lib-upload-btn"),
  libAuditBtn: document.getElementById("lib-audit-btn"),
  
  // Trend Radar
  trendCardsContainer: document.getElementById("trend-cards-container"),
  
  // Compliance
  auditScoreNum: document.getElementById("audit-score-num"),
  auditScoreText: document.getElementById("audit-score-text"),
  auditChecksContainer: document.getElementById("audit-checks-container"),
  runLatestAuditBtn: document.getElementById("run-latest-audit-btn"),
  testTitle: document.getElementById("test-title"),
  testBody: document.getElementById("test-body"),
  testAiDisclosure: document.getElementById("test-ai-disclosure"),
  runCustomAuditBtn: document.getElementById("run-custom-audit-btn"),
  customAuditResults: document.getElementById("custom-audit-results"),
  
  // Model Advisor
  modelAdvisorContent: document.getElementById("model-advisor-content"),
  
  // Modal & Profile
  profileModal: document.getElementById("profile-modal"),
  openProfileBtn: document.getElementById("open-profile-btn"),
  closeProfileBtn: document.getElementById("close-profile-btn")
};

// -----------------------------------------------------------------------------
// 1. Navigation & Tab Switching
// -----------------------------------------------------------------------------
function setupNavigation() {
  elements.tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetTab = tab.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  // Modal events
  if (elements.openProfileBtn) {
    elements.openProfileBtn.addEventListener("click", () => {
      elements.profileModal.classList.add("active");
    });
  }
  if (elements.closeProfileBtn) {
    elements.closeProfileBtn.addEventListener("click", () => {
      elements.profileModal.classList.remove("active");
    });
  }
}

function switchTab(tabName) {
  AppState.activeTab = tabName;
  elements.tabs.forEach((t) => {
    t.classList.toggle("active", t.getAttribute("data-tab") === tabName);
  });
  elements.panes.forEach((pane) => {
    pane.classList.toggle("active", pane.id === `pane-${tabName}`);
  });

  // Lazy load tab data
  if (tabName === "library") {
    loadProjectsList();
  } else if (tabName === "trends") {
    loadTrendRadar();
  } else if (tabName === "compliance") {
    loadLatestCompliance();
  } else if (tabName === "advisor") {
    loadModelAdvisor();
  }
}

// -----------------------------------------------------------------------------
// 2. Blueprint Remodify & Trending Suggestions
// -----------------------------------------------------------------------------
function setupBlueprintActions() {
  elements.remodifyBtn.addEventListener("click", async () => {
    const rawInput = elements.topicInput.value.trim() || "Claude 3.7 Artifacts Masterclass";
    const videoFormat = elements.configFormat.value;
    const refNotes = [
      elements.refImageInput.value ? `Image Ref: ${elements.refImageInput.value}` : "",
      elements.refVideoInput.value ? `Link Ref: ${elements.refVideoInput.value}` : ""
    ].filter(Boolean).join(" | ");

    appendConsoleLog("PLAN", `Polishing lesson plan for "${rawInput}"...`);

    try {
      const resp = await fetch("/api/topics/remodify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: rawInput, format: videoFormat, notes: refNotes })
      });
      const data = await resp.json();
      if (data.refined) {
        renderBlueprint(data.refined);
        appendConsoleLog("OK", `Lesson plan ready: "${data.refined.suggested_title}"`);
      }
    } catch (err) {
      appendConsoleLog("ERR", `Could not refine topic: ${err}`);
    }
  });

  elements.suggestBtn.addEventListener("click", async () => {
    appendConsoleLog("TRENDS", "Looking up top trending AI tools...");
    try {
      const resp = await fetch("/api/topics/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche: "all" })
      });
      const data = await resp.json();
      if (data.suggestions && data.suggestions.length > 0) {
        // Pick a random suggestion
        const item = data.suggestions[Math.floor(Math.random() * data.suggestions.length)];
        elements.topicInput.value = `${item.tool_name} — ${item.angle}`;
        renderBlueprint({
          tool_name: item.tool_name,
          suggested_title: item.suggested_title,
          angle: item.angle,
          format: "Step-by-Step Guide",
          potential_rpm: item.potential_rpm || "$14 - $28",
          key_points: item.key_points || []
        });
        appendConsoleLog("OK", `Picked trending tool: ${item.tool_name} (${item.suggested_title})`);
      }
    } catch (err) {
      appendConsoleLog("ERR", `Could not fetch suggestions: ${err}`);
    }
  });
}

function renderBlueprint(bp) {
  AppState.currentBlueprint = bp;
  elements.bpTitle.textContent = bp.suggested_title || "Educational Tutorial";
  elements.bpTool.textContent = `Tool: ${bp.tool_name || "AI Tool"}`;
  elements.bpRpm.textContent = `Est. RPM: ${bp.potential_rpm || "$14 - $28"}`;
  elements.bpFormat.textContent = bp.format || "Step-by-Step Hands-On";

  elements.bpPoints.innerHTML = "";
  const points = bp.key_points || [
    "Comprehensive setup and foundational architecture",
    "Hands-on step-by-step tactical implementation",
    "Pro-level optimization and revenue workflows"
  ];
  points.forEach((pt) => {
    const li = document.createElement("li");
    li.textContent = pt;
    elements.bpPoints.appendChild(li);
  });

  elements.bpPreview.style.display = "block";
}

// -----------------------------------------------------------------------------
// 3. Pipeline Generation & Job Monitor
// -----------------------------------------------------------------------------
function getFriendlyStageName(stage) {
  switch (stage) {
    case 1: return "Step 1 of 6: Researching Topic & Lesson Plan...";
    case 2: return "Step 2 of 6: Writing 1,500-Word Educational Script...";
    case 3: return "Step 3 of 6: Recording Studio Voiceover...";
    case 4: return "Step 4 of 6: Designing 1080p Lesson Slides...";
    case 5: return "Step 5 of 6: Assembling Video & Mixing Music...";
    case 6: return "Step 6 of 6: Creating 3 Thumbnail Covers & SEO...";
    case 7: return "🎉 Video Ready! Loading Your Video Player...";
    default: return `Working on Step ${stage}...`;
  }
}

function setupPipelineLauncher() {
  elements.startPipelineBtn.addEventListener("click", async () => {
    const rawInput = elements.topicInput.value.trim();
    const toolName = AppState.currentBlueprint?.tool_name || (rawInput ? rawInput.split(":")[0] : "Claude 3.7 Artifacts");
    const angle = AppState.currentBlueprint?.angle || rawInput;
    const voiceAvatar = elements.configVoice.value;
    const uploadMode = elements.configUploadMode.value;
    const autoUpload = uploadMode.startsWith("auto");
    const privacy = uploadMode === "auto_unlisted" ? "unlisted" : "private";

    elements.startPipelineBtn.disabled = true;
    elements.startPipelineBtn.innerHTML = "⏳ Making Your Video... (Please wait 1-2 mins)";

    appendConsoleLog("START", `Starting video creation for "${toolName}" [Voice: ${voiceAvatar}]`);
    updateProgress(10, getFriendlyStageName(1));
    setStageActive(1);

    try {
      const resp = await fetch("/api/pipeline/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool_name: toolName,
          angle: angle,
          auto_upload: autoUpload,
          privacy: privacy,
          voice_avatar: voiceAvatar,
          ken_burns: elements.configMotion?.value === "true",
          speaking_rate: parseInt(elements.configSpeechRate?.value || "165")
        })
      });
      const data = await resp.json();
      if (data.job_id) {
        AppState.activeJobId = data.job_id;
        startJobPolling(data.job_id);
      }
    } catch (err) {
      appendConsoleLog("ERR", `Launch failed: ${err}`);
      elements.startPipelineBtn.disabled = false;
      elements.startPipelineBtn.innerHTML = "🎬 Create My Video Now (One-Click)";
    }
  });
}

function startJobPolling(jobId) {
  if (AppState.pollTimer) clearInterval(AppState.pollTimer);

  AppState.pollTimer = setInterval(async () => {
    try {
      const resp = await fetch(`/api/pipeline/job/${jobId}`);
      const job = await resp.json();

      if (job.status === "running") {
        updateProgress(job.progress_percent || 30, getFriendlyStageName(job.stage || 2));
        setStageActive(job.stage || 2);
        if (job.logs && job.logs.length > 0) {
          const lastLog = job.logs[job.logs.length - 1];
          appendConsoleLog("PROGRESS", lastLog);
        }
      } else if (job.status === "completed") {
        clearInterval(AppState.pollTimer);
        updateProgress(100, "🎉 Success! Your Video Is Completely Finished");
        setStageAllDone();
        appendConsoleLog("DONE", `Video ready to watch: ${job.summary?.video_path || "Finished"}`);

        elements.startPipelineBtn.disabled = false;
        elements.startPipelineBtn.innerHTML = "🎬 Create Another Video";

        // Auto switch to library to view video
        setTimeout(() => {
          switchTab("library");
          if (job.project_id) {
            loadProjectDetails(job.project_id);
          }
        }, 1200);
      } else if (job.status === "failed") {
        clearInterval(AppState.pollTimer);
        updateProgress(0, "Notice: Video creation stopped");
        appendConsoleLog("ERR", `Error: ${job.error || "Unknown error"}`);
        elements.startPipelineBtn.disabled = false;
        elements.startPipelineBtn.innerHTML = "🎬 Create My Video Now (One-Click)";
      }
    } catch (err) {
      console.warn("Polling error:", err);
    }
  }, 1800);
}

function updateProgress(percent, label) {
  elements.progressPercent.textContent = `${percent}%`;
  elements.progressBarFill.style.width = `${percent}%`;
  if (label) elements.currentStageLabel.textContent = `Status: ${label}`;
}

function setStageActive(stageNum) {
  for (let i = 1; i <= 7; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) {
      el.classList.remove("active", "done");
      if (i < stageNum) el.classList.add("done");
      else if (i === stageNum) el.classList.add("active");
    }
  }
}

function setStageAllDone() {
  for (let i = 1; i <= 7; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) {
      el.classList.remove("active");
      el.classList.add("done");
    }
  }
}

function appendConsoleLog(prefix, message) {
  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  div.className = "console-entry";
  div.innerHTML = `<span class="console-time">[${time}]</span> <strong>[${prefix}]</strong> ${escapeHtml(message)}`;
  elements.consoleStream.appendChild(div);
  elements.consoleStream.scrollTop = elements.consoleStream.scrollHeight;
}

// -----------------------------------------------------------------------------
// 4. Video Library & Media Streaming
// -----------------------------------------------------------------------------
async function loadProjectsList() {
  try {
    const resp = await fetch("/api/projects");
    const data = await resp.json();
    AppState.projects = data.projects || [];
    renderProjectsList(AppState.projects);

    if (AppState.projects.length > 0 && !AppState.selectedProjectId) {
      loadProjectDetails(AppState.projects[0].project_id);
    }
  } catch (err) {
    elements.projectsListContainer.innerHTML = `<div style="color: #f87171; font-size: 0.8rem; padding: 12px;">Failed to load library: ${err}</div>`;
  }
}

function renderProjectsList(projects) {
  if (projects.length === 0) {
    elements.projectsListContainer.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-dim); text-align: center; padding: 20px;">No video projects found. Generate one in Studio Creator!</div>`;
    return;
  }

  elements.projectsListContainer.innerHTML = "";
  projects.forEach((p) => {
    const item = document.createElement("div");
    item.className = "card";
    item.style.padding = "14px";
    item.style.marginBottom = "8px";
    item.style.cursor = "pointer";
    if (p.project_id === AppState.selectedProjectId) {
      item.style.borderColor = "var(--accent-cyan)";
      item.style.background = "rgba(6, 182, 212, 0.08)";
    }

    item.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div style="font-weight: 600; font-size: 0.88rem; color: #fff;">${escapeHtml(p.title)}</div>
        <span class="rpm-badge">${p.has_video ? "1080p MP4" : "Draft"}</span>
      </div>
      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; display: flex; gap: 12px;">
        <span>ID: ${p.project_id}</span>
        <span>Chapters: ${p.chapters_count || 5}</span>
        <span>Size: ${p.video_size_mb} MB</span>
      </div>
    `;

    item.addEventListener("click", () => {
      loadProjectDetails(p.project_id);
    });

    elements.projectsListContainer.appendChild(item);
  });
}

async function loadProjectDetails(projectId) {
  AppState.selectedProjectId = projectId;
  renderProjectsList(AppState.projects); // Refresh selection highlight

  try {
    const resp = await fetch(`/api/project/${projectId}`);
    const data = await resp.json();
    const meta = data.metadata || {};

    elements.selectedProjectTitle.textContent = meta.title || `Project ${projectId}`;
    elements.selectedProjectMeta.textContent = `ID: ${projectId} | Created: ${meta.created_at || "Recent"}`;
    elements.selectedProjectBadge.style.display = "inline-block";

    // Media streaming URLs
    elements.libraryVideoPlayer.src = `/media/video/${projectId}`;
    elements.videoContainer.style.display = "block";

    elements.libraryAudioPlayer.src = `/media/audio/${projectId}`;
    elements.audioContainer.style.display = "block";

    elements.libraryThumbnailImg.src = `/media/thumbnail/${projectId}`;
    elements.libraryThumbnailImg.style.display = "block";

    // Thumbnail A/B testing variation switcher
    document.querySelectorAll(".thumb-var-btn").forEach((btn) => {
      btn.onclick = async () => {
        document.querySelectorAll(".thumb-var-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const variation = btn.getAttribute("data-var");
        elements.libraryThumbnailImg.src = `/media/thumbnail/${projectId}?v=${variation}&t=${Date.now()}`;

        try {
          await fetch(`/api/project/${projectId}/set_thumbnail`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ variation })
          });
          appendConsoleLog("THUMB", `Activated Thumbnail Variation ${variation} for Project ${projectId}`);
        } catch (e) {
          console.warn("Failed to set thumbnail variation:", e);
        }
      };
    });

    // Text fields
    elements.libraryYtTitle.value = meta.title || "";
    elements.libraryYtDesc.value = meta.description || "";

    // Tags
    elements.libraryTagsContainer.innerHTML = "";
    (meta.tags || []).forEach((tag) => {
      const span = document.createElement("span");
      span.className = "tag-pill";
      span.textContent = `#${tag}`;
      elements.libraryTagsContainer.appendChild(span);
    });

  } catch (err) {
    console.warn("Failed to load project details:", err);
  }
}

// -----------------------------------------------------------------------------
// 5. Trend Radar
// -----------------------------------------------------------------------------
async function loadTrendRadar() {
  try {
    const resp = await fetch("/api/topics/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ niche: "all" })
    });
    const data = await resp.json();
    const suggestions = data.suggestions || [];

    elements.trendCardsContainer.innerHTML = "";
    suggestions.forEach((item) => {
      const card = document.createElement("div");
      card.className = "trend-card";

      card.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div style="font-weight: 700; font-size: 1.0rem; color: #fff;">${escapeHtml(item.tool_name)}</div>
            <span class="rpm-badge">${escapeHtml(item.potential_rpm || "$14 - $28")}</span>
          </div>
          <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 600; margin-bottom: 6px;">
            ${escapeHtml(item.suggested_title)}
          </div>
          <div style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 12px; line-height: 1.4;">
            ${escapeHtml(item.reason || item.angle)}
          </div>
          <div style="font-size: 0.72rem; color: var(--text-dim); margin-bottom: 14px;">
            Niche: <strong>${escapeHtml(item.niche || "AI Tools")}</strong>
          </div>
        </div>
        <button class="btn btn-primary btn-block" style="font-size: 0.85rem; padding: 10px 14px;">
          🎬 Create Video on This Topic
        </button>
      `;

      card.querySelector("button").addEventListener("click", () => {
        elements.topicInput.value = `${item.tool_name}: ${item.angle}`;
        switchTab("studio");
        renderBlueprint({
          tool_name: item.tool_name,
          suggested_title: item.suggested_title,
          angle: item.angle,
          format: "Step-by-Step Guide",
          potential_rpm: item.potential_rpm,
          key_points: item.key_points || []
        });
      });

      elements.trendCardsContainer.appendChild(card);
    });
  } catch (err) {
    elements.trendCardsContainer.innerHTML = `<div style="color: #f87171; font-size: 0.8rem;">Failed to load trend radar: ${err}</div>`;
  }
}

// -----------------------------------------------------------------------------
// 6. Monetization & Policy Compliance Shield
// -----------------------------------------------------------------------------
async function loadLatestCompliance() {
  try {
    const resp = await fetch("/api/compliance/latest");
    const data = await resp.json();
    renderComplianceAudit(data.audit);
  } catch (err) {
    console.warn("Compliance load error:", err);
  }
}

function renderComplianceAudit(audit) {
  if (!audit) {
    elements.auditScoreNum.textContent = "--";
    elements.auditScoreText.textContent = "NONE";
    elements.auditChecksContainer.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-dim);">No audit available yet.</div>`;
    return;
  }

  elements.auditScoreNum.textContent = audit.score || 100;
  elements.auditScoreText.textContent = audit.status || "PASS";

  elements.auditChecksContainer.innerHTML = "";

  (audit.passed_checks || []).forEach((chk) => {
    const div = document.createElement("div");
    div.className = "compliance-check-item pass";
    div.innerHTML = `
      <span style="color: #10b981; font-weight: bold;">✔</span>
      <div>${escapeHtml(chk)}</div>
    `;
    elements.auditChecksContainer.appendChild(div);
  });

  (audit.issues || []).forEach((iss) => {
    const div = document.createElement("div");
    div.className = "compliance-check-item warn";
    div.innerHTML = `
      <span style="color: #f59e0b; font-weight: bold;">⚠</span>
      <div>
        <div style="font-weight: 600; color: #fbbf24;">[${iss.severity}] ${escapeHtml(iss.category)}</div>
        <div style="margin-top: 2px;">${escapeHtml(iss.message)}</div>
        <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Fix: ${escapeHtml(iss.action)}</div>
      </div>
    `;
    elements.auditChecksContainer.appendChild(div);
  });
}

function setupComplianceActions() {
  if (elements.runLatestAuditBtn) {
    elements.runLatestAuditBtn.addEventListener("click", () => {
      loadLatestCompliance();
    });
  }

  if (elements.runCustomAuditBtn) {
    elements.runCustomAuditBtn.addEventListener("click", async () => {
      const title = elements.testTitle.value.trim();
      const body = elements.testBody.value.trim();
      const hasDisclosure = elements.testAiDisclosure.checked;

      try {
        const resp = await fetch("/api/compliance/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: title,
            description: body,
            narration: body,
            tags: ["ai", "tutorial"],
            has_ai_disclosure: hasDisclosure
          })
        });
        const data = await resp.json();
        const audit = data.audit || {};

        if (elements.customAuditResults) {
          elements.customAuditResults.style.display = "block";
          elements.customAuditResults.innerHTML = `
            <div style="padding: 14px; border-radius: 8px; background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>Audit Score: ${audit.score}/100</strong>
                <span class="rpm-badge" style="${audit.score >= 90 ? 'color: #34d399;' : 'color: #f87171;'}">${audit.status}</span>
              </div>
              <div style="font-size: 0.78rem; color: var(--text-muted);">
                Passed Checks: ${audit.passed_checks ? audit.passed_checks.length : 0} | Issues: ${audit.issues ? audit.issues.length : 0}
              </div>
            </div>
          `;
        }
      } catch (err) {
        alert(`Audit failed: ${err}`);
      }
    });
  }

  // YouTube Upload button wiring
  if (elements.libUploadBtn) {
    elements.libUploadBtn.addEventListener("click", async () => {
      if (!AppState.selectedProjectId) {
        alert("Please select a completed video from the list first.");
        return;
      }
      const origText = elements.libUploadBtn.innerHTML;
      elements.libUploadBtn.disabled = true;
      elements.libUploadBtn.innerHTML = "⏳ Uploading to YouTube...";
      try {
        const resp = await fetch("/api/youtube/upload", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ project_id: AppState.selectedProjectId, privacy: "private" })
        });
        const data = await resp.json();
        if (data.status === "success" || data.video_id) {
          alert(`🎉 Successfully uploaded to YouTube! Video ID: ${data.video_id || "Done"}`);
        } else {
          alert(`Notice: ${data.message || data.error || "Review mode active. Check YouTube OAuth in config/client_secrets.json"}`);
        }
      } catch (e) {
        alert(`Upload error: ${e}`);
      } finally {
        elements.libUploadBtn.disabled = false;
        elements.libUploadBtn.innerHTML = origText;
      }
    });
  }
}

// -----------------------------------------------------------------------------
// 7. AI Model Advisor
// -----------------------------------------------------------------------------
async function loadModelAdvisor() {
  try {
    const resp = await fetch("/api/status");
    const data = await resp.json();
    const adv = data.advisor || {};

    const script = adv.script_engine || adv.scriptwriting || {};
    const voice = adv.voice_engine || adv.voiceover || {};
    const visual = adv.visual_engine || adv.visuals || {};
    const assembly = adv.assembly_engine || adv.video_assembly || {};

    elements.modelAdvisorContent.innerHTML = `
      <div class="card" style="margin-bottom: 12px; border-color: rgba(56, 189, 248, 0.3);">
        <div style="font-weight: 700; color: #38bdf8; font-size: 0.95rem; margin-bottom: 4px;">1. Scriptwriting Engine</div>
        <div style="font-size: 0.85rem; color: #fff; font-weight: 600;">${escapeHtml(script.selected_engine || "Procedural Masterclass")}</div>
        <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">${escapeHtml(script.rationale || "")}</div>
        <div style="font-size: 0.72rem; color: #34d399; margin-top: 4px;">Cost: ${escapeHtml(script.cost || "$0.00")} | Rating: ${escapeHtml(script.quality_rating || "")}</div>
      </div>

      <div class="card" style="margin-bottom: 12px; border-color: rgba(16, 185, 129, 0.3);">
        <div style="font-weight: 700; color: #34d399; font-size: 0.95rem; margin-bottom: 4px;">2. Voiceover & Speech Synthesis</div>
        <div style="font-size: 0.85rem; color: #fff; font-weight: 600;">${escapeHtml(voice.selected_engine || "macOS Studio Voice (Daniel)")}</div>
        <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">${escapeHtml(voice.rationale || "")}</div>
        <div style="font-size: 0.72rem; color: #34d399; margin-top: 4px;">Cost: ${escapeHtml(voice.cost || "$0.00")} | Rating: ${escapeHtml(voice.quality_rating || "")}</div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 700; color: #a78bfa; font-size: 0.95rem; margin-bottom: 4px;">3. Visual & Graphic Layout</div>
        <div style="font-size: 0.85rem; color: #fff; font-weight: 600;">${escapeHtml(visual.selected_engine || "")}</div>
        <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">${escapeHtml(visual.rationale || "")}</div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 700; color: #f59e0b; font-size: 0.95rem; margin-bottom: 4px;">4. Video Assembly Engine</div>
        <div style="font-size: 0.85rem; color: #fff; font-weight: 600;">${escapeHtml(assembly.engine || "FFmpeg 9.0.2")}</div>
        <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">Status: ${escapeHtml(assembly.status || "Active")} | ${escapeHtml(assembly.features || "")}</div>
      </div>
    `;
  } catch (err) {
    elements.modelAdvisorContent.innerHTML = `<div style="color: #f87171; font-size: 0.8rem;">Failed to load model advisor: ${err}</div>`;
  }
}

// -----------------------------------------------------------------------------
// 8. Clipboard Copy Helper
// -----------------------------------------------------------------------------
function setupCopyButtons() {
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const el = document.getElementById(targetId);
      if (el) {
        navigator.clipboard.writeText(el.value).then(() => {
          const original = btn.textContent;
          btn.textContent = "Copied!";
          btn.style.background = "#10b981";
          btn.style.color = "#fff";
          setTimeout(() => {
            btn.textContent = original;
            btn.style.background = "";
            btn.style.color = "";
          }, 1500);
        });
      }
    });
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// -----------------------------------------------------------------------------
// Application Initialization
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupBlueprintActions();
  setupPipelineLauncher();
  setupComplianceActions();
  setupCopyButtons();

  if (elements.refreshProjectsBtn) {
    elements.refreshProjectsBtn.addEventListener("click", () => loadProjectsList());
  }

  // Pre-load initial default blueprint
  renderBlueprint({
    tool_name: "Claude 3.7 Artifacts",
    suggested_title: "How to Build Full Apps with Claude 3.7 Artifacts (2026 Masterclass)",
    angle: "Complete Interactive React Prototyping with Extended Thinking",
    format: "Step-by-Step Hands-On Guide",
    potential_rpm: "$14 - $28",
    key_points: [
      "Dual-pane interactive React and Tailwind sandbox execution",
      "Using Claude Projects with design system knowledge",
      "Prompting with Hybrid Reasoning (Extended Thinking toggle)",
      "Exporting clean full-stack code directly to Vite & GitHub"
    ]
  });

  // Support direct hash tab routing (e.g. #library, #trends, #compliance)
  if (window.location.hash) {
    const hashTab = window.location.hash.replace("#", "");
    if (["studio", "library", "trends", "compliance", "advisor", "settings"].includes(hashTab)) {
      switchTab(hashTab);
    }
  }

  appendConsoleLog("READY", "Studio is ready! Enter an AI topic above or click 'Pick a Trending AI Tool' to start.");
});
