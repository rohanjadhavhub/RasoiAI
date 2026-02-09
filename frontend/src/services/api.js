/**
 * API Service for RasoiAI Backend
 */

const API_BASE = 'http://localhost:8000/api';

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
 * Chat with AI assistant
 */
export async function chat(sessionId, message, recipeContext = null) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
