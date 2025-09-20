import './App.css'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Login from './Components/Register/Login'
import LandingPage from './Components/LandingPage/LandingPage'
import Dashboard from './Components/Dashboard/Dashboard'
import User from './Components/User/User'
import {AdminDashboard}  from './Components/Admin/AdminDashboard'

function App() {
  return (
    <>
    <Router> 
      <Routes>
        <Route path='/' element={<LandingPage/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/dashboard" element={<Dashboard/>}/>
        <Route path='user' element={<User/>}/>
        <Route path='admindashboard' element={<AdminDashboard/>}/>
      </Routes>
       </Router>
    </>
  )
}

export default App
