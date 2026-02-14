import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useState } from 'react';
import { fetchUserProfile } from '../services/api';
import './ProfilePage.css';

const ProfilePage = () => {
    const { user, getAccessTokenSilently, isAuthenticated, isLoading } = useAuth0();
    const [dbUser, setDbUser] = useState(null);
    const [error, setError] = useState(null);
    const [isSyncing, setIsSyncing] = useState(true);

    useEffect(() => {
        const syncUser = async () => {
            if (isAuthenticated) {
                try {
                    const token = await getAccessTokenSilently();
                    const profile = await fetchUserProfile(token);
                    setDbUser(profile);
                } catch (err) {
                    console.error('Error syncing user:', err);
                    setError('Failed to sync profile with server');
                } finally {
                    setIsSyncing(false);
                }
            }
        };

        syncUser();
    }, [isAuthenticated, getAccessTokenSilently]);

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
                    <section className="profile-section">
                        <h2>Account Details</h2>
                        <div className="detail-row">
                            <span className="label">Auth Provider:</span>
                            <span className="value">{user.sub?.split('|')[0]}</span>
                        </div>
                        <div className="detail-row">
                            <span className="label">Backend ID:</span>
                            <span className="value">#{dbUser?.id || '...'}</span>
                        </div>
                        <div className="detail-row">
                            <span className="label">Member Since:</span>
                            <span className="value">{dbUser ? new Date(dbUser.created_at).toLocaleDateString() : '...'}</span>
                        </div>
                        <div className="detail-row">
                            <span className="label">Last Login:</span>
                            <span className="value">{dbUser ? new Date(dbUser.last_login).toLocaleTimeString() : '...'}</span>
                        </div>
                    </section>

                    {error && <p className="error-msg">{error}</p>}
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
