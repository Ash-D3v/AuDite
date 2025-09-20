import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'

const Navbar = ({ onServicesClick }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
        <nav className="navbar">
            
            <div className="navbar-logo">
                
              Ayudiet
            </div>
            <div className={`hamburger ${isOpen ? 'active' : ''}`} onClick={() => setIsOpen(!isOpen)}>
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul className={`navbar-links ${isOpen ? 'active' : ''}`}>
                <li><a href="/about">About</a></li>
                <li><a href="#" onClick={(e) => { e.preventDefault(); onServicesClick?.(); }}>Services</a></li>
                <li><a href="#" onClick={(e) => { e.preventDefault(); onServicesClick?.(); }}>contact</a></li>
                <Link to = "/Login"><li>Login</li></Link>
            </ul>
        </nav>
  )
}

export default Navbar
