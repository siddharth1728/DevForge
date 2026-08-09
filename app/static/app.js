const API_BASE = '/api';

// --- State ---
let authToken = localStorage.getItem('devforge_token');
let currentUser = null;
let cachedAiInsights = null;

// --- Utilities ---
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    if (isError) {
        toast.classList.add('error');
    } else {
        toast.classList.remove('error');
    }
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function apiFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

        if (response.status === 401 && endpoint !== '/auth/login' && endpoint !== '/auth/register') {
            handleLogout();
            throw new Error("Authentication expired. Please log in again.");
        }

        const isJson = response.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await response.json() : null;

        if (!response.ok) {
            throw new Error((data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'API Error');
        }

        return data;
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        throw error;
    }
}

function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
}

function createLoader(text = "Loading...") {
    return `
        <div class="state-container">
            <div class="loader"></div>
            <p>${text}</p>
        </div>
    `;
}

function createEmptyState(title, subtitle = "") {
    return `
        <div class="empty-state">
            <h3>${title}</h3>
            <p>${subtitle}</p>
        </div>
    `;
}

// --- Routing & Navigation ---
function toggleAuth(view) {
    document.getElementById('login-container').style.display = view === 'login' ? 'block' : 'none';
    document.getElementById('register-container').style.display = view === 'register' ? 'block' : 'none';
}

function navigateTo(viewId) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    document.getElementById('auth-view').style.display = 'none';
    
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    
    if (viewId === 'login' || viewId === 'register') {
        document.getElementById('app-layout').style.display = 'none';
        document.getElementById('auth-view').style.display = 'flex';
        toggleAuth(viewId);
    } else {
        document.getElementById('app-layout').style.display = 'flex';
        document.getElementById(`${viewId}-view`).classList.add('active');
        
        const navLink = document.querySelector(`.nav-link[onclick="navigateTo('${viewId}')"]`);
        if(navLink) navLink.classList.add('active');
        
        // Update topbar title
        const titles = {
            'dashboard': 'Overview',
            'projects': 'Projects',
            'github': 'GitHub',
            'ai': 'AI Portfolio Insights',
            'profile': 'Profile'
        };
        document.getElementById('topbar-title').textContent = titles[viewId] || 'DevForge';

        if (viewId === 'dashboard') renderDashboard();
        if (viewId === 'projects') renderProjects();
        if (viewId === 'github') renderGithub();
        if (viewId === 'profile') renderProfile();
        if (viewId === 'ai') renderAIView();
    }
}

function initApp() {
    if (authToken) {
        apiFetch('/auth/me')
            .then(user => {
                currentUser = user;
                // Update sidebar user profile
                document.getElementById('user-avatar').textContent = user.full_name.charAt(0).toUpperCase();
                document.getElementById('user-name').textContent = user.full_name;
                document.getElementById('github-subtitle').textContent = user.github_username ? `@${user.github_username}` : 'Not connected';
                
                navigateTo('dashboard');
            })
            .catch(() => handleLogout());
    } else {
        navigateTo('login');
    }
}

// --- Authentication Logic ---
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errEl = document.getElementById('login-error');
    errEl.style.display = 'none';

    try {
        const data = await apiFetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        authToken = data.access_token;
        localStorage.setItem('devforge_token', authToken);
        showToast("Signed in successfully");
        initApp();
    } catch (error) {
        errEl.textContent = error.message;
        errEl.style.display = 'block';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const github = document.getElementById('reg-github').value;
    const errEl = document.getElementById('reg-error');
    errEl.style.display = 'none';

    try {
        await apiFetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                email, password, full_name: name, github_username: github || null
            })
        });
        showToast("Registration complete. Please sign in.");
        toggleAuth('login');
    } catch (error) {
        errEl.textContent = error.message;
        errEl.style.display = 'block';
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    cachedAiInsights = null;
    localStorage.removeItem('devforge_token');
    navigateTo('login');
}

