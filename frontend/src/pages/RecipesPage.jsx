import { useNavigate, useLocation } from 'react-router-dom';
import './RecipesPage.css';

function RecipesPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const { recommendations, sessionId } = location.state || {};
    const { ready_to_cook = [], almost_there = [], need_shopping = [] } = recommendations || {};

    const RecipeCard = ({ recipe, variant = 'default' }) => (
        <div
            className={`rp-card rp-card--${variant}`}
            onClick={() => navigate('/recipe', { state: { recipe, sessionId } })}
        >
            <div className="rp-card__header">
                <div>
                    <h3 className="rp-card__title">{recipe.recipe}</h3>
                    <div className="rp-card__meta">
                        <span>⏱️ ~30 min</span>
                        <span>🍽️ 4 servings</span>
                    </div>
                </div>
                {variant === 'ready' && <span className="badge badge-success">✓ Ready</span>}
                {variant === 'almost' && <span className="badge badge-warning">Almost</span>}
            </div>

            <div className="rp-card__tags">
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

            <div className="rp-card__action">
                <span>View Recipe</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                </svg>
            </div>
        </div>
    );

    const isEmpty = ready_to_cook.length === 0 && almost_there.length === 0 && need_shopping.length === 0;
    const totalCount = ready_to_cook.length + almost_there.length + need_shopping.length;

    return (
        <div className="recipes-page">

            {/* Page Header */}
            <div className="rp-header">
                <div className="container">
                    <button className="back-btn" onClick={() => navigate('/upload')}>
                        ← Back to scan
                    </button>
                    <div className="rp-header__content fade-in">
                        <span className="rp-header__label">Your Results</span>
                        <h1 className="rp-header__title">
                            {isEmpty
                                ? 'No Matches Found'
                                : `${totalCount} Recipe${totalCount !== 1 ? 's' : ''} Matched`}
                        </h1>
                        <p className="rp-header__subtitle">
                            {isEmpty
                                ? 'Try scanning with more ingredients or adjust your search'
                                : 'Sorted by what you can cook right now'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Results */}
            <div className="rp-results">
                <div className="container">

                    {isEmpty ? (
                        <div className="rp-empty slide-up">
                            <div className="rp-empty__icon">🍳</div>
                            <h3>Nothing matched your ingredients</h3>
                            <p>Add more ingredients or try different ones to unlock recipes from our 6,500+ collection.</p>
                            <button
                                className="btn btn-primary"
                                onClick={() => navigate('/upload')}
                            >
                                Scan Again
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                    <line x1="5" y1="12" x2="19" y2="12" />
                                    <polyline points="12 5 19 12 12 19" />
                                </svg>
                            </button>
                        </div>
                    ) : (
                        <>
                            {/* Ready to Cook */}
                            {ready_to_cook.length > 0 && (
                                <div className="rp-section rp-section--ready slide-up">
                                    <div className="rp-section__header">
                                        <div className="rp-section__indicator rp-section__indicator--ready"></div>
                                        <div>
                                            <h2 className="rp-section__title">Ready to Cook</h2>
                                            <p className="rp-section__desc">You have everything needed — start cooking now</p>
                                        </div>
                                        <span className="rp-section__count">{ready_to_cook.length}</span>
                                    </div>
                                    <div className="rp-grid">
                                        {ready_to_cook.map((recipe, i) => (
                                            <RecipeCard key={i} recipe={recipe} variant="ready" />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Almost There */}
                            {almost_there.length > 0 && (
                                <div className="rp-section rp-section--almost slide-up" style={{ animationDelay: '0.1s' }}>
                                    <div className="rp-section__header">
                                        <div className="rp-section__indicator rp-section__indicator--almost"></div>
                                        <div>
                                            <h2 className="rp-section__title">Almost There</h2>
                                            <p className="rp-section__desc">Missing one or two items — quick substitutes may work</p>
                                        </div>
                                        <span className="rp-section__count">{almost_there.length}</span>
                                    </div>
                                    <div className="rp-grid">
                                        {almost_there.map((recipe, i) => (
                                            <RecipeCard key={i} recipe={recipe} variant="almost" />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Need Shopping */}
                            {need_shopping.length > 0 && (
                                <div className="rp-section rp-section--shopping slide-up" style={{ animationDelay: '0.2s' }}>
                                    <div className="rp-section__header">
                                        <div className="rp-section__indicator rp-section__indicator--shopping"></div>
                                        <div>
                                            <h2 className="rp-section__title">Worth Shopping For</h2>
                                            <p className="rp-section__desc">Great dishes that need a few more ingredients</p>
                                        </div>
                                        <span className="rp-section__count">{need_shopping.length}</span>
                                    </div>
                                    <div className="rp-grid">
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

            <footer className="landing-footer">
                <div className="container">
                    <p>RasoiAI — built for Indian home cooking</p>
                </div>
            </footer>
        </div>
    );
}

export default RecipesPage;
