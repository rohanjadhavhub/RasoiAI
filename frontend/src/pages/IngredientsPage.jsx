import { useState } from 'react';
import './IngredientsPage.css';
import { confirmIngredients, getRecommendations } from '../services/api';

function IngredientsPage({ sessionId, ingredients: initialIngredients, onNavigate }) {
    const [ingredients, setIngredients] = useState(initialIngredients || []);
    const [newIngredient, setNewIngredient] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const addIngredient = () => {
        if (newIngredient.trim() && !ingredients.includes(newIngredient.trim().toLowerCase())) {
            setIngredients([...ingredients, newIngredient.trim().toLowerCase()]);
            setNewIngredient('');
        }
    };

    const removeIngredient = (ing) => {
        setIngredients(ingredients.filter(i => i !== ing));
    };

    const handleContinue = async () => {
        if (ingredients.length === 0) {
            setError('Please add at least one ingredient');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            // Confirm ingredients
            await confirmIngredients(sessionId, ingredients);

            // Get recommendations
            const recommendations = await getRecommendations(sessionId);

            onNavigate('recipes', { recommendations });
        } catch (err) {
            setError(err.message || 'Failed to get recommendations');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="page ingredients-page">
            <div className="container">
                <button className="back-btn" onClick={() => onNavigate('upload')}>
                    ← Back
                </button>

                <div className="page-content">
                    <div className="ingredients-header fade-in">
                        <h1>Confirm Your Ingredients</h1>
                        <p>Review and adjust the detected ingredients</p>
                    </div>

                    <div className="ingredients-list slide-up">
                        {ingredients.length > 0 ? (
                            <div className="ingredient-chips">
                                {ingredients.map((ing, index) => (
                                    <div key={index} className="ingredient-chip">
                                        <span>{ing}</span>
                                        <button
                                            className="chip-remove"
                                            onClick={() => removeIngredient(ing)}
                                        >
                                            ×
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-ingredients">
                                <span>🥬</span>
                                <p>No ingredients detected. Add some below!</p>
                            </div>
                        )}
                    </div>

                    <div className="add-ingredient">
                        <input
                            type="text"
                            placeholder="Add more ingredients..."
                            value={newIngredient}
                            onChange={(e) => setNewIngredient(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && addIngredient()}
                        />
                        <button className="btn btn-secondary" onClick={addIngredient}>
                            + Add
                        </button>
                    </div>

                    <div className="common-ingredients">
                        <p className="common-label">Common ingredients:</p>
                        <div className="common-chips">
                            {['Paneer', 'Chicken', 'Rice', 'Lentils', 'Spinach', 'Peas', 'Capsicum']
                                .filter(ing => !ingredients.includes(ing.toLowerCase()))
                                .map(ing => (
                                    <button
                                        key={ing}
                                        className="quick-chip"
                                        onClick={() => setIngredients([...ingredients, ing.toLowerCase()])}
                                    >
                                        + {ing}
                                    </button>
                                ))
                            }
                        </div>
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}

                    <div className="ingredients-actions">
                        <button
                            className="btn btn-primary btn-large"
                            onClick={handleContinue}
                            disabled={isLoading || ingredients.length === 0}
                        >
                            {isLoading ? (
                                <>
                                    <div className="spinner" style={{ width: 20, height: 20 }}></div>
                                    Finding recipes...
                                </>
                            ) : (
                                <>🍳 Find Recipes ({ingredients.length} ingredients)</>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default IngredientsPage;
