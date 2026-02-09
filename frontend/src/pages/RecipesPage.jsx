import './RecipesPage.css';

function RecipesPage({ sessionId, recommendations, onNavigate }) {
    const { ready_to_cook = [], almost_there = [], need_shopping = [] } = recommendations || {};

    const RecipeCard = ({ recipe, variant = 'default' }) => (
        <div
            className={`recipe-card card ${variant}`}
            onClick={() => onNavigate('recipe-detail', { recipe })}
        >
            <div className="recipe-card-header">
                <div>
                    <h3 className="recipe-card-title">{recipe.recipe}</h3>
                    <div className="recipe-card-meta">
                        <span>⏱️ ~30 min</span>
                        <span>🍽️ 4 servings</span>
                    </div>
                </div>
                {variant === 'ready' && <span className="badge badge-success">✓ Ready</span>}
                {variant === 'almost' && <span className="badge badge-warning">Almost</span>}
            </div>

            <div className="recipe-card-ingredients">
                {recipe.have?.slice(0, 4).map((ing, i) => (
                    <span key={i} className="ingredient-tag have">✓ {ing}</span>
                ))}
                {recipe.missing_critical?.slice(0, 2).map((ing, i) => (
                    <span key={i} className="ingredient-tag missing">✗ {ing}</span>
                ))}
                {(recipe.have?.length > 4 || recipe.missing_critical?.length > 2) && (
                    <span className="ingredient-tag">+more</span>
                )}
            </div>
        </div>
    );

    const isEmpty = ready_to_cook.length === 0 && almost_there.length === 0 && need_shopping.length === 0;

    return (
        <div className="page recipes-page">
            <div className="container">
                <button className="back-btn" onClick={() => onNavigate('upload')}>
                    ← Start Over
                </button>

                <div className="page-content">
                    <div className="recipes-header fade-in">
                        <h1>Recipe Recommendations</h1>
                        <p>Based on your ingredients</p>
                    </div>

                    {isEmpty ? (
                        <div className="empty-state slide-up">
                            <div className="empty-state-icon">🍳</div>
                            <h3>No recipes found</h3>
                            <p>Try adding more ingredients or different ones</p>
                            <button
                                className="btn btn-primary"
                                onClick={() => onNavigate('upload')}
                            >
                                Try Again
                            </button>
                        </div>
                    ) : (
                        <>
                            {/* Ready to Cook */}
                            {ready_to_cook.length > 0 && (
                                <div className="recipe-section slide-up">
                                    <div className="section-header">
                                        <h2>🎯 Ready to Cook</h2>
                                        <span className="section-count">{ready_to_cook.length} recipes</span>
                                    </div>
                                    <div className="recipe-grid">
                                        {ready_to_cook.map((recipe, i) => (
                                            <RecipeCard key={i} recipe={recipe} variant="ready" />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Almost There */}
                            {almost_there.length > 0 && (
                                <div className="recipe-section slide-up" style={{ animationDelay: '0.1s' }}>
                                    <div className="section-header">
                                        <h2>🛒 Almost There</h2>
                                        <span className="section-count">{almost_there.length} recipes</span>
                                    </div>
                                    <div className="recipe-grid">
                                        {almost_there.map((recipe, i) => (
                                            <RecipeCard key={i} recipe={recipe} variant="almost" />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Worth Shopping For */}
                            {need_shopping.length > 0 && (
                                <div className="recipe-section slide-up" style={{ animationDelay: '0.2s' }}>
                                    <div className="section-header">
                                        <h2>🛍️ Worth Shopping For</h2>
                                        <span className="section-count">{need_shopping.length} recipes</span>
                                    </div>
                                    <div className="recipe-grid">
                                        {need_shopping.map((recipe, i) => (
                                            <RecipeCard key={i} recipe={recipe} />
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export default RecipesPage;
