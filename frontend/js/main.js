// File: frontend/js/main.js
// Description: Main Frontend Logic

async function fetchVideos() {
    // In a real scenario, this would hit a feed endpoint
    // Currently hitting a hypothetical endpoint
    try {
        const response = await fetch('/api/v1/videos/feed'); 
        if (!response.ok) return;
        const videos = await response.json();
        
        const grid = document.getElementById('video-grid');
        grid.innerHTML = videos.map(v => `
            <div class="video-card" onclick="window.location.href='/watch.html?v=${v.id}'">
                <div class="video-thumbnail"></div> <div style="padding: 10px">
                    <h3>${v.title}</h3>
                    <p>${v.views} views</p>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error("Failed to load videos");
    }
}

// Check auth
const token = localStorage.getItem('access_token');
if (token) {
    document.getElementById('auth-section').innerHTML = `<button onclick="logout()">Logout</button>`;
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.reload();
}

// Note: Feed endpoint logic wasn't explicitly requested in backend but is implied for index.