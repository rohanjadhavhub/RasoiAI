import './LandingPage.css';

function LandingPage({ onNavigate }) {
    return (
        <div className="landing-page">
            <div className="landing-hero">
                <div className="container">
                    <div className="landing-content fade-in">
                        <div className="hero-badge">
                            ✨ AI-Powered Recipe Discovery
                        </div>

                        <h1 className="hero-title">
                            Cook What You Have,
                            <span className="gradient-text"> Love What You Eat</span>
                        </h1>

                        <p className="hero-subtitle">
                            Snap a photo of your ingredients and discover delicious Indian recipes
                            you can make right now. No shopping needed.
                        </p>

                        <div className="hero-features">
                            <div className="feature-item">
                                <span className="feature-icon">📸</span>
                                <span>Photo Recognition</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">🍛</span>
                                <span>40+ Indian Recipes</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">⚡</span>
                                <span>Instant Suggestions</span>
                            </div>
                        </div>

                        <div className="hero-actions">
                            <button
                                className="btn btn-primary btn-large"
                                onClick={() => onNavigate('upload')}
                            >
                                <span>🍳</span>
                                Start Cooking
                            </button>

                            <button
                                className="btn btn-secondary"
                                onClick={() => onNavigate('upload')}
                            >
                                Learn More
                            </button>
                        </div>
                    </div>

                    <div className="hero-visual slide-up">
                        <div className="hero-card glass">
                            <div className="hero-card-emoji">🥘</div>
                            <div className="hero-card-text">
                                <strong>Ready to Cook</strong>
                                <span>Aloo Gobi</span>
                            </div>
                        </div>
                        <div className="hero-card glass" style={{ animationDelay: '0.1s' }}>
                            <div className="hero-card-emoji">🍲</div>
                            <div className="hero-card-text">
                                <strong>Almost There</strong>
                                <span>Paneer Butter Masala</span>
                            </div>
                        </div>
                        <div className="hero-card glass" style={{ animationDelay: '0.2s' }}>
                            <div className="hero-card-emoji">🥗</div>
                            <div className="hero-card-text">
                                <strong>Quick & Easy</strong>
                                <span>Jeera Aloo</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <footer className="landing-footer">
                <p>Made with ❤️ for Indian home cooking</p>
            </footer>
        </div>
    );
}

export default LandingPage;