// --- Dashboard Rendering ---
async function renderDashboard() {
    document.getElementById('greeting-title').textContent = `${getGreeting()}, ${currentUser.full_name.split(' ')[0]}`;
    const snapshotContainer = document.getElementById('dashboard-snapshot');
    const recentProjectsContainer = document.getElementById('dashboard-recent-projects');
    const nextActionContainer = document.getElementById('dashboard-next-action');
    
    snapshotContainer.innerHTML = createLoader("Aggregating signals...");
    
    try {
        const stats = await apiFetch('/dashboard/stats');
        
        // Calculate dynamic skill bars based on tech presence in projects
        const langs = stats.top_languages || [];
        let signalsHtml = '';
        if (langs.length === 0) {
            signalsHtml = '<p class="text-secondary" style="font-size: 0.85rem;">No technical signals detected yet.</p>';
        } else {
            signalsHtml = '<div class="skill-list">';
            langs.forEach((lang, index) => {
                signalsHtml += `
                    <div class="skill-item" style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                        <div class="skill-name" style="font-weight: 500;">${lang}</div>
                        <div class="skill-level" style="color: var(--text-secondary); font-size: 0.85rem;">Active in workspace</div>
                    </div>
                `;
            });
            signalsHtml += '</div>';
        }

        let gapsHtml = '';
        let readinessScore = 'N/A';
        let readinessLabel = 'Not analyzed';
        let readinessSub = 'Run analysis to compute';
        
        if (cachedAiInsights) {
            readinessScore = cachedAiInsights.portfolio_score;
            readinessLabel = cachedAiInsights.portfolio_score >= 80 ? 'Strong foundation' : 'Developing';
            readinessSub = 'Based on AI analysis';
            
            gapsHtml = '<div class="skill-list">';
            (cachedAiInsights.missing_skills || []).slice(0, 3).forEach(gap => {
                gapsHtml += `<div class="gap-item">${gap}</div>`;
            });
            gapsHtml += '</div>';
            
            const actionRec = (cachedAiInsights.recommendations && cachedAiInsights.recommendations.length > 0) 
                ? cachedAiInsights.recommendations[0] 
                : 'Keep building your projects.';
                
            nextActionContainer.innerHTML = `
                <h4>${actionRec}</h4>
                <p>Based on your latest portfolio analysis.</p>
                <button class="btn btn-secondary mt-1" onclick="navigateTo('ai')">View Details →</button>
            `;
        } else {
            gapsHtml = '<p class="text-secondary" style="font-size: 0.85rem;">Portfolio not analyzed yet.</p>';
            nextActionContainer.innerHTML = `
                <h4>Analyze Portfolio</h4>
                <p>Get AI-driven insights on your current projects and GitHub activity to identify skill gaps and compute readiness.</p>
                <button class="btn btn-secondary mt-1" onclick="navigateTo('ai')">Run Analysis →</button>
            `;
        }

        snapshotContainer.innerHTML = `
            <div class="snapshot-card">
                <div class="snapshot-card-title">PORTFOLIO READINESS</div>
                <div class="score-display">
                    <div class="score-value">${readinessScore}</div>
                    ${readinessScore !== 'N/A' ? '<div class="score-max">/ 100</div>' : ''}
                </div>
                <div class="score-label" style="color: ${readinessScore !== 'N/A' ? 'var(--text-primary)' : 'var(--text-secondary)'}">${readinessLabel}</div>
                <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">${readinessSub}</p>
            </div>
            <div class="snapshot-card">
                <div class="snapshot-card-title">YOUR STRONGEST SIGNALS</div>
                ${signalsHtml}
            </div>
            <div class="snapshot-card">
                <div class="snapshot-card-title">EVIDENCE GAPS</div>
                ${gapsHtml}
            </div>
        `;

        // Fetch recent projects
        const projects = await apiFetch('/projects/');
        const recent = projects.slice(0, 3);
        
        if (recent.length === 0) {
            recentProjectsContainer.innerHTML = `<div class="list-row"><p class="text-secondary" style="font-size:0.85rem;">No projects added yet.</p></div>`;
        } else {
            recentProjectsContainer.innerHTML = `
                ${recent.map(p => `
                    <div class="list-row" style="padding: 1rem;">
                        <div class="list-col-main">
                            <h4 style="font-size: 0.95rem;">${p.title}</h4>
                            <div style="margin-top: 0.25rem;">
                                <span style="font-size: 0.75rem; color: var(--text-secondary);">${p.tech_stack}</span>
                            </div>
                        </div>
                        <div class="list-col-actions">
                            <span class="status-badge ${p.status}">${p.status === 'completed' ? 'Completed' : 'Active'}</span>
                        </div>
                    </div>
                `).join('')}
            `;
        }

    } catch (error) {
        snapshotContainer.innerHTML = `<div class="error-message" style="display:block;">Failed to load dashboard: ${error.message}</div>`;
    }
}

