import requests
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class TMDBService:
    """Service for TMDB API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
        self.image_base_url = 'https://image.tmdb.org/t/p/w500'
    
    def get_movie_details(self, tmdb_id):
        """Get movie details from TMDB"""
        try:
            url = f"{self.base_url}/movie/{tmdb_id}"
            params = {'api_key': self.api_key, 'language': 'en-US'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_movie_data(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching movie details from TMDB: {str(e)}")
            raise
    
    def search_movies(self, query, page=1):
        """Search for movies on TMDB"""
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': query,
                'page': page,
                'language': 'en-US'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'total_results': data.get('total_results', 0),
                'total_pages': data.get('total_pages', 0),
                'current_page': data.get('page', 1),
                'results': [self._format_movie_data(movie) for movie in data.get('results', [])]
            }
        except requests.RequestException as e:
            logger.error(f"Error searching movies on TMDB: {str(e)}")
            raise
    
    def get_trending_movies(self, time_window='week', page=1):
        """Get trending movies from TMDB"""
        try:
            url = f"{self.base_url}/trending/movie/{time_window}"
            params = {
                'api_key': self.api_key,
                'page': page,
                'language': 'en-US'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'total_results': data.get('total_results', 0),
                'total_pages': data.get('total_pages', 0),
                'current_page': data.get('page', 1),
                'results': [self._format_movie_data(movie) for movie in data.get('results', [])]
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching trending movies from TMDB: {str(e)}")
            raise
    
    def get_movies_by_genre(self, genre_id, page=1):
        """Get movies by genre from TMDB"""
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'with_genres': genre_id,
                'page': page,
                'language': 'en-US'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'total_results': data.get('total_results', 0),
                'total_pages': data.get('total_pages', 0),
                'current_page': data.get('page', 1),
                'results': [self._format_movie_data(movie) for movie in data.get('results', [])]
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching movies by genre from TMDB: {str(e)}")
            raise
    
    @lru_cache(maxsize=100)
    def get_genres(self):
        """Get list of movie genres from TMDB"""
        try:
            url = f"{self.base_url}/genre/movie/list"
            params = {'api_key': self.api_key, 'language': 'en-US'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('genres', [])
        except requests.RequestException as e:
            logger.error(f"Error fetching genres from TMDB: {str(e)}")
            raise
    
    @staticmethod
    def _format_movie_data(data):
        """Format movie data from TMDB response"""
        return {
            'tmdb_id': data.get('id'),
            'title': data.get('title'),
            'description': data.get('overview'),
            'release_date': data.get('release_date'),
            'rating': data.get('vote_average'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
            'backdrop_url': f"https://image.tmdb.org/t/p/w1280{data.get('backdrop_path')}" if data.get('backdrop_path') else None,
            'genre_ids': data.get('genre_ids', [])
        }
