import { useState } from 'react';
import './RecipeDetailPage.css';
import { chat } from '../services/api';

function RecipeDetailPage({ recipe, sessionId, onNavigate }) {
    const [chatInput, setChatInput] = useState('');
    const [chatMessages, setChatMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

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

    // Parse instructions into steps
    const parseInstructions = (instruction) => {
        if (!instruction) return [];
        return instruction
            .split(/\d+\.\s+/)
            .filter(step => step.trim())
            .map(step => step.trim().replace(/\.$/, ''));
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
                            <h2>👨‍🍳 Instructions</h2>
                            <div className="instructions-list">
                                {steps.map((step, i) => (
                                    <div key={i} className="instruction-step">
                                        <span className="step-number">{i + 1}</span>
                                        <p>{step}</p>
                                    </div>
                                ))}
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
