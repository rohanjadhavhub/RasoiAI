import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './UploadPage.css';
import { uploadImages, searchRecipes } from '../services/api';

function UploadPage() {
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [previews, setPreviews] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [manualInput, setManualInput] = useState('');



    const handleFileChange = useCallback((e) => {
        const selectedFiles = Array.from(e.target.files).slice(0, 3);
        setFiles(selectedFiles);
        setError(null);

        // Create previews
        const newPreviews = selectedFiles.map(file => URL.createObjectURL(file));
        setPreviews(newPreviews);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        const droppedFiles = Array.from(e.dataTransfer.files)
            .filter(f => f.type.startsWith('image/'))
            .slice(0, 3);

        setFiles(droppedFiles);
        setError(null);

        const newPreviews = droppedFiles.map(file => URL.createObjectURL(file));
        setPreviews(newPreviews);
    }, []);

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const removeFile = (index) => {
        setFiles(files.filter((_, i) => i !== index));
        setPreviews(previews.filter((_, i) => i !== index));
    };

    const handleAnalyze = async () => {
        if (files.length === 0) {
            setError('Please upload at least one image');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            // Upload images
            const uploadResult = await uploadImages(files);
            const sessionId = uploadResult.session_id;

            // Navigate to scanning page — analysis happens there with animation
            navigate('/ingredients-scan', {
                state: {
                    sessionId,
                    preview: previews[0] || null
                }
            });
        } catch (err) {
            setError(err.message || 'Failed to upload images');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRemoteScan = () => {
        // Navigate to scanning page — remote scan + animation happens there
        navigate('/ingredients-scan', {
            state: { mode: 'remote' }
        });
    };

    const handleManualSearch = async () => {
        if (!manualInput.trim()) {
            setError('Please enter some ingredients');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const ingredients = manualInput.split(',').map(i => i.trim()).filter(Boolean);

            // Use search API directly
            const result = await searchRecipes(ingredients);

            // Group by readiness
            const ready = result.recipes.filter(r => r.readiness === 'READY');
            const almost = result.recipes.filter(r => r.readiness === 'ALMOST_THERE');
            const shopping = result.recipes.filter(r => r.readiness === 'NEED_SHOPPING');

            navigate('/recipes', {
                state: {
                    recommendations: {
                        ready_to_cook: ready,
                        almost_there: almost,
                        need_shopping: shopping
                    }
                }
            });
        } catch (err) {
            setError(err.message || 'Failed to search recipes');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="upload-page">

            {/* Chapter 1: The Moment */}
            <section className="chapter chapter--upload-hero">
                <div className="container">
                    <div className="chapter__content fade-in">
                        <span className="chapter__label">Your kitchen, decoded</span>
                        <h1 className="chapter__headline">
                            Show us what you have.<br />
                            We'll show you what to <em>cook.</em>
                        </h1>
                        <p className="chapter__body">
                            Three ways to start — snap a photo, scan your fridge remotely,
                            or just tell us what's on the counter. Pick your path.
                        </p>
                    </div>
                </div>
            </section>

            {/* Chapter 2: Upload Photos */}
            <section className="chapter chapter--photo-upload">
                <div className="container">
                    <div className="chapter__content">
                        <div className="upload-method">
                            <div className="upload-method__header">
                                <div className="upload-method__num">01</div>
                                <div>
                                    <span className="chapter__label">The quickest way</span>
                                    <h2 className="chapter__headline upload-method__title">
                                        Point. Snap. Cook.
                                    </h2>
                                    <p className="chapter__body">
                                        Messy counter? Open fridge? Doesn't matter. Our AI sees every
                                        ingredient hiding in your photo.
                                    </p>
                                </div>
                            </div>

                            <div
                                className={`upload-dropzone ${files.length > 0 ? 'has-files' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                            >
                                {previews.length > 0 ? (
                                    <div className="preview-grid">
                                        {previews.map((preview, index) => (
                                            <div key={index} className="preview-item">
                                                <img src={preview} alt={`Preview ${index + 1}`} />
                                                <button
                                                    className="preview-remove"
                                                    onClick={() => removeFile(index)}
                                                >
                                                    ×
                                                </button>
                                            </div>
                                        ))}
                                        {files.length < 3 && (
                                            <label className="preview-add">
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    multiple
                                                    onChange={handleFileChange}
                                                    hidden
                                                />
                                                <span>+</span>
                                            </label>
                                        )}
                                    </div>
                                ) : (
                                    <label className="dropzone-content">
                                        <input
                                            type="file"
                                            accept="image/*"
                                            multiple
                                            onChange={handleFileChange}
                                            hidden
                                        />
                                        <div className="dropzone-icon">
                                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                                                <circle cx="8.5" cy="8.5" r="1.5" />
                                                <polyline points="21 15 16 10 5 21" />
                                            </svg>
                                        </div>
                                        <p className="dropzone-text">
                                            Drop your kitchen photos here or <span>browse</span>
                                        </p>
                                        <p className="dropzone-hint">Up to 3 photos · JPG, PNG, WebP</p>
                                    </label>
                                )}
                            </div>

                            {files.length > 0 && (
                                <button
                                    className="btn btn-primary"
                                    onClick={handleAnalyze}
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <>
                                            <div className="spinner" style={{ width: 20, height: 20 }}></div>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            Identify Ingredients
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                                <line x1="5" y1="12" x2="19" y2="12" />
                                                <polyline points="12 5 19 12 12 19" />
                                            </svg>
                                        </>
                                    )}
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            {/* Chapter 3: Remote Scan */}
            <section className="chapter chapter--remote-scan">
                <div className="container">
                    <div className="chapter__content">
                        <div className="upload-method">
                            <div className="upload-method__header">
                                <div className="upload-method__num upload-method__num--turmeric">02</div>
                                <div>
                                    <span className="chapter__label">The smart way</span>
                                    <h2 className="chapter__headline upload-method__title">
                                        Your fridge has eyes now.
                                    </h2>
                                    <p className="chapter__body">
                                        One tap. Your connected fridge camera captures what's inside,
                                        AI identifies every ingredient, and recipes appear — all without
                                        leaving this screen.
                                    </p>
                                </div>
                            </div>

                            <div className="scan-action-area">
                                <button
                                    className="btn btn-scan"
                                    onClick={handleRemoteScan}
                                    disabled={isLoading}
                                    id="remote-scan-btn"
                                >
                                    Capture & Find Recipes
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                                        <circle cx="12" cy="13" r="4" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Chapter 4: Manual Input */}
            <section className="chapter chapter--manual-input">
                <div className="container">
                    <div className="chapter__content">
                        <div className="upload-method">
                            <div className="upload-method__header">
                                <div className="upload-method__num upload-method__num--teal">03</div>
                                <div>
                                    <span className="chapter__label">The classic way</span>
                                    <h2 className="chapter__headline upload-method__title">
                                        You already know what's there.
                                    </h2>
                                    <p className="chapter__body">
                                        No camera needed. Type what you have, separated by commas, and
                                        we'll match you with recipes from 6,500+ authentic dishes.
                                    </p>
                                </div>
                            </div>

                            <div className="manual-input-area">
                                <div className="manual-input-group">
                                    <input
                                        type="text"
                                        placeholder="e.g., potato, cauliflower, onion, tomato"
                                        value={manualInput}
                                        onChange={(e) => setManualInput(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleManualSearch()}
                                    />
                                    <button
                                        className="btn btn-primary"
                                        onClick={handleManualSearch}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Searching...' : 'Find Recipes'}
                                    </button>
                                </div>

                                <div className="quick-ingredients">
                                    <span className="quick-label">Quick add:</span>
                                    {['Potato', 'Paneer', 'Tomato', 'Onion', 'Rice', 'Chicken'].map(ing => (
                                        <button
                                            key={ing}
                                            className="chip"
                                            onClick={() => setManualInput(prev =>
                                                prev ? `${prev}, ${ing.toLowerCase()}` : ing.toLowerCase()
                                            )}
                                        >
                                            {ing}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Error display */}
            {error && (
                <div className="container">
                    <div className="upload-error fade-in">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                        {error}
                    </div>
                </div>
            )}

            <footer className="landing-footer">
                <div className="container">
                    <p>RasoiAI — built for Indian home cooking</p>
                </div>
            </footer>
        </div>
    );
}

export default UploadPage;
