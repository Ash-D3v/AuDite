import React, { useState, useEffect } from 'react';
import './Login.css';
import img4 from "../../assets/photo4.png"
import { db } from "./Firebase";
import { collection, addDoc, query, where, getDocs } from 'firebase/firestore';


function Login() {
    const [activeTab, setActiveTab] = useState('login');
    const [selectedRole, setSelectedRole] = useState('');

    const showLogin = () => setActiveTab('login');
    const showSignup = () => setActiveTab('signup');
    
    const handleRoleChange = (e) => {
        const role = e.target.value;
        setSelectedRole(role);
        const userIdLabel = document.getElementById('userIdLabel');
        const userIdInput = document.getElementById('userIdInput');
        
        if (role === 'admin') {
            userIdLabel.textContent = '📧 Email';
            userIdInput.placeholder = 'Enter your email';
            userIdInput.type = 'email';
        } else if (role === 'doctors') {
            userIdLabel.textContent = '🆔 Doctor ID';
            userIdInput.placeholder = 'Enter Doctor ID (e.g., DR8A3F2B1C)';
            userIdInput.type = 'text';
        } else {
            userIdLabel.textContent = '📧 Licence ID';
            userIdInput.placeholder = 'Enter licence Id';
            userIdInput.type = 'text';
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
            
            console.log('UserId:', userId, 'Password:', password);
            
            button.textContent = 'Signing In...';
            button.disabled = true;
            
            const role = formData.get('role');
            
            if (role === 'doctor') {
                const doctorsQuery = query(
                    collection(db, 'doctors'),
                    where('doctorId', '==', userId),
                    where('password', '==', password)
                );
                getDocs(doctorsQuery)
                    .then((querySnapshot) => {
                        if (!querySnapshot.empty) {
                            const doctorData = querySnapshot.docs[0].data();
                            localStorage.setItem('currentUser', JSON.stringify({
                                ...doctorData,
                                id: querySnapshot.docs[0].id
                            }));
                            setTimeout(() => {
                                window.location.href = '/dashboard';
                            }, 1500);
                        } else {
                            setTimeout(() => {
                                alert('Invalid Doctor ID or password!');
                                button.textContent = originalText;
                                button.disabled = false;
                            }, 1500);
                        }
                    })
                    .catch((error) => {
                        console.error('Error checking doctor credentials:', error);
                        setTimeout(() => {
                            alert('Login error. Please try again.');
                            button.textContent = originalText;
                            button.disabled = false;
                        }, 1500);
                    });
                return;
            }
               else if (userId === 'user1234' && password === '1234' && role === 'user') {
                setTimeout(() => {
                    window.location.href = '/user';
                }, 1500);
            } else if (role === 'admin') {
                // Check admin credentials from Firestore
                const adminQuery = query(
                    collection(db, 'admins'),
                    where('email', '==', userId),
                    where('password', '==', password)
                );
                
                getDocs(adminQuery)
                    .then((querySnapshot) => {
                        if (!querySnapshot.empty) {
                            setTimeout(() => {
                                window.location.href = '/admindashboard';
                            }, 1500);
                        } else {
                            setTimeout(() => {
                                alert('Invalid admin credentials!');
                                button.textContent = originalText;
                                button.disabled = false;
                            }, 1500);
                        }
                    })
                    .catch((error) => {
                        console.error('Error checking admin credentials:', error);
                        setTimeout(() => {
                            alert('Login error. Please try again.');
                            button.textContent = originalText;
                            button.disabled = false;
                        }, 1500);
                    });
                return; // Exit early for admin login
            } else {
                setTimeout(() => {
                    alert('Invalid credentials or role mismatch!');
                    button.textContent = originalText;
                    button.disabled = false;
                }, 1500);
            }
        } else {
            // Admin signup
            const formData = new FormData(e.target);
            const firstName = formData.get('firstName');
            const lastName = formData.get('lastName');
            const email = formData.get('email');
            const password = formData.get('password');
            const confirmPassword = formData.get('confirmPassword');
            
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            button.textContent = 'Creating Admin Account...';
            button.disabled = true;
            
            // Store admin data in Firestore
            const adminData = {
                firstName,
                lastName,
                email,
                password, // In production, hash this password
                role: 'admin',
                createdAt: new Date().toISOString(),
                licenseId: `ADMIN_${Date.now()}` // Generate admin ID
            };
            
            addDoc(collection(db, 'admins'), adminData)
                .then(() => {
                    setTimeout(() => {
                        alert(`Admin account created successfully! Use your email and password to login.`);
                        button.textContent = originalText;
                        button.disabled = false;
                        setActiveTab('login');
                    }, 1500);
                })
                .catch((error) => {
                    console.error('Error creating admin account:', error);
                    alert('Error creating account. Please try again.');
                    button.textContent = originalText;
                    button.disabled = false;
                });
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
                        <button className={`tab ${activeTab === 'signup' ? 'active' : ''}`} onClick={showSignup}>🔐Admin</button>
                    </div>

                    <div className="form-content-wrapper">
                        <div className={`form-content ${activeTab === 'login' ? 'active' : 'inactive'}`} id="loginForm">
                            <div className="form-header">
                                <h2>Welcome Back! </h2>
                                <p>Continue your wellness journey</p>
                            </div>
                            <form onSubmit={(e) => handleSubmit(e, true)}>
                                 <div className="input-group">
                                    <label>👥 Role</label>
                                    <select name="role" onChange={handleRoleChange} required>
                                        <option value="">Select your role</option>
                                        <option value="doctor">Doctor</option>
                                        <option value="user">User/Patient</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <div className="input-group">
                                    <label id="userIdLabel">📧 Licence ID</label>
                                    <input type="text" name="userId" id="userIdInput" placeholder='Enter licence Id' required />
                                </div>
                                <div className="input-group">
                                    <label>🔒 Password</label>
                                    <input type="password" name="password" placeholder='Enter your password'required />
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
                                <div className="input-group">
                                    <label>📧 Email Address</label>
                                    <input type="email" name="email" placeholder="Enter your email" required />
                                </div>
                                <div className="input-group">
                                    <label>🔒 password</label>
                                    <input type="password" name="password" placeholder="Enter your password" required />
                                </div>
                                <div className="input-group">   
                                    <label>🔒 confirm password</label>
                                    <input type="password" name="confirmPassword" placeholder="Confirm password" required />
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