// --- Projects Rendering ---
async function renderProjects() {
    const container = document.getElementById('projects-list-container');
    container.innerHTML = createLoader("Loading workspace projects...");
    
    try {
        const projects = await apiFetch('/projects/');
        
        if (projects.length === 0) {
            container.innerHTML = createEmptyState("No projects yet", "Add your first project to start building your developer profile.");
            return;
        }

        container.innerHTML = projects.map(p => `
            <div class="list-row">
                <div class="list-col-main">
                    <h4>${p.title}</h4>
                    <p>${p.description || 'No description provided.'}</p>
                    <div style="margin-top: 0.75rem;">
                        ${p.tech_stack.split(',').map(t => `<span class="tech-tag">${t.trim()}</span>`).join('')}
                    </div>
                </div>
                <div class="list-col-actions" style="flex-direction: column; align-items: flex-end; justify-content: space-between; gap: 1rem;">
                    <span class="status-badge ${p.status}">${p.status === 'completed' ? 'Completed' : 'In Progress'}</span>
                    <div>
                        ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="action-link">GitHub</a>` : ''}
                        ${p.live_url ? `<a href="${p.live_url}" target="_blank" class="action-link">Live</a>` : ''}
                        <a class="action-link" style="cursor:pointer;" onclick='openProjectModal(${JSON.stringify(p)})'>Edit</a>
                        <a class="action-link" style="cursor:pointer; color: var(--danger-text);" onclick="deleteProject(${p.id})">Delete</a>
                    </div>
                </div>
            </div>
        `).join('');

    } catch (error) {
        container.innerHTML = `<div class="error-message" style="display:block;">Error loading projects: ${error.message}</div>`;
    }
}

// Project Modal State
let editProjectId = null;

function openProjectModal(project = null) {
    const modal = document.getElementById('project-modal');
    document.getElementById('project-form').reset();
    document.getElementById('proj-error').style.display = 'none';
    
    if (project) {
        editProjectId = project.id;
        document.getElementById('modal-title').textContent = 'Edit Project';
        document.getElementById('proj-title').value = project.title;
        document.getElementById('proj-desc').value = project.description || '';
        document.getElementById('proj-tech').value = project.tech_stack;
        document.getElementById('proj-github').value = project.github_url || '';
        document.getElementById('proj-live').value = project.live_url || '';
        document.getElementById('proj-status').value = project.status;
    } else {
        editProjectId = null;
        document.getElementById('modal-title').textContent = 'Add Project';
    }
    
    modal.style.display = 'flex';
}

function closeProjectModal() {
    document.getElementById('project-modal').style.display = 'none';
}

async function handleProjectSubmit(e) {
    e.preventDefault();
    const errEl = document.getElementById('proj-error');
    errEl.style.display = 'none';

    const payload = {
        title: document.getElementById('proj-title').value,
        tech_stack: document.getElementById('proj-tech').value,
        description: document.getElementById('proj-desc').value || null,
        github_url: document.getElementById('proj-github').value || null,
        live_url: document.getElementById('proj-live').value || null,
        status: document.getElementById('proj-status').value
    };

    try {
        if (editProjectId) {
            await apiFetch(`/projects/${editProjectId}`, { method: 'PUT', body: JSON.stringify(payload) });
            showToast("Project updated");
        } else {
            await apiFetch('/projects/', { method: 'POST', body: JSON.stringify(payload) });
            showToast("Project created");
        }
        closeProjectModal();
        renderProjects();
        if (document.getElementById('dashboard-view').classList.contains('active')) renderDashboard();
    } catch (error) {
        errEl.textContent = error.message;
        errEl.style.display = 'block';
    }
}

async function deleteProject(id) {
    if (!confirm("Delete this project? This cannot be undone.")) return;
    try {
        await apiFetch(`/projects/${id}`, { method: 'DELETE' });
        showToast("Project deleted");
        renderProjects();
    } catch (error) {
        showToast(error.message, true);
    }
}

// --- GitHub Rendering ---
async function renderGithub() {
    const container = document.getElementById('github-content');
    container.innerHTML = createLoader("Fetching repository analytics...");
    
    try {
        const stats = await apiFetch('/github/user-stats');
        
        const languages = stats.languages || {};
        let totalBytes = 0;
        const colorMap = { 'Python': '#3572A5', 'JavaScript': '#f1e05a', 'TypeScript': '#3178c6', 'HTML': '#e34c26', 'CSS': '#563d7c', 'Java': '#b07219', 'Go': '#00ADD8' };
        
        for (const bytes of Object.values(languages)) {
            totalBytes += bytes;
        }

        let langBarHtml = '';
        let langLegendHtml = '';
        
        if (totalBytes > 0) {
            for (const [lang, bytes] of Object.entries(languages)) {
                const percentage = (bytes / totalBytes) * 100;
                const color = colorMap[lang] || '#8b949e';
                langBarHtml += `<div class="lang-segment" style="width: ${percentage}%; background-color: ${color};" title="${lang}"></div>`;
                langLegendHtml += `<div class="lang-legend-item"><div class="lang-dot" style="background-color: ${color};"></div>${lang} <span style="opacity:0.5">${percentage.toFixed(1)}%</span></div>`;
            }
        }

        const reposHtml = (stats.repos || []).map(r => `
            <div class="list-row" style="padding: 1rem;">
                <div class="list-col-main">
                    <h4><a href="${r.url}" target="_blank" style="color: var(--text-primary); text-decoration: none;">${r.name}</a></h4>
                    <p style="font-size: 0.75rem; margin-top: 0.25rem;">Updated recently</p>
                </div>
                <div class="list-col-actions" style="gap: 1.5rem; color: var(--text-secondary); font-size: 0.8rem;">
                    <span>${r.language || 'Unknown'}</span>
                    <span>★ ${r.stars}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="metrics-row" style="margin-bottom: 1.5rem;">
                <div class="metric-item">
                    <div class="metric-label">Repositories</div>
                    <div class="metric-value">${stats.total_repos}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Stars</div>
                    <div class="metric-value">${stats.total_stars}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Primary Language</div>
                    <div class="metric-value highlight">${Object.keys(languages)[0] || 'N/A'}</div>
                </div>
            </div>
            
            <h3 class="section-label">ESTIMATED LANGUAGE DISTRIBUTION</h3>
            ${totalBytes > 0 ? `
                <div class="lang-distribution-bar">${langBarHtml}</div>
                <div class="lang-legend">${langLegendHtml}</div>
            ` : '<p class="text-secondary" style="margin-bottom: 2rem;">No language data available.</p>'}
            
            <h3 class="section-label">REPOSITORIES</h3>
            <div class="list-container dense-list">${reposHtml || '<div class="list-row"><p class="text-secondary">No public repositories found.</p></div>'}</div>
            
            <div style="margin-top: 2rem; text-align: center;">
                <button class="btn btn-secondary" onclick="renderGithub()">Refresh GitHub Data</button>
            </div>
        `;
    } catch (error) {
        container.innerHTML = createEmptyState("GitHub Data Unavailable", error.message);
    }
}

// --- AI Rendering ---
function renderAIView() {
    if (cachedAiInsights) {
        showAIResults(cachedAiInsights);
    } else {
        const container = document.getElementById('ai-content');
        container.innerHTML = `
            <div class="empty-state">
                <h3 style="margin-bottom: 1rem;">PORTFOLIO NOT ANALYZED</h3>
                <p style="max-width: 400px; margin: 0 auto 2rem;">Run an analysis to understand your current strengths, evidence gaps, and improvement opportunities based on your DevForge projects.</p>
                <button class="btn btn-primary" onclick="runAIAnalysis()">Analyze Portfolio</button>
            </div>
        `;
    }
}

async function runAIAnalysis() {
    const container = document.getElementById('ai-content');
    
    // 2D sequence UI
    container.innerHTML = `
        <div class="ai-sequence">
            <div class="sequence-step active" id="step-1"><div class="step-icon"><div class="spinner"></div></div> <span>Analyzing Projects</span></div>
            <div class="sequence-step" id="step-2"><div class="step-icon">○</div> <span>Processing GitHub Activity</span></div>
            <div class="sequence-step" id="step-3"><div class="step-icon">○</div> <span>Extracting Technical Evidence</span></div>
            <div class="sequence-step" id="step-4"><div class="step-icon">○</div> <span>Generating Insights</span></div>
        </div>
    `;
    
    // Fake sequence timing for UX
    const setStep = (id, text, isDone) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (isDone) {
            el.className = 'sequence-step completed';
            el.querySelector('.step-icon').innerHTML = '✓';
        } else {
            el.className = 'sequence-step active';
            el.querySelector('.step-icon').innerHTML = '<div class="spinner"></div>';
        }
    };

    setTimeout(() => { setStep('step-1', null, true); setStep('step-2', null, false); }, 1200);
    setTimeout(() => { setStep('step-2', null, true); setStep('step-3', null, false); }, 2400);
    setTimeout(() => { setStep('step-3', null, true); setStep('step-4', null, false); }, 3800);
    
    try {
        const insights = await apiFetch('/ai/resume-insights');
        cachedAiInsights = insights; // store for dashboard
        
        // Let the last animation finish visually before snapping to results
        setTimeout(() => {
            showAIResults(insights);
        }, 5000);
        
    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                <h3 style="color: var(--danger-text)">Analysis Failed</h3>
                <p style="margin-bottom: 1.5rem;">${error.message}</p>
                <button class="btn btn-primary" onclick="renderAIView()">Try Again</button>
            </div>
        `;
    }
}

