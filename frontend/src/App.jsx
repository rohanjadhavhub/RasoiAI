import { useState, useCallback } from 'react';
import './App.css';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import IngredientsPage from './pages/IngredientsPage';
import RecipesPage from './pages/RecipesPage';
import RecipeDetailPage from './pages/RecipeDetailPage';

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
      default:
        return <LandingPage onNavigate={navigate} />;
    }
  };

  return (
    <div className="app">
      {renderPage()}
    </div>
  );
}

export default App;
