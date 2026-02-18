import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useState } from 'react';
import {
    fetchUserProfile,
    getFavourites,
    removeFavourite,
    getBookmarks,
    removeBookmark,
} from '../services/api';
import './ProfilePage.css';

const ProfilePage = ({ onNavigate }) => {
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

    const handleRecipeClick = (item) => {
        if (onNavigate) {
            onNavigate('recipe-detail', {
                recipe: {
                    recipe_id: item.recipe_id,
                    recipe: item.recipe_name,
                    ingredients: '',
                    instruction: '',
                },
            });
        }
    };

    if (isLoading || isSyncing) {
        return (
            <div className="profile-container">
                <div className="profile-card loading">
                    <div className="loader"></div>
                    <p>Loading profile...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="profile-container">
                <div className="profile-card error">
                    <p>Please log in to view your profile.</p>
                </div>
            </div>
        );
    }

    const renderList = (items, type) => {
        if (historyLoading) {
            return (
                <div className="history-loading">
                    <div className="loader"></div>
                    <p>Loading...</p>
                </div>
            );
        }

        if (items.length === 0) {
            return (
                <div className="history-empty">
                    <p>No {type} yet</p>
                    <p className="empty-hint">
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
                    <div key={item.recipe_id} className="saved-recipe-card">
                        <div
                            className="saved-recipe-info"
                            onClick={() => handleRecipeClick(item)}
                        >
                            <div className="saved-recipe-text">
                                <p className="saved-recipe-name">
                                    {item.recipe_name || `Recipe #${item.recipe_id}`}
                                </p>
                                <p className="saved-recipe-date">
                                    Added {new Date(item.created_at).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                        <button
                            className="remove-btn"
                            onClick={() =>
                                type === 'favourites'
                                    ? handleRemoveFavourite(item.recipe_id)
                                    : handleRemoveBookmark(item.recipe_id)
                            }
                            title="Delete"
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
        <div className="profile-container">
            <div className="profile-card">
                <div className="profile-header">
                    <img src={user.picture} alt={user.name} className="profile-avatar" />
                    <div className="profile-info">
                        <h1>{user.name}</h1>
                        <p className="email">{user.email}</p>
                        <span className="badge">Authenticated</span>
                    </div>
                </div>

                <div className="profile-content">
                    {/* ─── Favourites & Bookmarks Tabs ──────────────── */}
                    <section className="profile-section history-section">
                        <h2>My Recipes</h2>
                        <div className="history-tabs">
                            <button
                                className={`tab-btn ${activeTab === 'favourites' ? 'active' : ''}`}
                                onClick={() => setActiveTab('favourites')}
                            >
                                Favourites
                                {favourites.length > 0 && (
                                    <span className="tab-count">{favourites.length}</span>
                                )}
                            </button>
                            <button
                                className={`tab-btn ${activeTab === 'bookmarks' ? 'active' : ''}`}
                                onClick={() => setActiveTab('bookmarks')}
                            >
                                Bookmarks
                                {bookmarks.length > 0 && (
                                    <span className="tab-count">{bookmarks.length}</span>
                                )}
                            </button>
                        </div>

                        <div className="tab-content">
                            {activeTab === 'favourites'
                                ? renderList(favourites, 'favourites')
                                : renderList(bookmarks, 'bookmarks')}
                        </div>
                    </section>

                    {error && <p className="error-msg">{error}</p>}
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
