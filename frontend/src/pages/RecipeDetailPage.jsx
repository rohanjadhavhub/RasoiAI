import { useState, useEffect, useRef } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate, useLocation } from 'react-router-dom';
import './RecipeDetailPage.css';
import {
    chat,
    addFavourite,
    removeFavourite,
    getFavouriteStatus,
    addBookmark,
    removeBookmark,
    getBookmarkStatus,
} from '../services/api';

function RecipeDetailPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const { recipe, sessionId } = location.state || {};

    const { isAuthenticated, getAccessTokenSilently } = useAuth0();
    const [chatInput, setChatInput] = useState('');
    const [chatMessages, setChatMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isFav, setIsFav] = useState(false);
    const [isBook, setIsBook] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);

    // Live recipe state — starts from the original recipe and can be updated by chat
    const [displayRecipe, setDisplayRecipe] = useState(recipe);
    const [isModified, setIsModified] = useState(false);

    const messagesEndRef = useRef(null);

    // Auto-scroll chat to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages, isLoading]);

    // Fetch favourite/bookmark status when recipe loads
    useEffect(() => {
        const fetchStatus = async () => {
            if (!isAuthenticated || !recipe) return;
            try {
                const token = await getAccessTokenSilently();
                const [favRes, bookRes] = await Promise.all([
                    getFavouriteStatus(token, recipe.recipe_id),
                    getBookmarkStatus(token, recipe.recipe_id),
                ]);
                setIsFav(favRes.is_favourite);
                setIsBook(bookRes.is_bookmark);
            } catch (err) {
                console.error('Failed to fetch status:', err);
            }
        };
        fetchStatus();
    }, [isAuthenticated, recipe, getAccessTokenSilently]);

    if (!recipe) {
        return (
            <div className="page">
                <div className="container">
                    <div className="empty-state">
                        <p>No recipe selected</p>
                        <button className="btn btn-primary" onClick={() => navigate('/recipes')}>
                            Back to Recipes
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const toggleFavourite = async () => {
        if (!isAuthenticated || actionLoading) return;
        setActionLoading(true);
        try {
            const token = await getAccessTokenSilently();
            if (isFav) {
                await removeFavourite(token, recipe.recipe_id);
            } else {
                await addFavourite(token, recipe.recipe_id, recipe.recipe);
            }
            setIsFav(!isFav);
        } catch (err) {
            console.error('Favourite toggle failed:', err);
        } finally {
            setActionLoading(false);
        }
    };

    const toggleBookmark = async () => {
        if (!isAuthenticated || actionLoading) return;
        setActionLoading(true);
        try {
            const token = await getAccessTokenSilently();
            if (isBook) {
                await removeBookmark(token, recipe.recipe_id);
            } else {
                await addBookmark(token, recipe.recipe_id, recipe.recipe);
            }
            setIsBook(!isBook);
        } catch (err) {
            console.error('Bookmark toggle failed:', err);
        } finally {
            setActionLoading(false);
        }
    };

    // Parse instructions into steps
    const parseInstructions = (instruction) => {
        if (!instruction) return [];
        let text = instruction.trim();
        text = text.replace(/(?:^|\n)\s*(?:step\s*)?\d+[.):\-]\s*/gi, '\n');
        let parts = text.split(/\n+/).map(s => s.trim()).filter(Boolean);
        if (parts.length <= 1) {
            parts = text.split(/\.\s+/).map(s => s.trim()).filter(Boolean);
        }
        return parts.map(s =>
            s.replace(/^[-•*>]+\s*/, '').replace(/\.$/, '').trim()
        ).filter(Boolean);
    };

    const steps = parseInstructions(displayRecipe.instruction);

    // ─── Gap Analysis: classify each ingredient ────────────────────
    const hasGapData = displayRecipe.have || displayRecipe.missing_critical || displayRecipe.missing_optional;

    const classifyIngredient = (rawIngredient) => {
        if (!hasGapData) return null; // no gap data → no highlighting

        // Normalize the raw ingredient the same way the backend does
        let norm = rawIngredient.toLowerCase().trim();
        norm = norm.replace(/\d+[\s]*(?:tsp|tbsp|cup|cups|kg|g|ml|l|pieces?|medium|small|large|inch)?[\s]*/g, '');
        norm = norm.replace(/(?:fresh|dried|chopped|sliced|diced|grated|minced|crushed|boiled|cooked|raw)\s*/g, '');
        norm = norm.replace(/\s*[-–]\s*.*$/, '');
        norm = norm.replace(/\s*\(.*\)/, '');
        norm = norm.trim();

        const matchesList = (list) =>
            list?.some(item => {
                const lo = item.toLowerCase();
                return lo === norm || lo.includes(norm) || norm.includes(lo);
            });

        if (matchesList(displayRecipe.have)) return 'have';
        if (matchesList(displayRecipe.missing_critical)) return 'missing';
        if (matchesList(displayRecipe.missing_optional)) return 'optional';
        return null; // assumed-available or unclassified
    };

    // Clean any residual markdown from chat text
    const cleanText = (text) => {
        return text
            .replace(/\*{1,3}(.*?)\*{1,3}/g, '$1')
            .replace(/^#{1,4}\s*/gm, '')
            .replace(/^[-•*]\s+/gm, '')
            .trim();
    };

    const handleChat = async () => {
        if (!chatInput.trim()) return;

        const userMessage = chatInput.trim();
        setChatInput('');
        setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            // Get auth token for persistent memory (if logged in)
            let token = null;
            if (isAuthenticated) {
                try {
                    token = await getAccessTokenSilently();
                } catch (e) {
                    // Not logged in or token expired — proceed without memory
                }
            }

            const response = await chat(sessionId || 'default', userMessage, displayRecipe, token);

            if (response.response_type === 'recipe_update' && response.updated_recipe) {
                // Merge updated recipe fields into displayRecipe
                setDisplayRecipe(prev => ({
                    ...prev,
                    ...response.updated_recipe,
                }));
                setIsModified(true);

                // Show a brief confirmation in chat
                setChatMessages(prev => [...prev, {
                    role: 'assistant',
                    content: response.response || "Done, updated the recipe for you.",
                }]);
            } else {
                // Regular chat response
                setChatMessages(prev => [...prev, {
                    role: 'assistant',
                    content: cleanText(response.response),
                }]);
            }
        } catch (err) {
            setChatMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestion = (suggestion) => {
        setChatInput(suggestion);
    };

    const resetRecipe = () => {
        setDisplayRecipe(recipe);
        setIsModified(false);
    };

    return (
        <div className="page recipe-detail-page">
            <div className="container">
                <button className="back-btn" onClick={() => navigate(-1)}>
                    ← Back to Recipes
                </button>

                <div className="recipe-detail-content">
                    {/* Recipe Info */}
                    <div className={`recipe-main fade-in ${isModified ? 'recipe-updated' : ''}`}>
                        <div className="recipe-header">
                            <div className="recipe-title-row">
                                <h1>{displayRecipe.recipe}</h1>
                                {isModified && (
                                    <span className="modified-badge">Modified</span>
                                )}
                            </div>
                            <div className="recipe-meta">
                                <span className="meta-item">
                                    ⏱️ {displayRecipe.cook_time || '~30 min'}
                                </span>
                                <span className="meta-item">
                                    🍽️ {displayRecipe.servings || '4 servings'}
                                </span>
                                <span className="meta-item">
                                    🌶️ {displayRecipe.spice_level || 'Medium'}
                                </span>
                            </div>

                            <div className="recipe-header-actions">
                                {isModified && (
                                    <button className="reset-btn" onClick={resetRecipe}>
                                        Reset to original
                                    </button>
                                )}

                                {isAuthenticated && (
                                    <div className="recipe-actions">
                                        <button
                                            className={`action-btn fav-btn ${isFav ? 'active' : ''}`}
                                            onClick={toggleFavourite}
                                            disabled={actionLoading}
                                            title={isFav ? 'Remove from favourites' : 'Add to favourites'}
                                        >
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill={isFav ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                                            </svg>
                                        </button>
                                        <button
                                            className={`action-btn book-btn ${isBook ? 'active' : ''}`}
                                            onClick={toggleBookmark}
                                            disabled={actionLoading}
                                            title={isBook ? 'Remove bookmark' : 'Save for later'}
                                        >
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill={isBook ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                                            </svg>
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Ingredients */}
                        <div className="recipe-section">
                            <h2>Ingredients</h2>

                            {/* Legend — only when gap data exists */}
                            {hasGapData && (
                                <div className="ingredient-legend">
                                    <span className="legend-item legend-have">Available</span>
                                    <span className="legend-item legend-missing">Missing</span>
                                    <span className="legend-item legend-optional">Optional</span>
                                </div>
                            )}

                            <div className="ingredients-list-detail">
                                {displayRecipe.ingredients.split(',').map((ing, i) => {
                                    const status = classifyIngredient(ing);
                                    return (
                                        <div
                                            key={i}
                                            className={`ingredient-item ${status ? `ingredient-${status}` : ''}`}
                                        >
                                            <span className="ingredient-bullet">•</span>
                                            <span>{ing.trim()}</span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Instructions */}
                        <div className="recipe-section">
                            <h2>Instructions</h2>
                            <div className="instructions-list">
                                {steps.length > 0 ? (
                                    steps.map((step, i) => (
                                        <div key={i} className="instruction-step">
                                            <span className="step-number">{i + 1}</span>
                                            <p>{step}</p>
                                        </div>
                                    ))
                                ) : (
                                    <p className="instruction-fallback">{displayRecipe.instruction}</p>
                                )}
                            </div>
                        </div>

                        {/* Tips */}
                        <div className="recipe-tips glass">
                            <h3>Pro Tips</h3>
                            <ul>
                                <li>Prep all ingredients before starting to cook</li>
                                <li>Adjust spice levels to your preference</li>
                                <li>Let the dish rest for 2-3 minutes before serving</li>
                            </ul>
                        </div>
                    </div>

                    {/* Chat Assistant — Annapurna */}
                    <div className="recipe-chat slide-up">
                        <div className="chat-header">
                            <div className="chat-header-identity">
                                <span className="annapurna-avatar">A</span>
                                <div>
                                    <h3>Annapurna</h3>
                                    <p>Your personal recipe chef</p>
                                </div>
                            </div>
                        </div>

                        <div className="chat-messages">
                            {chatMessages.length === 0 ? (
                                <div className="chat-welcome">
                                    <div className="welcome-avatar">A</div>
                                    <p className="welcome-text">I am Annapurna, your personal chef. Ask me anything about this recipe or tell me how you would like it changed.</p>
                                    <div className="chat-suggestions">
                                        <button onClick={() => handleSuggestion('Change the servings')}>
                                            Change servings
                                        </button>
                                        <button onClick={() => handleSuggestion('Make it less spicy')}>
                                            Adjust spice level
                                        </button>
                                        <button onClick={() => handleSuggestion('Suggest a substitution')}>
                                            Swap an ingredient
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                chatMessages.map((msg, i) => (
                                    <div key={i} className={`chat-message ${msg.role}`}>
                                        {msg.role === 'assistant' && (
                                            <span className="msg-avatar">A</span>
                                        )}
                                        <div className="message-content">
                                            {msg.content.split('\n').map((line, j) => (
                                                line.trim() ? <p key={j}>{line}</p> : null
                                            ))}
                                        </div>
                                    </div>
                                ))
                            )}
                            {isLoading && (
                                <div className="chat-message assistant">
                                    <div className="message-content typing">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="chat-input-group">
                            <input
                                id="chat-input"
                                type="text"
                                placeholder="Ask Annapurna anything..."
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                            />
                            <button
                                id="chat-send-btn"
                                className="btn btn-primary"
                                onClick={handleChat}
                                disabled={isLoading}
                            >
                                Send
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RecipeDetailPage;
