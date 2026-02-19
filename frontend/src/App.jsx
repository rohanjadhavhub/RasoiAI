import { useAuth0 } from '@auth0/auth0-react';
import { Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom';
import './App.css';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import IngredientsPage from './pages/IngredientsPage';
import RecipesPage from './pages/RecipesPage';
import RecipeDetailPage from './pages/RecipeDetailPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';

function Header() {
  const { isAuthenticated, logout, user } = useAuth0();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header className="app-header">
      <div className="logo" onClick={() => navigate('/')}>
        Rasoi<span>AI</span>
      </div>
      <nav>
        <Link
          className={location.pathname === '/' ? 'active' : ''}
          to="/"
        >
          Home
        </Link>
        {isAuthenticated ? (
          <div className="user-menu">
            <Link
              className={location.pathname === '/profile' ? 'active' : ''}
              to="/profile"
            >
              Profile
            </Link>
            <button className="logout-btn" onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>
              Logout
            </button>
            <img src={user.picture} alt={user.name} className="nav-avatar" onClick={() => navigate('/profile')} />
          </div>
        ) : (
          <Link className="login-btn" to="/login">
            Login
          </Link>
        )}
      </nav>
    </header>
  );
}

function App() {
  return (
    <div className="app">
      <Header />
      <main className="app-content">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/ingredients" element={<IngredientsPage />} />
          <Route path="/recipes" element={<RecipesPage />} />
          <Route path="/recipe" element={<RecipeDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
