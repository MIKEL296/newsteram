// BLIXX Frontend Application

let currentPage = 1;
let currentSearchQuery = '';
let currentMovieId = null;
let previousSection = 'homeSection';

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
    loadMovies();
});

// ============= Navigation Functions =============

function showHome() {
    hideAllSections();
    document.getElementById('homeSection').style.display = 'block';
    previousSection = 'homeSection';
}

function showLogin() {
    hideAllSections();
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    previousSection = 'authSection';
}

function showRegister() {
    hideAllSections();
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    previousSection = 'authSection';
}

function showMovies() {
    if (!api.isAuthenticated()) {
        showLogin();
        return;
    }
    hideAllSections();
    currentPage = 1;
    currentSearchQuery = '';
    document.getElementById('moviesSection').style.display = 'block';
    document.getElementById('searchInput').value = '';
    loadMovies();
    previousSection = 'moviesSection';
}

function showTrending() {
    hideAllSections();
    document.getElementById('trendingSection').style.display = 'block';
    loadTrending();
    previousSection = 'trendingSection';
}

function showUpload() {
    if (!api.isAuthenticated()) {
        showLogin();
        return;
    }
    hideAllSections();
    document.getElementById('uploadSection').style.display = 'block';
    previousSection = 'uploadSection';
}

function showProfile() {
    if (!api.isAuthenticated()) {
        showLogin();
        return;
    }
    hideAllSections();
    document.getElementById('profileSection').style.display = 'block';
    loadProfile();
    previousSection = 'profileSection';
}

function hideAllSections() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.style.display = 'none');
}

function switchToLogin() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('regError').style.display = 'none';
}

function switchToRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('loginError').style.display = 'none';
}

function goBack() {
    if (currentMovieId) {
        currentMovieId = null;
        document.getElementById('playerSection').style.display = 'none';
        document.getElementById(previousSection).style.display = 'block';
    }
}

