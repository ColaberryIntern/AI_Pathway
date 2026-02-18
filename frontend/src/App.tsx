import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ProfileSelectionPage from './pages/ProfileSelectionPage'
import AnalysisPage from './pages/AnalysisPage'
import LearningPathPage from './pages/LearningPathPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="profiles" element={<ProfileSelectionPage />} />
          <Route path="analysis/:profileId" element={<AnalysisPage />} />
          <Route path="path/:pathId" element={<LearningPathPage />} />
          <Route path="dashboard/:userId" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
