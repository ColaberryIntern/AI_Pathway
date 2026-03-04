import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ProfileSelectionPage from './pages/ProfileSelectionPage'
import AnalysisPage from './pages/AnalysisPage'
import LearningPathPage from './pages/LearningPathPage'
import DashboardPage from './pages/DashboardPage'
import JDTestPage from './pages/JDTestPage'
import LearningDashboardPage from './pages/LearningDashboardPage'
import LessonPage from './pages/LessonPage'
import SkillGenomePage from './pages/SkillGenomePage'
import CuriosityFeedPage from './pages/CuriosityFeedPage'

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
          <Route path="learn/:pathId" element={<LearningDashboardPage />} />
          <Route path="learn/:pathId/lesson/:lessonId" element={<LessonPage />} />
          <Route path="genome/:userId" element={<SkillGenomePage />} />
          <Route path="curiosity/:userId" element={<CuriosityFeedPage />} />
          <Route path="jd-test" element={<JDTestPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