function showAIResults(insights) {
    const container = document.getElementById('ai-content');
    const renderList = (arr, isGap = false) => arr.map(i => `<div class="gap-item" style="${isGap ? 'color: var(--text-secondary);' : ''}">${i}</div>`).join('');
    
    container.innerHTML = `
        <div class="snapshot-card" style="align-items: center; text-align: center; max-width: 400px; margin: 0 auto 3rem;">
            <div class="snapshot-card-title">PORTFOLIO READINESS</div>
            <div class="score-display">
                <div class="score-value">${insights.portfolio_score}</div>
                <div class="score-max">/ 100</div>
            </div>
            <div class="score-label" style="font-size: 1.1rem; margin-top: 0.5rem;">${insights.portfolio_score >= 80 ? 'Strong foundation' : 'Developing'}</div>
        </div>
        
        <div class="split-layout" style="margin-bottom: 3rem;">
            <div class="split-left">
                <h3 class="section-label" style="color: var(--text-title);">YOUR STRENGTHS</h3>
                <div class="skill-list" style="margin-top: 1rem;">
                    ${renderList(insights.strengths)}
                </div>
            </div>
            <div class="split-right">
                <h3 class="section-label">EVIDENCE GAPS</h3>
                <div class="skill-list" style="margin-top: 1rem;">
                    ${renderList(insights.missing_skills, true)}
                </div>
            </div>
        </div>
        
        <div class="split-layout">
            <div class="split-left">
                <h3 class="section-label">RECOMMENDATIONS</h3>
                <div class="skill-list" style="margin-top: 1rem;">
                    ${insights.recommendations.map((r, i) => `<div style="margin-bottom: 1rem; color: var(--text-secondary);"><strong style="color: var(--text-primary);">${i+1}.</strong> ${r}</div>`).join('')}
                </div>
            </div>
            <div class="split-right">
                <h3 class="section-label">NEXT BEST ACTION</h3>
                <div class="content-panel highlight-panel">
                    <h4 style="font-size: 1.1rem; line-height: 1.4; margin-bottom: 1rem;">${insights.recommendations[0] || 'Continue building.'}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.85rem;">Why? Addressing this gap provides the highest impact to your portfolio readiness based on your current demonstrated skills.</p>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 4rem; text-align: center;">
            <button class="btn btn-secondary" onclick="cachedAiInsights = null; runAIAnalysis()">Re-run Analysis</button>
        </div>
    `;
}

