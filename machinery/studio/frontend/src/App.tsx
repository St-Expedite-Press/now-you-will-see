import { Routes, Route, Navigate } from 'react-router-dom'
import Login from '@/pages/Login'
import StudioHome from '@/pages/StudioHome'
import ProjectSelect from '@/pages/ProjectSelect'
import ProjectConfig from '@/pages/ProjectConfig'
import ProjectEditor from '@/pages/ProjectEditor'
import IngestProjectPicker from '@/pages/IngestProjectPicker'
import IngestDocuments from '@/pages/IngestDocuments'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<StudioHome />} />
      <Route path="/login" element={<Login />} />
      <Route path="/ingest" element={<IngestProjectPicker />} />
      <Route path="/projects" element={<ProjectSelect />} />
      <Route path="/projects/new" element={<ProjectConfig />} />
      <Route path="/projects/:projectId/ingest" element={<IngestDocuments />} />
      <Route path="/projects/:projectId" element={<ProjectEditor />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
