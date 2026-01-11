// API Client for BLIXX Backend

class APIClient {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
        this.accessToken = localStorage.getItem('accessToken');
        this.refreshToken = localStorage.getItem('refreshToken');
    }

    // Helper method to make API calls
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            ...options.headers,
        };

        // Add JWT token if available
        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle token expiration
            if (response.status === 401) {
                if (await this.refreshAccessToken()) {
                    // Retry the request with new token
                    return this.request(endpoint, options);
                } else {
                    this.logout();
                    throw new Error('Authentication failed');
                }
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication Methods
    async register(username, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
    }

    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        // Save tokens
        this.accessToken = data.access_token;
        this.refreshToken = data.refresh_token;
        localStorage.setItem('accessToken', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        return data;
    }

    async refreshAccessToken() {
        try {
            if (!this.refreshToken) return false;

            const data = await this.request('/auth/refresh', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.refreshToken}` }
            });

            this.accessToken = data.access_token;
            localStorage.setItem('accessToken', data.access_token);
            return true;
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    }

    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
    }

    // User Methods
    async getCurrentUser() {
        return this.request('/users/me');
    }

    async updateProfile(data) {
        return this.request('/users/me', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    async getUserProfile(userId) {
        return this.request(`/users/${userId}`);
    }

    // Movie Methods
    async getMovies(page = 1, perPage = 20) {
        return this.request(`/movies?page=${page}&per_page=${perPage}`);
    }

    async getMovie(movieId) {
        return this.request(`/movies/${movieId}`);
    }

    async searchMovies(query, page = 1, perPage = 20) {
        return this.request(`/movies/search?q=${query}&page=${page}&per_page=${perPage}`);
    }

    async getFeaturedMovies(page = 1, perPage = 20) {
        return this.request(`/movies/featured?page=${page}&per_page=${perPage}`);
    }

    async uploadMovie(formData, onProgress) {
        const url = `${this.baseUrl}/movies/upload`;
        const headers = {};

        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Track upload progress
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(new Error(JSON.parse(xhr.responseText).error));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });

            xhr.addEventListener('abort', () => {
                reject(new Error('Upload aborted'));
            });

            xhr.open('POST', url);
            for (const [key, value] of Object.entries(headers)) {
                xhr.setRequestHeader(key, value);
            }

            xhr.send(formData);
        });
    }

    async updateMovie(movieId, data) {
        return this.request(`/movies/${movieId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    async deleteMovie(movieId) {
        return this.request(`/movies/${movieId}`, {
            method: 'DELETE'
        });
    }

    async getUserMovies(page = 1, perPage = 20) {
        return this.request(`/users/me/movies?page=${page}&per_page=${perPage}`);
    }

    // Streaming Methods
    async getStreamUrl(movieId) {
        return this.request(`/stream/${movieId}/url`);
    }

    async recordWatch(movieId, watchTime, totalDuration) {
        return this.request(`/stream/${movieId}/watch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ watch_time: watchTime, total_duration: totalDuration })
        });
    }

    async getWatchHistory(page = 1, perPage = 20) {
        return this.request(`/stream/history?page=${page}&per_page=${perPage}`);
    }

    // TMDB Methods
    async searchTMDB(query, page = 1) {
        return this.request(`/movies/tmdb/search?q=${query}&page=${page}`);
    }

    async getTrendingMovies(timeWindow = 'week', page = 1) {
        return this.request(`/movies/tmdb/trending?time_window=${timeWindow}&page=${page}`);
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.accessToken;
    }

    // Get stored user
    getStoredUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
}

// Create global API client instance
const api = new APIClient();