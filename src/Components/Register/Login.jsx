import React, { useState, useEffect } from 'react';
import './Login.css';
import img4 from "../../assets/photo4.png"


function Login() {
    const [activeTab, setActiveTab] = useState('login');
    const [selectedRole, setSelectedRole] = useState('');

    const showLogin = () => setActiveTab('login');
    const showSignup = () => setActiveTab('signup');
    
    const handleRoleChange = (e) => {
        const role = e.target.value;
        setSelectedRole(role);
        const doctorFields = document.querySelectorAll('.doctor-only');
        const licenseInput = document.querySelector('input[name="licenseId"]');
        const specializationSelect = document.querySelector('select[name="specialization"]');
        
        if (role === 'doctor') {
            doctorFields.forEach(field => field.style.display = 'block');
            if (licenseInput) licenseInput.required = true;
            if (specializationSelect) specializationSelect.required = true;
        } else {
            doctorFields.forEach(field => field.style.display = 'none');
            if (licenseInput) licenseInput.required = false;
            if (specializationSelect) specializationSelect.required = false;
        }
    };

   

    useEffect(() => {
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('input-focused');
            });
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('input-focused');
            });
        });
    }, []);

    const handleSubmit = (e, isLogin) => {
        e.preventDefault();
        const button = e.target.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        if (isLogin) {
            const formData = new FormData(e.target);
            const userId = formData.get('userId');
            const password = formData.get('password');
            
            console.log('UserId:', userId, 'Password:', password); // Debug log
            
            button.textContent = 'Signing In...';
            button.disabled = true;
            
            if (userId === 'doctor123' && password === 'password') {
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else if (userId === 'user1234' && password === '1234') {
                setTimeout(() => {
                    window.location.href = '/user';
                }, 1500);
            } else {
                setTimeout(() => {
                    alert('Invalid credentials! Use: doctor123/password or user1234/1234');
                    button.textContent = originalText;
                    button.disabled = false;
                }, 1500);
            }
        } else {
          
            const formData = new FormData(e.target);
            const licenseId = formData.get('licenseId');
            const email = formData.get('email');
            
            button.textContent = 'Verifying License...';
            button.disabled = true;
         
            setTimeout(() => {
                button.textContent = 'Sending Credentials...';
                
                setTimeout(() => {
                    alert(`Registration successful! Login credentials have been sent to ${email}. Please check your email and use the provided credentials to sign in.`);
                    button.textContent = originalText;
                    button.disabled = false;
                    setActiveTab('login'); 
                }, 2000);
            }, 2000);
        }
    };

    return (
        <div className="login-signup-page" style={{backgroundImage: `url(${img4})`}}>
            <div className="background-overlay"></div>
            <div className="container">
                <div className="header fade-in">
                    <h1 className="title">Ayurdiet-Diet plan</h1>
                    <p className="subtitle">suggest diet plans and predict  </p>
                    <div className="divider"></div>
                </div>

                <div className="form-container glass-morphism slide-in">
                    <div className={`tabs ${activeTab}`}>
                        <button className={`tab ${activeTab === 'login' ? 'active' : ''}`} onClick={showLogin}>🔐 Sign In</button>
                        <button className={`tab ${activeTab === 'signup' ? 'active' : ''}`} onClick={showSignup}>🔐Sign Up</button>
                    </div>

                    <div className="form-content-wrapper">
                        <div className={`form-content ${activeTab === 'login' ? 'active' : 'inactive'}`} id="loginForm">
                            <div className="form-header">
                                <h2>Welcome Back! </h2>
                                <p>Continue your wellness journey</p>
                            </div>
                            <form onSubmit={(e) => handleSubmit(e, true)}>
                                <div className="input-group">
                                    <label>📧 Licence ID</label>
                                    <input type="text" name="userId" placeholder="Enter your Id (try: doctor123 or user1234)" required />
                                </div>
                                <div className="input-group">
                                    <label>🔒 Password</label>
                                    <input type="password" name="password" placeholder="Enter your password (try: password or 1234)" required />
                                </div>
                                <div className="form-footer">
                                    <label>
                                        <input type="checkbox" />
                                        Remember me
                                    </label>
                                    <a href="#">Forgot password?</a>
                                </div>
                                <button type="submit"> Sign In </button>
                            </form>
                            <div className="switch">
                                <p>New to Ayurdiet ?</p>
                                <button onClick={showSignup}>Create your account</button>
                            </div>
                        </div>
                        <div className={`form-content ${activeTab === 'signup' ? 'active' : 'inactive'}`} id="signupForm">
                            <div className="form-header">
                                <h2>Join Our Community! </h2>
                                <p>Begin your wellness transformation</p>
                            </div>
                            <form onSubmit={(e) => handleSubmit(e, false)}>
                                <div className="input-group">
                                    <label>👥 Role</label>
                                    <select name="role" onChange={handleRoleChange} required>
                                        <option value="">Select your role</option>
                                        <option value="doctor">Doctor</option>
                                        <option value="user">User/Patient</option>
                                    </select>
                                </div>
                                
                                <div className="input-grid">
                                    <div className="input-group1">
                                        <label>👤 First Name</label>
                                        <input type="text" name="firstName" placeholder="First name" required />
                                    </div>
                                    <div className="input-group1">
                                        <label>👤 Last Name</label>
                                        <input type="text" name="lastName" placeholder="Last name" required />
                                    </div>
                                </div>
                
                                <div className="input-group doctor-only" style={{display: 'none'}}>
                                    <label>🏥 Medical License ID</label>
                                    <input type="text" name="licenseId" placeholder="Enter your medical license number" />
                                </div>
                                <div className="input-group">
                                    <label>📧 Email Address</label>
                                    <input type="email" name="email" placeholder="Enter your email" required />
                                </div>
                                <div className="input-group doctor-only" style={{display: 'none'}}>
                                    <label>🩺 Specialization</label>
                                    <select name="specialization">
                                        <option value="">Select your specialization</option>
                                        <option value="ayurveda">Ayurveda</option>
                                        <option value="general">General Medicine</option>
                                        <option value="nutrition">Nutrition & Dietetics</option>
                                        <option value="internal">Internal Medicine</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div className="checkbox-group">
                                    <label>
                                        <input type="checkbox" required />
                                        I agree to the  <span><a href="#">Terms of Service</a> </span>and <a href="#">Privacy Policy</a>
                                    </label>
                                </div>
                                <button type="submit">Sign Up</button>
                            </form>
                            <div className="switch">
                                <p>Already have an account?</p>
                                <button onClick={showLogin}>Sign in!</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="features">
                    <div className="feature-card">
                        <div className="icon">🌿</div>
                        <p className="feature-title">Diet plans</p>
                        <p className="feature-desc">Ancient wisdom</p>
                    </div>
                    <div className="feature-card">
                        <div className="icon">🧘</div>
                        <p className="feature-title">Holistic Wellness</p>
                        <p className="feature-desc">Complete healing</p>
                    </div>
                    <div className="feature-card">
                        <div className="icon">⚖️</div>
                        <p className="feature-title">Mind-Body Balance</p>
                        <p className="feature-desc">Perfect harmony</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
