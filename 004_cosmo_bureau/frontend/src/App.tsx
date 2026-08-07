import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Header } from './components/Header'
import { Cosmonauts } from './pages/Cosmonauts'
import { EarthMap } from './pages/EarthMap'
import { Hangar } from './pages/Hangar'
import { Landing } from './pages/Landing'
import { Missions } from './pages/Missions'
import { RocketDetail } from './pages/RocketDetail'
import { StationDetail } from './pages/StationDetail'

export default function App() {
  return (
    <BrowserRouter>
      <div className="starfield crt relative min-h-screen">
        <Header />
        <main className="relative z-10">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/cosmonauts" element={<Cosmonauts />} />
            <Route path="/earth" element={<EarthMap />} />
            <Route path="/stations/:id" element={<StationDetail />} />
            <Route path="/rockets/:id" element={<RocketDetail />} />
            <Route path="/missions" element={<Missions />} />
            <Route path="/hangar" element={<Hangar />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
