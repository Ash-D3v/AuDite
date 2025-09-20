import React, { useState, useEffect } from 'react'
import './Overall.css'
import { UserPlus } from 'lucide-react';
import { NotebookPen } from 'lucide-react';
import { CalendarRange } from 'lucide-react';

const Overall = () => {
    const [doctorName, setDoctorName] = useState('');

    useEffect(() => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser'));
        if (currentUser && currentUser.name) {
            setDoctorName(currentUser.name);
        }
    }, []);

    const RecentActivity= [
    { id: 'New patient added', label: 'Dashboard', icon: <UserPlus /> },
    { id: 'Diet plan updated', label: 'Patients', icon: <NotebookPen />},
    { id: 'Appointment scheduled', label: 'Diet Plans', icon: <CalendarRange /> },
  ]
  return (
    <>
      <div className="content-header">
        <h1>Welcome,  {doctorName}</h1>
      </div>
      <div className="overall-container">
        <div className="con-body">
          <h1>Total Patients</h1>
          <div className="sub-head">??</div>
        </div>

        <div className="con-body">
          <h1>Active Diet Plans</h1>
          <div className="sub-head">??</div>
        </div>

        <div className="con-body">
          <h1>Upcoming Appointments</h1>
          <div className="sub-head">??</div>
        </div>
      </div>
      <div className="content-header1">
        <h1>Recent Activity</h1>
      </div>
      <div className="recent-activities">
        {RecentActivity.map((activity, index) => (
          <div key={index} className="recent-content">
            <div className="activity-icon">{activity.icon}</div>
            <div className="activity-details">
              <h2>{activity.id}</h2>
              <div className="subheading">Just now</div>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}

export default Overall
