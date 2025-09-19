import React from 'react'
import './Footer.css'
import { Instagram } from 'lucide-react'
import { Facebook } from 'lucide-react'
import { Linkedin } from 'lucide-react'



const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-logo">Ayurdiet</h3>
            <p className="footer-desc">Transform your health with personalized Ayurvedic diet plans powered by AI</p>
            <div className="social-links">
              <a href="#" className="social-link"><Instagram /></a>
              <a href="#" className="social-link"><Facebook/></a>
              <a href="#" className="social-link"><Linkedin/></a>
            </div>
          </div>
          
          <div className="footer-section">
            <h4 className="footer-title">Services</h4>
            <ul className="footer-links">
              <li><a href="#">Diet Plans</a></li>
              <li><a href="#">Consultation</a></li>
              <li><a href="#">Nutrition Tracking</a></li>
              <li><a href="#">Herbal Remedies</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4 className="footer-title">Company</h4>
            <ul className="footer-links">
              <li><a href="#">About Us</a></li>
              <li><a href="#">Contact</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms of Service</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4 className="footer-title">Contact Info</h4>
            <div className="contact-info">
              <p>📧 Ayudiet@yahoo.com</p>
              <p>📞 +91 9945671198 </p>
              <p>📍 saheed Nagar, Bhubaneswar</p>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 Ayurdiet. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
