import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="landing-page">

            {/* Chapter 1: The Hook */}
            <section className="chapter chapter--hook">
                <div className="container">
                    <div className="chapter__content fade-in">
                        <span className="chapter__label">The everyday struggle</span>
                        <h1 className="chapter__headline">
                            You open the fridge.<br />
                            Ingredients stare back.<br />
                            <em>No ideas come.</em>
                        </h1>
                    </div>
                </div>
            </section>

            {/* Chapter 2: The Problem */}
            <section className="chapter chapter--problem">
                <div className="container">
                    <div className="chapter__content">
                        <span className="chapter__label">The problem</span>
                        <h2 className="chapter__headline">
                            6,500 Indian recipes exist.<br />
                            You know maybe 20.
                        </h2>
                        <p className="chapter__body">
                            The gap between what you have and what you could cook
                            is not knowledge -- it's connection. Your ingredients already
                            hold the answer. You just can't see it yet.
                        </p>
                    </div>
                </div>
            </section>

            {/* Chapter 3: The Turn */}
            <section className="chapter chapter--turn">
                <div className="container">
                    <div className="chapter__content">
                        <span className="chapter__label">The shift</span>
                        <h2 className="chapter__headline">
                            What if your camera<br />
                            could read your kitchen?
                        </h2>
                        <div className="turn__steps">
                            <div className="turn__step">
                                <div className="turn__step-num">01</div>
                                <div className="turn__step-content">
                                    <h3>Point your camera</h3>
                                    <p>Snap a photo of whatever you have. Messy counter, open fridge, scattered veggies -- all fine.</p>
                                </div>
                            </div>
                            <div className="turn__step">
                                <div className="turn__step-num">02</div>
                                <div className="turn__step-content">
                                    <h3>AI sees ingredients</h3>
                                    <p>Our Vision Model identifies every ingredient in your photo. Tomatoes, onions, that forgotten paneer -- nothing escapes.</p>
                                </div>
                            </div>
                            <div className="turn__step">
                                <div className="turn__step-num">03</div>
                                <div className="turn__step-content">
                                    <h3>Recipes appear</h3>
                                    <p>Matched against 6,500+ authentic Indian recipes. Sorted by what you can cook right now, no shopping required.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Chapter 4: The Proof */}
            <section className="chapter chapter--proof">
                <div className="container">
                    <div className="proof__grid">
                        <div className="proof__card">
                            <div className="proof__number">6,500+</div>
                            <div className="proof__label">Indian recipes in our database</div>
                        </div>
                        <div className="proof__card">
                            <div className="proof__number">&lt;3s</div>
                            <div className="proof__label">From photo to recipe matches</div>
                        </div>
                        <div className="proof__card">
                            <div className="proof__number">AI</div>
                            <div className="proof__label">Powered by Gemini Vision</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Chapter 5: The Climax CTA */}
            <section className="chapter chapter--cta">
                <div className="container">
                    <div className="chapter__content">
                        <h2 className="chapter__headline">
                            Tonight's dinner is already<br />
                            in your kitchen.
                        </h2>
                        <p className="chapter__body">
                            Stop scrolling for recipes. Start with what you have.
                        </p>
                        <div className="cta__actions">
                            <button
                                className="btn btn-primary btn-large"
                                onClick={() => navigate('/upload')}
                                aria-label="Upload ingredient photos to get recipe suggestions"
                            >
                                Scan Your Ingredients
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                    <line x1="5" y1="12" x2="19" y2="12" />
                                    <polyline points="12 5 19 12 12 19" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <footer className="landing-footer">
                <div className="container">
                    <p>RasoiAI -- built for Indian home cooking</p>
                </div>
            </footer>
        </div>
    );
}

export default LandingPage;
