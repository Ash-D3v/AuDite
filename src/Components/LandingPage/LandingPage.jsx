import React, { useRef } from 'react'
import { Link } from 'react-router-dom'
import './LandingPage.css'
import Navbar from '../Navbar/Navbar'
import img1 from "../../assets/photo6.png"
import img2 from "../../assets/photo7.png"
import img3 from "../../assets/photo8.png"
import ServiceSection from './ServiceSection'
import Footer from '../Footer/Footer'

const LandingPage = () => {
  const serviceRef = useRef(null)

  const scrollToServices = () => {
    serviceRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  return (
     <>
     <Navbar onServicesClick={scrollToServices}/>
        <div className="landing-page">
            <div className="hero-section">
                <div className="content">
                    <h1 className="title">Diet Charts made Easy with <span className="highlight">Ayurdiet</span></h1>
                    <p className="subtitle">Personalized Ayurvedic diet plans powered by AI to nourish your body, mind & soul</p>
                    <div className="features-preview">
                        <span className="feature">🌿 Natural Healing</span>
                        <span className="feature">🧘 Holistic Wellness</span>
                        <span className="feature">⚖️ Perfect Balance</span>
                    </div>
                    <Link to="/login" className="get-started-button">Start prescribing now</Link>
                </div>
                <div className="image-container">
                    <div className="image-cards">
                        <div className="card left">
                            <img src={img1} alt="Ayurvedic wellness" className="card-image" />
                        </div>
                        <div className="card center">
                            <img src={img2} alt="Ayurvedic wellness" className="card-image" />
                        </div>
                        <div className="card right">
                            <img src={img3} alt="Ayurvedic wellness" className="card-image" />
                        </div>
                    </div>
                    <div className="image-overlay">
                        <h3>Ancient Wisdom</h3>
                        <p>Modern Technology</p>
                    </div>
                     
                </div>
            </div>
 <ServiceSection ref={serviceRef}/>
        </div>
        <Footer/>
    </>
  )
}

export default LandingPage;
