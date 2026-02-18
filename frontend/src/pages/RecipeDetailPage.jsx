import { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
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

function RecipeDetailPage({ recipe, sessionId, onNavigate }) {
    const { isAuthenticated, getAccessTokenSilently } = useAuth0();
    const [chatInput, setChatInput] = useState('');
    const [chatMessages, setChatMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isFav, setIsFav] = useState(false);
    const [isBook, setIsBook] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);

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
                        <button className="btn btn-primary" onClick={() => onNavigate('recipes')}>
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

        // Normalise common separators into newlines
        // Handles "1. …", "1) …", "Step 1: …", "Step 1 - …"
        text = text.replace(/(?:^|\n)\s*(?:step\s*)?\d+[.):\-]\s*/gi, '\n');

        // Split on newlines first
        let parts = text.split(/\n+/).map(s => s.trim()).filter(Boolean);

        // If still only one chunk, try period-space-uppercase boundaries
        if (parts.length <= 1) {
            parts = text.split(/\.\s+/).map(s => s.trim()).filter(Boolean);
        }

        // Clean each step: strip leading bullets/dashes, trailing period
        return parts.map(s =>
            s.replace(/^[-•*>]+\s*/, '').replace(/\.$/, '').trim()
        ).filter(Boolean);
    };

    const steps = parseInstructions(recipe.instruction);

    const handleChat = async () => {
        if (!chatInput.trim()) return;

        const userMessage = chatInput.trim();
        setChatInput('');
        setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await chat(sessionId || 'default', userMessage, recipe);
            setChatMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response,
                suggestions: response.suggestions
            }]);
        } catch (err) {
            setChatMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestion = (suggestion) => {
        setChatInput(suggestion);
    };

    return (
        <div className="page recipe-detail-page">
            <div className="container">
                <button className="back-btn" onClick={() => onNavigate('recipes')}>
                    ← Back to Recipes
                </button>

                <div className="recipe-detail-content">
                    {/* Recipe Info */}
                    <div className="recipe-main fade-in">
                        <div className="recipe-header">
                            <h1>{recipe.recipe}</h1>
                            <div className="recipe-meta">
                                <span className="meta-item">⏱️ ~30 min</span>
                                <span className="meta-item">🍽️ 4 servings</span>
                                <span className="meta-item">🌶️ Medium</span>
                            </div>

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

                        {/* Ingredients */}
                        <div className="recipe-section">
                            <h2>📝 Ingredients</h2>
                            <div className="ingredients-list-detail">
                                {recipe.ingredients.split(',').map((ing, i) => (
                                    <div key={i} className="ingredient-item">
                                        <span className="ingredient-bullet">•</span>
                                        <span>{ing.trim()}</span>
                                    </div>
                                ))}
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
                                    <p className="instruction-fallback">{recipe.instruction}</p>
                                )}
                            </div>
                        </div>

                        {/* Tips */}
                        <div className="recipe-tips glass">
                            <h3>💡 Pro Tips</h3>
                            <ul>
                                <li>Prep all ingredients before starting to cook</li>
                                <li>Adjust spice levels to your preference</li>
                                <li>Let the dish rest for 2-3 minutes before serving</li>
                            </ul>
                        </div>
                    </div>

                    {/* Chat Assistant */}
                    <div className="recipe-chat slide-up">
                        <div className="chat-header">
                            <h3>🤖 Recipe Assistant</h3>
                            <p>Ask me anything about this recipe!</p>
                        </div>

                        <div className="chat-messages">
                            {chatMessages.length === 0 ? (
                                <div className="chat-welcome">
                                    <p>Need help with this recipe? Ask me about:</p>
                                    <div className="chat-suggestions">
                                        <button onClick={() => handleSuggestion('Can I use pressure cooker?')}>
                                            Pressure cooker method?
                                        </button>
                                        <button onClick={() => handleSuggestion('How to make it less spicy?')}>
                                            Make it less spicy?
                                        </button>
                                        <button onClick={() => handleSuggestion('What can I substitute?')}>
                                            Substitutions?
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                chatMessages.map((msg, i) => (
                                    <div key={i} className={`chat-message ${msg.role}`}>
                                        <div className="message-content">
                                            {msg.content.split('\n').map((line, j) => (
                                                <p key={j}>{line}</p>
                                            ))}
                                        </div>
                                        {msg.suggestions && msg.suggestions.length > 0 && (
                                            <div className="chat-suggestions">
                                                {msg.suggestions.map((s, j) => (
                                                    <button key={j} onClick={() => handleSuggestion(s)}>
                                                        {s}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
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
                        </div>

                        <div className="chat-input-group">
                            <input
                                type="text"
                                placeholder="Ask a question..."
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                            />
                            <button
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
