import { HashRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Home } from './pages/Home';
import { Weapons } from './pages/Weapons';
import { WeaponDetail } from './pages/WeaponDetail';
import { Armor } from './pages/Armor';
import { Perks } from './pages/Perks';
import { Mutations } from './pages/Mutations';
import { Consumables } from './pages/Consumables';
import { Chat } from './pages/Chat';
import { BuildPlanner } from './pages/BuildPlanner';
import './index.css';

function App() {
  return (
    <HashRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/weapons" element={<Weapons />} />
          <Route path="/weapons/:id" element={<WeaponDetail />} />
          <Route path="/armor" element={<Armor />} />
          <Route path="/perks" element={<Perks />} />
          <Route path="/mutations" element={<Mutations />} />
          <Route path="/consumables" element={<Consumables />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/builder" element={<BuildPlanner />} />
        </Routes>
      </Layout>
    </HashRouter>
  );
}

export default App;