// --- Profile Rendering ---
async function renderProfile() {
    const container = document.getElementById('profile-content');
    container.innerHTML = createLoader("Loading profile...");
    
    try {
        const user = await apiFetch('/auth/me');
        container.innerHTML = `
            <form id="profile-form" class="list-container dense-list" style="max-width: 600px;" onsubmit="handleProfileUpdate(event)">
                <div id="profile-error" class="error-message"></div>
                <div class="list-row">
                    <div class="list-col-main" style="width: 100%;">
                        <label for="profile-name">Name</label>
                        <input type="text" id="profile-name" class="input-field" value="${user.full_name}" required style="width: 100%; margin-top: 0.5rem;">
                    </div>
                </div>
                <div class="list-row">
                    <div class="list-col-main" style="width: 100%;">
                        <label>Email Address (Cannot be changed)</label>
                        <input type="email" class="input-field" value="${user.email}" disabled style="width: 100%; margin-top: 0.5rem; opacity: 0.7; cursor: not-allowed;">
                    </div>
                </div>
                <div class="list-row">
                    <div class="list-col-main" style="width: 100%;">
                        <label for="profile-github">GitHub Username</label>
                        <input type="text" id="profile-github" class="input-field" value="${user.github_username || ''}" style="width: 100%; margin-top: 0.5rem;">
                    </div>
                </div>
                <div class="list-row">
                    <div class="list-col-main">
                        <label>Member Since</label>
                        <p style="margin-top: 0.5rem;">${new Date(user.created_at).toLocaleDateString()}</p>
                    </div>
                </div>
                <div style="margin-top: 1.5rem; display: flex; justify-content: flex-end;">
                    <button type="submit" class="btn btn-primary" id="profile-save-btn">Save Changes</button>
                </div>
            </form>
        `;
    } catch (error) {
        container.innerHTML = createEmptyState("Error", error.message);
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    const btn = document.getElementById('profile-save-btn');
    const errEl = document.getElementById('profile-error');
    errEl.style.display = 'none';
    btn.textContent = 'Saving...';
    btn.disabled = true;

    const payload = {
        full_name: document.getElementById('profile-name').value,
        github_username: document.getElementById('profile-github').value || null
    };

    try {
        const updatedUser = await apiFetch('/auth/me', { method: 'PUT', body: JSON.stringify(payload) });
        currentUser = updatedUser;
        document.getElementById('user-avatar').textContent = updatedUser.full_name.charAt(0).toUpperCase();
        document.getElementById('user-name').textContent = updatedUser.full_name;
        document.getElementById('github-subtitle').textContent = updatedUser.github_username ? `@${updatedUser.github_username}` : 'Not connected';
        showToast("Profile updated successfully");
    } catch (error) {
        errEl.textContent = error.message;
        errEl.style.display = 'block';
    } finally {
        btn.textContent = 'Save Changes';
        btn.disabled = false;
    }
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('project-form').addEventListener('submit', handleProjectSubmit);
    
    document.getElementById('project-modal').addEventListener('click', (e) => {
        if(e.target.id === 'project-modal') closeProjectModal();
    });
    
    initApp();
});
