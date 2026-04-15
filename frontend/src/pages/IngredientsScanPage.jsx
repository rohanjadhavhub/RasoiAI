import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './IngredientsScanPage.css';
import {
    analyzeIngredients,
    confirmIngredients,
    getRecommendations,
    remoteScan,
    getRpiImageUrl,
    searchRecipes,
} from '../services/api';

const UPLOAD_STEPS = [
    { id: 'upload', label: 'Image received' },
    { id: 'vision', label: 'Vision model analyzing…' },
    { id: 'extract', label: 'Extracting ingredients…' },
    { id: 'done', label: 'Analysis complete' },
];

const REMOTE_STEPS = [
    { id: 'capture', label: 'Capturing from fridge…' },
    { id: 'scan', label: 'Image scanned by AI…' },
    { id: 'extract', label: 'Extracting ingredients…' },
    { id: 'done', label: 'Analysis complete' },
];

function IngredientsScanPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const {
        sessionId,
        preview: initialPreview,
        mode = 'upload',          // 'upload' | 'remote'
    } = location.state || {};

    const isRemote = mode === 'remote';
    const scanSteps = isRemote ? REMOTE_STEPS : UPLOAD_STEPS;

    const [currentStep, setCurrentStep] = useState(0);
    const [isScanning, setIsScanning] = useState(true);
    const [ingredients, setIngredients] = useState([]);
    const [rawIngredients, setRawIngredients] = useState([]);
    const [error, setError] = useState(null);
    const [newIngredient, setNewIngredient] = useState('');
    const [isLoadingRecipes, setIsLoadingRecipes] = useState(false);
    const [preview, setPreview] = useState(initialPreview || null);

    // Redirect if no session (upload mode) or no mode at all
    useEffect(() => {
        if (!isRemote && !sessionId) {
            navigate('/upload');
        }
    }, [sessionId, isRemote, navigate]);

    // ── Upload mode pipeline ──
    useEffect(() => {
        if (isRemote || !sessionId) return;

        let cancelled = false;

        const runAnalysis = async () => {
            try {
                setCurrentStep(0);
                await delay(800);
                if (cancelled) return;

                setCurrentStep(1);
                const result = await analyzeIngredients(sessionId);
                if (cancelled) return;

                setCurrentStep(2);
                await delay(600);
                if (cancelled) return;

                setCurrentStep(3);
                await delay(400);
                if (cancelled) return;

                const detected = result.identified_ingredients || [];
                setRawIngredients(detected);
                setIngredients(detected.map(i => i.name));
                setIsScanning(false);
            } catch (err) {
                if (!cancelled) {
                    setError(err.message || 'Failed to analyze ingredients');
                    setIsScanning(false);
                }
            }
        };

        runAnalysis();
        return () => { cancelled = true; };
    }, [sessionId, isRemote]);

    // ── Remote mode pipeline ──
    useEffect(() => {
        if (!isRemote) return;

        let cancelled = false;

        const runRemoteScan = async () => {
            try {
                // Step 1: Capturing from fridge
                setCurrentStep(0);
                const data = await remoteScan();
                if (cancelled) return;

                // Show the captured fridge image
                setPreview(getRpiImageUrl());

                // Step 2: Image scanned by AI
                setCurrentStep(1);
                await delay(800);
                if (cancelled) return;

                // Step 3: Extracting ingredients
                setCurrentStep(2);
                await delay(600);
                if (cancelled) return;

                // Step 4: Done
                setCurrentStep(3);
                await delay(400);
                if (cancelled) return;

                const detected = (data.ingredients_detected || []).map(name => ({
                    name,
                    confidence: 0.9,
                }));
                setRawIngredients(detected);
                setIngredients(detected.map(i => i.name));
                setIsScanning(false);
            } catch (err) {
                if (!cancelled) {
                    setError(err.message || 'Remote scan failed — is the RPi online?');
                    setIsScanning(false);
                }
            }
        };

        runRemoteScan();
        return () => { cancelled = true; };
    }, [isRemote]);

    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    const removeIngredient = useCallback((name) => {
        setIngredients(prev => prev.filter(i => i !== name));
        setRawIngredients(prev => prev.filter(i => i.name !== name));
    }, []);

    const addIngredient = useCallback(() => {
        const trimmed = newIngredient.trim().toLowerCase();
        if (trimmed && !ingredients.includes(trimmed)) {
            setIngredients(prev => [...prev, trimmed]);
            setRawIngredients(prev => [...prev, { name: trimmed, confidence: 0.85 }]);
            setNewIngredient('');
        }
    }, [newIngredient, ingredients]);

    const handleRecommendRecipes = async () => {
        if (ingredients.length === 0) {
            setError('No ingredients to search with');
            return;
        }

        setIsLoadingRecipes(true);
        setError(null);

        try {
            if (isRemote) {
                // Remote mode — use searchRecipes directly (no session)
                const result = await searchRecipes(ingredients);
                const recipes = result.recipes || [];
                const ready = recipes.filter(r => r.readiness === 'READY');
                const almost = recipes.filter(r => r.readiness === 'ALMOST_THERE');
                const shopping = recipes.filter(r => r.readiness === 'NEED_SHOPPING');

                navigate('/recipes', {
                    state: {
                        recommendations: {
                            ready_to_cook: ready,
                            almost_there: almost,
                            need_shopping: shopping,
                        },
                    },
                });
            } else {
                // Upload mode — confirm + get recommendations via session
                await confirmIngredients(sessionId, ingredients);
                const recommendations = await getRecommendations(sessionId);
                navigate('/recipes', { state: { recommendations, sessionId } });
            }
        } catch (err) {
            setError(err.message || 'Failed to get recommendations');
        } finally {
            setIsLoadingRecipes(false);
        }
    };

    // Helper to get confidence level
    const getConfidenceLevel = (conf) => {
        if (conf >= 0.8) return 'high';
        if (conf >= 0.5) return 'medium';
        return 'low';
    };

    // Helper to get dot color class
    const getDotClass = (index) => {
        const cycle = index % 3;
        if (cycle === 1) return 'ingredient-name__dot--alt';
        if (cycle === 2) return 'ingredient-name__dot--accent';
        return '';
    };

    // Guard: upload mode without session
    if (!isRemote && !sessionId) return null;

    return (
        <div className="scan-page">

            {/* Chapter 1: Hero */}
            <section className="chapter chapter--scan-hero">
                <div className="container">
                    <div className="chapter__content fade-in">
                        <span className="chapter__label">
                            {isRemote ? 'Fridge scan' : 'Ingredient analysis'}
                        </span>
                        <h1 className="chapter__headline">
                            {isScanning ? (
                                isRemote ? (
                                    <>
                                        Scanning your<br />
                                        <em>fridge.</em>
                                    </>
                                ) : (
                                    <>
                                        Our AI is reading<br />
                                        your <em>kitchen.</em>
                                    </>
                                )
                            ) : error ? (
                                <>
                                    Something went<br />
                                    <em>wrong.</em>
                                </>
                            ) : (
                                <>
                                    We found <em>{ingredients.length}</em><br />
                                    ingredients.
                                </>
                            )}
                        </h1>
                        <p className="chapter__body">
                            {isScanning
                                ? isRemote
                                    ? 'Your fridge camera is capturing and our AI is identifying every ingredient inside. Hang tight.'
                                    : 'Gemini Vision is analyzing your photo to identify every ingredient. This takes just a moment.'
                                : error
                                    ? 'There was a problem analyzing your image. Please try again.'
                                    : 'Review what we detected below. Add or remove items before finding recipes.'
                            }
                        </p>
                    </div>
                </div>
            </section>

            {/* Chapter 2: Scanning Animation */}
            {isScanning && (
                <section className="chapter chapter--scanning">
                    <div className="container">
                        <div className="scanning-stage">
                            {preview && (
                                <div className="scanning-preview">
                                    <img src={preview} alt={isRemote ? 'Fridge camera capture' : 'Uploaded kitchen photo'} />
                                </div>
                            )}

                            {/* Fridge icon when no preview yet (remote mode) */}
                            {!preview && isRemote && (
                                <div className="scanning-preview scanning-preview--placeholder">
                                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                                        <rect x="4" y="2" width="16" height="20" rx="2" />
                                        <line x1="4" y1="10" x2="20" y2="10" />
                                        <line x1="12" y1="6" x2="12" y2="6.01" />
                                        <line x1="12" y1="14" x2="12" y2="14.01" />
                                    </svg>
                                </div>
                            )}

                            <div className="scanning-status">
                                <div className="scanning-status__title">
                                    {isRemote
                                        ? 'Scanning fridge with AI…'
                                        : 'Analyzing with Gemini Vision…'
                                    }
                                </div>

                                <div className="scanning-status__steps">
                                    {scanSteps.map((step, idx) => (
                                        <div
                                            key={step.id}
                                            className={`scan-step ${
                                                idx < currentStep
                                                    ? 'scan-step--done'
                                                    : idx === currentStep
                                                        ? 'scan-step--active'
                                                        : ''
                                            }`}
                                        >
                                            <span className="scan-step__icon">
                                                {idx < currentStep ? '✓' : ''}
                                            </span>
                                            <span>{step.label}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            )}

            {/* Chapter 3: Results Table */}
            {!isScanning && !error && (
                <section className="chapter chapter--scan-results">
                    <div className="container">
                        <div className="scan-results-wrapper">
                            <span className="chapter__label">Detected ingredients</span>
                            <h2 className="chapter__headline">
                                Everything we found in<br />
                                your {isRemote ? 'fridge' : 'photo'}.
                            </h2>

                            {/* Summary bar */}
                            <div className="scan-summary">
                                <span className="scan-summary__text">
                                    <strong>{ingredients.length}</strong> ingredient{ingredients.length !== 1 ? 's' : ''} identified
                                    {isRemote ? ' from fridge scan' : ' by AI'}
                                </span>
                            </div>

                            {/* Add ingredient controls */}
                            <div className="scan-edit-controls">
                                <input
                                    type="text"
                                    placeholder="Add missing ingredient…"
                                    value={newIngredient}
                                    onChange={(e) => setNewIngredient(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && addIngredient()}
                                />
                                <button className="btn btn-secondary" onClick={addIngredient}>
                                    + Add
                                </button>
                            </div>

                            {/* Ingredients table */}
                            {ingredients.length > 0 ? (
                                <table className="ingredients-table">
                                    <thead>
                                        <tr>
                                            <th style={{ width: 60 }}>#</th>
                                            <th>Ingredient</th>
                                            <th style={{ width: 180 }}>Confidence</th>
                                            <th style={{ width: 60 }}></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rawIngredients.map((ing, index) => {
                                            const conf = ing.confidence || 0.9;
                                            const level = getConfidenceLevel(conf);
                                            return (
                                                <tr
                                                    key={ing.name}
                                                    style={{ animationDelay: `${index * 0.06}s` }}
                                                >
                                                    <td>
                                                        <span className="ingredient-num">
                                                            {String(index + 1).padStart(2, '0')}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span className="ingredient-name">
                                                            <span className={`ingredient-name__dot ${getDotClass(index)}`}></span>
                                                            {ing.name}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <div className="confidence-bar">
                                                            <div className="confidence-bar__track">
                                                                <div
                                                                    className={`confidence-bar__fill confidence-bar__fill--${level}`}
                                                                    style={{ width: `${Math.round(conf * 100)}%` }}
                                                                />
                                                            </div>
                                                            <span className="confidence-bar__label">
                                                                {Math.round(conf * 100)}%
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <button
                                                            className="ingredient-remove"
                                                            onClick={() => removeIngredient(ing.name)}
                                                            aria-label={`Remove ${ing.name}`}
                                                        >
                                                            ×
                                                        </button>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            ) : (
                                <div className="empty-state slide-up">
                                    <div className="empty-state-icon">🥬</div>
                                    <h3>No ingredients</h3>
                                    <p>Add ingredients manually using the input above.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </section>
            )}

            {/* Error display */}
            {error && !isScanning && (
                <section className="chapter chapter--scan-results">
                    <div className="container">
                        <div className="scan-error fade-in">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="15" y1="9" x2="9" y2="15" />
                                <line x1="9" y1="9" x2="15" y2="15" />
                            </svg>
                            {error}
                        </div>
                        <button
                            className="btn btn-primary"
                            onClick={() => navigate('/upload')}
                            style={{ marginTop: 24 }}
                        >
                            Try Again
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="5" y1="12" x2="19" y2="12" />
                                <polyline points="12 5 19 12 12 19" />
                            </svg>
                        </button>
                    </div>
                </section>
            )}

            {/* Chapter 4: CTA - Recommend Recipes */}
            {!isScanning && !error && ingredients.length > 0 && (
                <section className="chapter chapter--scan-cta">
                    <div className="container">
                        <div className="chapter__content">
                            <h2 className="chapter__headline">
                                Ready to find what<br />
                                you can cook?
                            </h2>
                            <p className="chapter__body">
                                We'll match your {ingredients.length} ingredient{ingredients.length !== 1 ? 's' : ''} against
                                6,500+ authentic Indian recipes.
                            </p>
                            <button
                                className="btn btn-primary btn-large"
                                onClick={handleRecommendRecipes}
                                disabled={isLoadingRecipes}
                                id="recommend-recipes-btn"
                            >
                                {isLoadingRecipes ? (
                                    <>
                                        <div className="spinner" style={{ width: 20, height: 20 }}></div>
                                        Finding recipes…
                                    </>
                                ) : (
                                    <>
                                        Recommend Recipes
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                            <line x1="5" y1="12" x2="19" y2="12" />
                                            <polyline points="12 5 19 12 12 19" />
                                        </svg>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </section>
            )}

            <footer className="landing-footer">
                <div className="container">
                    <p>RasoiAI — built for Indian home cooking</p>
                </div>
            </footer>
        </div>
    );
}

export default IngredientsScanPage;