// ============= Authentication Functions =============

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');

    try {
        await api.login(username, password);
        errorDiv.style.display = 'none';
        updateAuthUI();
        showHome();
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    const errorDiv = document.getElementById('regError');

    if (password !== confirmPassword) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        await api.register(username, email, password);
        errorDiv.style.display = 'none';
        switchToLogin();
        document.getElementById('loginUsername').value = username;
        alert('Registration successful! Please log in.');
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

function logout() {
    api.logout();
    updateAuthUI();
    showHome();
}

function updateAuthUI() {
    const isAuth = api.isAuthenticated();
    const user = api.getStoredUser();

    document.getElementById('loginBtn').style.display = isAuth ? 'none' : 'block';
    document.getElementById('registerBtn').style.display = isAuth ? 'none' : 'block';
    document.getElementById('logoutBtn').style.display = isAuth ? 'block' : 'none';

    if (isAuth && user) {
        document.getElementById('profileLink').style.display = 'block';
        document.getElementById('username').textContent = user.username;
    } else {
        document.getElementById('profileLink').style.display = 'none';
    }
}

// ============= Movie Functions =============

async function loadMovies() {
    try {
        const data = await api.getMovies(currentPage, 12);
        displayMovies(data.movies);
    } catch (error) {
        console.error('Error loading movies:', error);
        document.getElementById('moviesList').innerHTML = `<p class="error">Error loading movies: ${error.message}</p>`;
    }
}

async function loadTrending() {
    try {
        const data = await api.getTrendingMovies('week', 1);
        displayMovies(data.results, 'trendingList');
    } catch (error) {
        console.error('Error loading trending:', error);
        document.getElementById('trendingList').innerHTML = `<p class="error">Error loading trending movies</p>`;
    }
}

function displayMovies(movies, containerId = 'moviesList') {
    const container = document.getElementById(containerId);

    if (!movies || movies.length === 0) {
        container.innerHTML = '<p>No movies found</p>';
        return;
    }

    container.innerHTML = movies.map(movie => `
        <div class="movie-card">
            <img src="${movie.poster_url || 'https://via.placeholder.com/200x300?text=No+Poster'}" 
                 alt="${movie.title}" class="movie-poster">
            <div class="movie-info">
                <h3>${movie.title}</h3>
                <p class="rating">⭐ ${movie.rating || 'N/A'}/10</p>
                <p class="views">${movie.view_count || 0} views</p>
                <button onclick="playMovie(${movie.id})" class="btn btn-primary">Watch</button>
            </div>
        </div>
    `).join('');
}

async function playMovie(movieId) {
    try {
        const movie = await api.getMovie(movieId);
        const streamData = await api.getStreamUrl(movieId);

        currentMovieId = movieId;

        // Set video player
        const videoPlayer = document.getElementById('videoPlayer');
        videoPlayer.src = streamData.stream_url;
        videoPlayer.onended = () => recordWatchComplete(movieId, movie.duration * 60);

        // Display movie details
        document.getElementById('playerTitle').textContent = movie.title;
        document.getElementById('playerDesc').textContent = movie.description || 'No description available';
        document.getElementById('playerDuration').textContent = movie.duration || 'Unknown';
        document.getElementById('playerRating').textContent = movie.rating || 'N/A';
        document.getElementById('playerGenre').textContent = movie.genre || 'Unknown';
        document.getElementById('playerViews').textContent = movie.view_count || 0;

        // Show player section
        hideAllSections();
        document.getElementById('playerSection').style.display = 'block';

        // Record watch progress every 10 seconds
        recordWatchInterval(movieId, movie.duration * 60);
    } catch (error) {
        alert('Error playing movie: ' + error.message);
    }
}

function recordWatchInterval(movieId, totalDuration) {
    const videoPlayer = document.getElementById('videoPlayer');

    setInterval(() => {
        if (!videoPlayer.paused && currentMovieId === movieId) {
            api.recordWatch(movieId, Math.floor(videoPlayer.currentTime), totalDuration);
        }
    }, 10000);
}

async function recordWatchComplete(movieId, totalDuration) {
    try {
        await api.recordWatch(movieId, totalDuration, totalDuration);
    } catch (error) {
        console.error('Error recording watch:', error);
    }
}

async function searchMovies() {
    const query = document.getElementById('searchInput').value;

    if (!query.trim()) {
        loadMovies();
        return;
    }

    try {
        const data = await api.searchMovies(query, 1, 12);
        displayMovies(data.movies || []);
    } catch (error) {
        console.error('Error searching movies:', error);
        document.getElementById('moviesList').innerHTML = `<p class="error">Error searching movies</p>`;
    }
}

// ============= Upload Functions =============

async function handleUpload(event) {
    event.preventDefault();

    const file = document.getElementById('movieFile').files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', document.getElementById('movieTitle').value);
    formData.append('description', document.getElementById('movieDesc').value);
    formData.append('genre', document.getElementById('movieGenre').value);
    formData.append('is_public', document.getElementById('moviePublic').checked);

    try {
        document.getElementById('uploadProgress').style.display = 'block';

        await api.uploadMovie(formData, (progress) => {
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = Math.round(progress) + '%';
        });

        alert('Movie uploaded successfully!');
        document.getElementById('uploadForm').reset();
        document.getElementById('uploadProgress').style.display = 'none';
        showProfile();
    } catch (error) {
        document.getElementById('uploadError').textContent = error.message;
        document.getElementById('uploadError').style.display = 'block';
    }
}

// ============= Profile Functions =============

async function loadProfile() {
    try {
        const user = api.getStoredUser();
        document.getElementById('profileUsername').textContent = user.username;
        document.getElementById('profileEmail').textContent = user.email;
        document.getElementById('profileJoined').textContent = new Date(user.created_at).toLocaleDateString();

        // Load user's movies
        const moviesData = await api.getUserMovies(1, 12);
        displayMovies(moviesData.movies, 'myMoviesList');

        // Load watch history
        const historyData = await api.getWatchHistory(1, 10);
        displayWatchHistory(historyData.watch_history);
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function displayWatchHistory(history) {
    const container = document.getElementById('watchHistoryList');

    if (!history || history.length === 0) {
        container.innerHTML = '<p>No watch history yet</p>';
        return;
    }

    container.innerHTML = history.map(entry => `
        <div class="watch-history-item">
            <p><strong>Movie ID:</strong> ${entry.movie_id}</p>
            <p><strong>Progress:</strong> ${entry.progress_percentage}%</p>
            <p><strong>Last Watched:</strong> ${new Date(entry.last_watched).toLocaleString()}</p>
            <p><strong>Status:</strong> ${entry.is_completed ? '✓ Completed' : 'In Progress'}</p>
        </div>
    `).join('');
}

// ============= Error Handling =============

window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});