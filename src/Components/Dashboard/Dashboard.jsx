import React, { useState } from 'react'
import './Dashboard.css'
import { LayoutDashboard, User } from 'lucide-react';
import { Users } from 'lucide-react';
import { Utensils } from 'lucide-react';
import { Settings } from 'lucide-react';
import { UtensilsCrossed } from 'lucide-react';
import Overall from './Overall';



const Dashboard = () => {
  const [activeSection, setActiveSection] = useState('dashboard')

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard /> },
    { id: 'patients', label: 'Patients', icon: <Users /> },
    { id: 'dietplans', label: 'Diet Plans', icon: <UtensilsCrossed /> },
    { id: 'recipes', label: 'Recipes', icon: <Utensils /> },
    { id: 'settings', label: 'Settings', icon: <Settings /> }
  ]

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-logo"> 📊 Ayudiet</h2>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => setActiveSection(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>
        
      
      <div className="main-content">
        
        
        <div className="content-body">
          {activeSection === 'dashboard' && <div><Overall/></div>}
          {activeSection === 'patients' && <div>Patients Content</div>}
          {activeSection === 'dietplans' && <div>Diet Plans Content</div>}
          {activeSection === 'recipes' && <div>Recipes Content</div>}
          {activeSection === 'settings' && <div>Settings Content</div>}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
