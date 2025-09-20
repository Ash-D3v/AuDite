import React, { useEffect, useRef } from 'react'
import './ServiceSection.css'
import img1 from '../../assets/photo9.png'
import img2 from '../../assets/photo10.png'
import img3 from '../../assets/photo11.png'
import img4 from '../../assets/photo12.png'
import img5 from '../../assets/photo13.png'

const ServiceSection = React.forwardRef((props, ref) => {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate')
          }
        })
      },
      { threshold: 0.1 }
    )

    const serviceItems = ref?.current?.querySelectorAll('.service-item')
    serviceItems?.forEach((item) => observer.observe(item))

    return () => observer.disconnect()
  }, [ref])
  const services = [
    {
      id: 1,
      image: img1,
      title: "Personalized Diet Plans",
      description: "AI-powered custom meal plans tailored to your body type and health goals",
      icon: "🍽️"
    },
    {
      id: 2,
      image: img2,
      title: "Dashboard to Manage patient",
      description: "Expert guidance from certified Ayurvedic practitioners for holistic wellness",
      icon: "🧘‍♀️"
    },
    {
      id: 3,
      image: img3,
      title: " Track Patient",
      description: "Smart tracking system to monitor your daily nutrition and progress",
      icon: "📊"
    },
    {
      id: 4,
      image: img4,
      title: "Patient health record",
      description: "Natural herbal solutions and supplements for optimal health",
      icon: "🌿"
    },
    {
      id: 5,
      image: img5,
      title: "Recipies",
      description: "Complete lifestyle transformation with mindful eating and wellness habits",
      icon: "⚖️"
    }
  ]

  return (
    <section className="service-section" ref={ref}>
      <div className="service-container">
        <div className="service-header">
          <h2 className="service-title">Our <span className="highlight">Services</span></h2>
          <p className="service-subtitle">Comprehensive Ayurvedic wellness solutions for your health journey</p>
        </div>
        
        <div className="services-list">
          {services.map((service, index) => (
            <div key={service.id} className={`service-item ${index % 2 === 0 ? 'left-image' : 'right-image'} item-${index + 1}`}>
              <div className="service-image-wrapper">
                <img src={service.image} alt={service.title} className="service-image" />
                <div className="image-glow"></div>
              </div>
              <div className="service-text">
                <div className="service-icon-badge">{service.icon}</div>
                <h3 className="service-title-main">{service.title}</h3>
                <p className="service-desc">{service.description}</p>
                <button className="service-cta">Explore Service</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
})

ServiceSection.displayName = 'ServiceSection'
export default ServiceSection
