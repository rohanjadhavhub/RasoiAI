import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    fetchUserProfile,
    getFavourites,
    removeFavourite,
    getBookmarks,
    removeBookmark,
    getRecipe,
} from '../services/api';
import './ProfilePage.css';

const ProfilePage = () => {
    const navigate = useNavigate();
    const { user, getAccessTokenSilently, isAuthenticated, isLoading } = useAuth0();
    const [dbUser, setDbUser] = useState(null);
    const [error, setError] = useState(null);
    const [isSyncing, setIsSyncing] = useState(true);
    const [activeTab, setActiveTab] = useState('favourites');
    const [favourites, setFavourites] = useState([]);
    const [bookmarks, setBookmarks] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    // Sync profile & fetch history
    useEffect(() => {
        const syncUser = async () => {
            if (isAuthenticated) {
                try {
                    const token = await getAccessTokenSilently();
                    const profile = await fetchUserProfile(token);
                    setDbUser(profile);

                    // Fetch favourites & bookmarks in parallel
                    setHistoryLoading(true);
                    const [favs, books] = await Promise.all([
                        getFavourites(token),
                        getBookmarks(token),
                    ]);
                    setFavourites(favs);
                    setBookmarks(books);
                } catch (err) {
                    console.error('Error syncing user:', err);
                    setError('Failed to sync profile with server');
                } finally {
                    setIsSyncing(false);
                    setHistoryLoading(false);
                }
            }
        };

        syncUser();
    }, [isAuthenticated, getAccessTokenSilently]);

    const handleRemoveFavourite = async (recipeId) => {
        try {
            const token = await getAccessTokenSilently();
            await removeFavourite(token, recipeId);
            setFavourites(prev => prev.filter(f => f.recipe_id !== recipeId));
        } catch (err) {
            console.error('Failed to remove favourite:', err);
        }
    };

    const handleRemoveBookmark = async (recipeId) => {
        try {
            const token = await getAccessTokenSilently();
            await removeBookmark(token, recipeId);
            setBookmarks(prev => prev.filter(b => b.recipe_id !== recipeId));
        } catch (err) {
            console.error('Failed to remove bookmark:', err);
        }
    };

    const handleRecipeClick = async (item) => {
        try {
            // Fetch full recipe details (ingredients + instructions) by ID
            const fullRecipe = await getRecipe(item.recipe_id);
            navigate('/recipe', {
                state: {
                    recipe: fullRecipe,
                },
            });
        } catch (err) {
            console.error('Failed to load recipe:', err);
            // Fallback: navigate with just the name
            navigate('/recipe', {
                state: {
                    recipe: {
                        recipe_id: item.recipe_id,
                        recipe: item.recipe_name,
                        ingredients: '',
                        instruction: '',
                    },
                },
            });
        }
    };

    if (isLoading || isSyncing) {
        return (
            <div className="profile-page">
                <div className="profile-loading-state">
                    <div className="spinner"></div>
                    <p>Setting the table...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="profile-page">
                <div className="profile-unauth">
                    <div className="profile-unauth__icon">👨‍🍳</div>
                    <h1 className="profile-unauth__title">
                        Your kitchen story<br />
                        starts with a login.
                    </h1>
                    <p className="profile-unauth__body">
                        Sign in to save your favourite recipes, bookmark dishes for later,
                        and build your personal cooking journal.
                    </p>
                </div>
            </div>
        );
    }

    const renderList = (items, type) => {
        if (historyLoading) {
            return (
                <div className="profile-list-loading">
                    <div className="spinner" style={{ width: 24, height: 24 }}></div>
                    <p>Loading...</p>
                </div>
            );
        }

        if (items.length === 0) {
            return (
                <div className="profile-empty-state">
                    <div className="profile-empty-icon">
                        {type === 'favourites' ? '♡' : '⊟'}
                    </div>
                    <p className="profile-empty-title">
                        No {type} yet
                    </p>
                    <p className="profile-empty-hint">
                        {type === 'favourites'
                            ? 'Tap the heart on any recipe to add it here'
                            : 'Tap bookmark on any recipe to save it for later'}
                    </p>
                </div>
            );
        }

        return (
            <div className="saved-recipes-list">
                {items.map((item) => (
                    <div key={item.recipe_id} className="saved-recipe-row">
                        <div
                            className="saved-recipe-info"
                            onClick={() => handleRecipeClick(item)}
                        >
                            <p className="saved-recipe-name">
                                {item.recipe_name || `Recipe #${item.recipe_id}`}
                            </p>
                            <p className="saved-recipe-date">
                                Added {new Date(item.created_at).toLocaleDateString()}
                            </p>
                        </div>
                        <button
                            className="remove-btn"
                            onClick={() =>
                                type === 'favourites'
                                    ? handleRemoveFavourite(item.recipe_id)
                                    : handleRemoveBookmark(item.recipe_id)
                            }
                            title="Remove"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                <line x1="10" y1="11" x2="10" y2="17" />
                                <line x1="14" y1="11" x2="14" y2="17" />
                            </svg>
                        </button>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="profile-page">

            {/* Profile Header */}
            <section className="profile-header">
                <div className="container">
                    <div className="profile-header__inner fade-in">
                        <img src={user.picture} alt={user.name} className="profile-avatar" />
                        <div className="profile-header__info">
                            <span className="profile-greeting">Welcome back</span>
                            <h1 className="profile-name">{user.name}</h1>
                            <p className="profile-email">{user.email}</p>
                            <span className="profile-badge">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                    <polyline points="20 6 9 17 4 12" />
                                </svg>
                                Verified Chef
                            </span>
                        </div>
                        <div className="profile-stats">
                            <div className="profile-stat">
                                <span className="profile-stat__value">{favourites.length}</span>
                                <span className="profile-stat__label">Favourites</span>
                            </div>
                            <div className="profile-stat-divider"></div>
                            <div className="profile-stat">
                                <span className="profile-stat__value">{bookmarks.length}</span>
                                <span className="profile-stat__label">Bookmarks</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Saved Recipes */}
            <section className="profile-recipes">
                <div className="container">
                    <div className="profile-tabs">
                        <button
                            className={`profile-tab ${activeTab === 'favourites' ? 'profile-tab--active' : ''}`}
                            onClick={() => setActiveTab('favourites')}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill={activeTab === 'favourites' ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                            </svg>
                            Favourites
                            {favourites.length > 0 && (
                                <span className="profile-tab__count">{favourites.length}</span>
                            )}
                        </button>
                        <button
                            className={`profile-tab ${activeTab === 'bookmarks' ? 'profile-tab--active' : ''}`}
                            onClick={() => setActiveTab('bookmarks')}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill={activeTab === 'bookmarks' ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                            </svg>
                            Bookmarks
                            {bookmarks.length > 0 && (
                                <span className="profile-tab__count">{bookmarks.length}</span>
                            )}
                        </button>
                    </div>

                    <div className="profile-tab-content slide-up">
                        {activeTab === 'favourites'
                            ? renderList(favourites, 'favourites')
                            : renderList(bookmarks, 'bookmarks')}
                    </div>

                    {error && (
                        <div className="profile-error fade-in">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="15" y1="9" x2="9" y2="15" />
                                <line x1="9" y1="9" x2="15" y2="15" />
                            </svg>
                            {error}
                        </div>
                    )}
                </div>
            </section>

            <footer className="landing-footer">
                <div className="container">
                    <p>RasoiAI — built for Indian home cooking</p>
                </div>
            </footer>
        </div>
    );
};

export default ProfilePage;
