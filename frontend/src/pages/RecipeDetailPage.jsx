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
            <div className="rd-page">
                <div className="container">
                    <div className="rd-empty">
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
        <div className="rd-page">

            {/* Header Bar */}
            <div className="rd-topbar">
                <div className="container">
                    <button className="back-btn" onClick={() => navigate(-1)}>
                        ← Back to results
                    </button>
                </div>
            </div>

            {/* Recipe Title Section */}
            <div className={`rd-hero ${isModified ? 'rd-hero--modified' : ''}`}>
                <div className="container">
                    <div className="rd-hero__content fade-in">
                        <div className="rd-hero__title-row">
                            <h1 className="rd-hero__title">{displayRecipe.recipe}</h1>
                            {isModified && (
                                <span className="rd-modified-badge">Modified</span>
                            )}
                        </div>
                        <div className="rd-hero__meta">
                            <span className="rd-meta-item">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                                {displayRecipe.cook_time || '~30 min'}
                            </span>
                            <span className="rd-meta-item">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
                                {displayRecipe.servings || '4 servings'}
                            </span>
                            <span className="rd-meta-item">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/><path d="M12 6v6l4 2"/></svg>
                                {displayRecipe.spice_level || 'Medium'}
                            </span>
                        </div>
                        <div className="rd-hero__actions">
                            {isModified && (
                                <button className="rd-reset-btn" onClick={resetRecipe}>
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                                    Reset to original
                                </button>
                            )}
                            {isAuthenticated && (
                                <div className="rd-action-btns">
                                    <button
                                        className={`rd-action-btn ${isFav ? 'rd-action-btn--active-fav' : ''}`}
                                        onClick={toggleFavourite}
                                        disabled={actionLoading}
                                        title={isFav ? 'Remove from favourites' : 'Add to favourites'}
                                    >
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill={isFav ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                                        </svg>
                                    </button>
                                    <button
                                        className={`rd-action-btn ${isBook ? 'rd-action-btn--active-book' : ''}`}
                                        onClick={toggleBookmark}
                                        disabled={actionLoading}
                                        title={isBook ? 'Remove bookmark' : 'Save for later'}
                                    >
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill={isBook ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                                        </svg>
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="rd-body">
                <div className="container">
                    <div className="rd-layout">

                        {/* Left: Recipe Details */}
                        <div className="rd-main">

                            {/* Ingredients */}
                            <section className="rd-section">
                                <div className="rd-section__header">
                                    <h2>Ingredients</h2>
                                    {hasGapData && (
                                        <div className="rd-legend">
                                            <span className="rd-legend__item rd-legend__item--have">Available</span>
                                            <span className="rd-legend__item rd-legend__item--missing">Missing</span>
                                            <span className="rd-legend__item rd-legend__item--optional">Optional</span>
                                        </div>
                                    )}
                                </div>
                                <div className="rd-ingredients">
                                    {displayRecipe.ingredients.split(',').map((ing, i) => {
                                        const status = classifyIngredient(ing);
                                        return (
                                            <div
                                                key={i}
                                                className={`rd-ingredient ${status ? `rd-ingredient--${status}` : ''}`}
                                            >
                                                <span className="rd-ingredient__bullet">•</span>
                                                <span>{ing.trim()}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </section>

                            {/* Instructions */}
                            <section className="rd-section">
                                <div className="rd-section__header">
                                    <h2>Instructions</h2>
                                </div>
                                <div className="rd-steps">
                                    {steps.length > 0 ? (
                                        steps.map((step, i) => (
                                            <div key={i} className="rd-step">
                                                <span className="rd-step__num">{String(i + 1).padStart(2, '0')}</span>
                                                <p className="rd-step__text">{step}</p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="rd-step__fallback">{displayRecipe.instruction}</p>
                                    )}
                                </div>
                            </section>

                            {/* Tips */}
                            <section className="rd-tips">
                                <h3>Pro Tips</h3>
                                <ul>
                                    <li>Prep all ingredients before starting to cook</li>
                                    <li>Adjust spice levels to your preference</li>
                                    <li>Let the dish rest for 2-3 minutes before serving</li>
                                </ul>
                            </section>
                        </div>

                        {/* Right: Chat Assistant */}
                        <aside className="rd-chat slide-up">
                            <div className="rd-chat__header">
                                <div className="rd-chat__identity">
                                    <span className="rd-chat__avatar">A</span>
                                    <div>
                                        <h3>Annapurna</h3>
                                        <p>Your recipe assistant</p>
                                    </div>
                                </div>
                            </div>

                            <div className="rd-chat__messages">
                                {chatMessages.length === 0 ? (
                                    <div className="rd-chat__welcome">
                                        <div className="rd-chat__welcome-avatar">A</div>
                                        <p className="rd-chat__welcome-text">
                                            I'm Annapurna — ask me anything about this recipe, or tell me how you'd like it changed.
                                        </p>
                                        <div className="rd-chat__suggestions">
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
                                        <div key={i} className={`rd-msg rd-msg--${msg.role}`}>
                                            {msg.role === 'assistant' && (
                                                <span className="rd-msg__avatar">A</span>
                                            )}
                                            <div className="rd-msg__content">
                                                {msg.content.split('\n').map((line, j) => (
                                                    line.trim() ? <p key={j}>{line}</p> : null
                                                ))}
                                            </div>
                                        </div>
                                    ))
                                )}
                                {isLoading && (
                                    <div className="rd-msg rd-msg--assistant">
                                        <div className="rd-msg__content rd-typing">
                                            <span></span><span></span><span></span>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            <div className="rd-chat__input">
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
                        </aside>
                    </div>
                </div>
            </div>

            <footer className="landing-footer">
                <div className="container">
                    <p>RasoiAI — built for Indian home cooking</p>
                </div>
            </footer>
        </div>
    );
}

export default RecipeDetailPage;
