/**
 * API Service for RasoiAI Backend
 */

const API_BASE = 'http://localhost:8000/api';
const RPI_CAMERA_BASE = 'http://172.31.185.50:8001/api/camera';


/**
 * Trigger RPi camera scan → Gemini Vision → forward to main app for recipes.
 * Returns { success, image_path, ingredients_detected, analysis_details, recipes }
 */
export async function remoteScan() {
    const response = await fetch(`${RPI_CAMERA_BASE}/scan-and-forward`, {
        method: 'POST',
    });

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Remote scan failed');
    }

    return response.json();
}

/**
 * Get the latest captured image URL from the RPi camera.
 */
export function getRpiImageUrl() {
    return `${RPI_CAMERA_BASE}/latest-image?t=${Date.now()}`;
}

/**
 * Upload images for ingredient analysis
 */
export async function uploadImages(files) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    const response = await fetch(`${API_BASE}/upload-images`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('Failed to upload images');
    }

    return response.json();
}

/**
 * Analyze uploaded images for ingredients
 */
export async function analyzeIngredients(sessionId) {
    const response = await fetch(`${API_BASE}/analyze-ingredients?session_id=${sessionId}`, {
        method: 'POST',
    });

    if (!response.ok) {
        throw new Error('Failed to analyze ingredients');
    }

    return response.json();
}

/**
 * Confirm ingredients and preferences
 */
export async function confirmIngredients(sessionId, ingredients, preferences = null) {
    const response = await fetch(`${API_BASE}/confirm-ingredients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            confirmed_ingredients: ingredients,
            preferences: preferences,
        }),
    });

    if (!response.ok) {
        throw new Error('Failed to confirm ingredients');
    }

    return response.json();
}

/**
 * Get recipe recommendations
 */
export async function getRecommendations(sessionId) {
    const response = await fetch(`${API_BASE}/get-recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
        throw new Error('Failed to get recommendations');
    }

    return response.json();
}

/**
 * Get recipe by ID
 */
export async function getRecipe(recipeId) {
    const response = await fetch(`${API_BASE}/recipe/${recipeId}`);

    if (!response.ok) {
        throw new Error('Failed to get recipe');
    }

    return response.json();
}

/**
 * Search recipes by ingredients
 */
export async function searchRecipes(ingredients) {
    const ingredientStr = ingredients.join(',');
    const response = await fetch(`${API_BASE}/recipes/search?ingredients=${encodeURIComponent(ingredientStr)}`);

    if (!response.ok) {
        throw new Error('Failed to search recipes');
    }

    return response.json();
}

/**
 * Helper for authenticated fetch requests
 */
async function authFetch(url, token, options = {}) {
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    };

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        if (response.status === 401) {
            throw new Error('Unauthorized - please login again');
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'API request failed');
    }

    return response.json();
}

/**
 * Fetch or create user profile in backend
 */
export async function fetchUserProfile(token) {
    return authFetch(`${API_BASE}/auth/me`, token);
}

/**
 * Chat with AI assistant
 * @param {string} sessionId
 * @param {string} message
 * @param {object|null} recipeContext
 * @param {string|null} token - Auth0 access token (optional, enables memory)
 */
export async function chat(sessionId, message, recipeContext = null, token = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            session_id: sessionId,
            message: message,
            recipe_context: recipeContext,
        }),
    });

    if (!response.ok) {
        throw new Error('Failed to get chat response');
    }

    return response.json();
}


// ─── Favourites ──────────────────────────────────────────

export async function addFavourite(token, recipeId, recipeName) {
    return authFetch(`${API_BASE}/favourites`, token, {
        method: 'POST',
        body: JSON.stringify({ recipe_id: recipeId, recipe_name: recipeName }),
    });
}

export async function removeFavourite(token, recipeId) {
    return authFetch(`${API_BASE}/favourites/${recipeId}`, token, {
        method: 'DELETE',
    });
}

export async function getFavourites(token) {
    return authFetch(`${API_BASE}/favourites`, token);
}

export async function getFavouriteStatus(token, recipeId) {
    return authFetch(`${API_BASE}/favourites/${recipeId}/status`, token);
}


// ─── Bookmarks ───────────────────────────────────────────

export async function addBookmark(token, recipeId, recipeName) {
    return authFetch(`${API_BASE}/bookmarks`, token, {
        method: 'POST',
        body: JSON.stringify({ recipe_id: recipeId, recipe_name: recipeName }),
    });
}

export async function removeBookmark(token, recipeId) {
    return authFetch(`${API_BASE}/bookmarks/${recipeId}`, token, {
        method: 'DELETE',
    });
}

export async function getBookmarks(token) {
    return authFetch(`${API_BASE}/bookmarks`, token);
}

export async function getBookmarkStatus(token, recipeId) {
    return authFetch(`${API_BASE}/bookmarks/${recipeId}/status`, token);
}
