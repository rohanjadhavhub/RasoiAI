import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './UploadPage.css';
import { uploadImages, analyzeIngredients, searchRecipes, remoteScan, getRpiImageUrl } from '../services/api';

function UploadPage() {
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [previews, setPreviews] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [manualInput, setManualInput] = useState('');

    // Remote scan state
    const [isScanning, setIsScanning] = useState(false);
    const [scanPreview, setScanPreview] = useState(null);
    const [scanIngredients, setScanIngredients] = useState([]);

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

            // Analyze ingredients
            const analysisResult = await analyzeIngredients(sessionId);

            // Navigate to ingredients confirmation
            const ingredientNames = analysisResult.identified_ingredients.map(i => i.name);
            navigate('/ingredients', {
                state: {
                    sessionId,
                    ingredients: ingredientNames
                }
            });
        } catch (err) {
            setError(err.message || 'Failed to analyze images');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRemoteScan = async () => {
        setIsScanning(true);
        setError(null);
        setScanPreview(null);
        setScanIngredients([]);

        try {
            const data = await remoteScan();

            // Show captured image preview
            setScanPreview(getRpiImageUrl());
            setScanIngredients(data.ingredients_detected || []);

            // Navigate to recipes with results from RPi
            const recipes = data.recipes?.recipes || [];
            const ready = recipes.filter(r => r.readiness === 'READY');
            const almost = recipes.filter(r => r.readiness === 'ALMOST_THERE');
            const shopping = recipes.filter(r => r.readiness === 'NEED_SHOPPING');

            // Short delay so user sees the scan result before navigating
            setTimeout(() => {
                navigate('/recipes', {
                    state: {
                        recommendations: {
                            ready_to_cook: ready,
                            almost_there: almost,
                            need_shopping: shopping
                        }
                    }
                });
            }, 1500);
        } catch (err) {
            setError(err.message || 'Remote scan failed — is the RPi online?');
        } finally {
            setIsScanning(false);
        }
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
        <div className="page upload-page">
            <div className="container">
                <button className="back-btn" onClick={() => navigate('/')}>
                    ← Back
                </button>

                <div className="page-content">
                    <div className="upload-header fade-in">
                        <h1>What's in Your Kitchen?</h1>
                        <p>Upload photos, scan from your RPi camera, or type ingredients manually</p>
                    </div>

                    {/* Image Upload Section */}
                    <div className="upload-section slide-up">
                        <h3 className="section-title">📸 Upload Photos</h3>

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
                                    <div className="dropzone-icon">📷</div>
                                    <p className="dropzone-text">
                                        Drag & drop images here or <span>browse</span>
                                    </p>
                                    <p className="dropzone-hint">Upload up to 3 photos</p>
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
                                    <>🔍 Analyze Ingredients</>
                                )}
                            </button>
                        )}
                    </div>

                    <div className="divider">
                        <span>or</span>
                    </div>

                    {/* RPi Remote Scan Section */}
                    <div className="remote-scan-section slide-up">
                        <h3 className="section-title">📡 Scan from Raspberry Pi</h3>
                        <p className="remote-scan-desc">
                            Capture ingredients directly from your RPi kitchen camera
                        </p>

                        <button
                            className="btn btn-scan"
                            onClick={handleRemoteScan}
                            disabled={isScanning || isLoading}
                            id="remote-scan-btn"
                        >
                            {isScanning ? (
                                <>
                                    <div className="spinner" style={{ width: 20, height: 20 }}></div>
                                    Scanning & Analyzing…
                                </>
                            ) : (
                                <>📸 Capture & Find Recipes</>
                            )}
                        </button>

                        {scanPreview && (
                            <div className="scan-result">
                                <img src={scanPreview} alt="Scanned ingredients" className="scan-preview" />
                                {scanIngredients.length > 0 && (
                                    <div className="scan-ingredients">
                                        <span className="scan-label">Detected:</span>
                                        {scanIngredients.map(ing => (
                                            <span key={ing} className="chip">{ing}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="divider">
                        <span>or</span>
                    </div>

                    {/* Manual Input Section */}
                    <div className="manual-section slide-up">
                        <h3 className="section-title">⌨️ Type Ingredients</h3>

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

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default UploadPage;
