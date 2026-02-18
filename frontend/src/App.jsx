import { useState, useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import './App.css';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import IngredientsPage from './pages/IngredientsPage';
import RecipesPage from './pages/RecipesPage';
import RecipeDetailPage from './pages/RecipeDetailPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';

function Header({ onNavigate, currentPage }) {
  const { isAuthenticated, loginWithRedirect, logout, user } = useAuth0();

  return (
    <header className="app-header">
      <div className="logo" onClick={() => onNavigate('landing')}>
        Rasoi<span>AI</span>
      </div>
      <nav>
        <button
          className={currentPage === 'landing' ? 'active' : ''}
          onClick={() => onNavigate('landing')}
        >
          Home
        </button>
        {isAuthenticated ? (
          <div className="user-menu">
            <button
              className={currentPage === 'profile' ? 'active' : ''}
              onClick={() => onNavigate('profile')}
            >
              Profile
            </button>
            <button className="logout-btn" onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>
              Logout
            </button>
            <img src={user.picture} alt={user.name} className="nav-avatar" onClick={() => onNavigate('profile')} />
          </div>
        ) : (
          <button className="login-btn" onClick={() => onNavigate('login')}>
            Login
          </button>
        )}
      </nav>
    </header>
  );
}

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [sessionId, setSessionId] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [selectedRecipe, setSelectedRecipe] = useState(null);

  const navigate = useCallback((page, data = {}) => {
    if (data.sessionId) setSessionId(data.sessionId);
    if (data.ingredients) setIngredients(data.ingredients);
    if (data.recommendations) setRecommendations(data.recommendations);
    if (data.recipe) setSelectedRecipe(data.recipe);
    setCurrentPage(page);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage onNavigate={navigate} />;
      case 'upload':
        return <UploadPage onNavigate={navigate} />;
      case 'ingredients':
        return (
          <IngredientsPage
            sessionId={sessionId}
            ingredients={ingredients}
            onNavigate={navigate}
          />
        );
      case 'recipes':
        return (
          <RecipesPage
            sessionId={sessionId}
            recommendations={recommendations}
            onNavigate={navigate}
          />
        );
      case 'recipe-detail':
        return (
          <RecipeDetailPage
            recipe={selectedRecipe}
            sessionId={sessionId}
            onNavigate={navigate}
          />
        );
      case 'login':
        return <LoginPage />;
      case 'profile':
        return <ProfilePage onNavigate={navigate} />;
      default:
        return <LandingPage onNavigate={navigate} />;
    }
  };

  return (
    <div className="app">
      <Header onNavigate={navigate} currentPage={currentPage} />
      <main className="app-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
