import { Routes, Route, Navigate } from 'react-router-dom'
import Login from '@/pages/Login'
import ProjectSelect from '@/pages/ProjectSelect'
import ProjectConfig from '@/pages/ProjectConfig'
import ProjectEditor from '@/pages/ProjectEditor'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/projects" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/projects" element={<ProjectSelect />} />
      <Route path="/projects/new" element={<ProjectConfig />} />
      <Route path="/projects/:projectId" element={<ProjectEditor />} />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  )
}
