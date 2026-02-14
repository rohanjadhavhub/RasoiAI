import { useAuth0 } from '@auth0/auth0-react';
import './LoginPage.css';

const LoginPage = () => {
    const { loginWithRedirect, isLoading } = useAuth0();

    if (isLoading) {
        return (
            <div className="login-container">
                <div className="login-card">
                    <div className="loader"></div>
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>Welcome to RasoiAI</h1>
                <p>Sign in to access personalized features and save your recipe journey.</p>

                <div className="auth-buttons">
                    <button
                        className="login-button primary"
                        onClick={() => loginWithRedirect()}
                    >
                        Sign In / Register
                    </button>
                </div>

                <div className="login-features">
                    <div className="feature">
                        <span className="feature-icon">✨</span>
                        <p>Smart Recommendations</p>
                    </div>
                    <div className="feature">
                        <span className="feature-icon">📸</span>
                        <p>Vision AI Analysis</p>
                    </div>
                    <div className="feature">
                        <span className="feature-icon">💬</span>
                        <p>AI Chef Chat</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
