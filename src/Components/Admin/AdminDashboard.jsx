import React, { useState, useEffect } from 'react';
import { 
  Shield, Users, UserPlus, Stethoscope, User, LogOut, Trash2, X 
} from 'lucide-react';
import { db } from '../Register/Firebase';
import { collection, addDoc, onSnapshot, deleteDoc, doc } from 'firebase/firestore';
import { Link } from 'react-router-dom';

export function AdminDashboard({ 
  currentUser = { name: 'Admin User' }, 
  users = [], 
  onLogout = () => {}, 
  onAddUser = () => {}, 
  onDeleteUser = () => {} 
}) {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [createUserType, setCreateUserType] = useState('doctor');
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [doctors, setDoctors] = useState([]);

  const patients = users.filter(user => user.role === 'patient');

  useEffect(() => {
    const unsubscribe = onSnapshot(collection(db, 'doctors'), (snapshot) => {
      const doctorsList = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setDoctors(doctorsList);
    });
    return () => unsubscribe();
  }, []);


  const generateDoctorId = () => {
    return 'DR' + Math.random().toString(36).substr(2, 8).toUpperCase();
  };

  const handleCreateDoctor = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const doctorId = generateDoctorId();
    const doctorData = {
      doctorId,
      name: formData.get('name'),
      email: formData.get('email'),
      username: formData.get('username'),
      password: formData.get('password'),
      specialization: formData.get('specialization'),
      role: 'doctor',
      createdAt: new Date().toISOString(),
      createdBy: currentUser.name
    };

    try {
      await addDoc(collection(db, 'doctors'), doctorData);
      setIsCreateDialogOpen(false);
      setAlertMessage(`Doctor ${doctorData.name} created successfully with ID: ${doctorId}`);
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
      e.target.reset();
    } catch (error) {
      setAlertMessage('Error creating doctor account');
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
    }
  };

  const handleDeleteDoctor = async (doctorId, doctorName) => {
    try {
      await deleteDoc(doc(db, 'doctors', doctorId));
      setAlertMessage(`Doctor ${doctorName} has been deleted`);
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
    } catch (error) {
      setAlertMessage('Error deleting doctor');
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-green-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-r from-green-500 to-blue-600 p-2 rounded-xl shadow-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">Ayurdiet Management System</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-800">{currentUser.name}</p>
                <p className="text-xs text-gray-500">Administrator</p>
              </div>
              <Link to="/login">
              <button className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors duration-200 shadow-md">
                <LogOut className="w-4 h-4" /> Logout
              </button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showAlert && (
          <div className="mb-6 p-4 bg-green-100 border border-green-300 text-green-700 rounded-lg">{alertMessage}</div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-blue-100 p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center">
              <div className="bg-blue-100 p-3 rounded-full mr-4">
                <Stethoscope className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{doctors.length}</p>
                <p className="text-gray-600">Active Doctors</p>
              </div>
            </div>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-green-100 p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center">
              <div className="bg-green-100 p-3 rounded-full mr-4">
                <User className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{patients.length}</p>
                <p className="text-gray-600">Registered Patients</p>
              </div>
            </div>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-purple-100 p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center">
              <div className="bg-purple-100 p-3 rounded-full mr-4">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{users.length}</p>
                <p className="text-gray-600">Total Users</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Doctor Accounts</h2>
            <button 
              onClick={() => setIsCreateDialogOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors duration-200 shadow-md"
            >
              <UserPlus className="w-4 h-4" />
              Add Doctor
            </button>
          </div>
          {doctors.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Stethoscope className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No doctor accounts created yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Doctor ID</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Name</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Username</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Specialization</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Created</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.map((doctor) => (
                    <tr key={doctor.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">{doctor.doctorId}</span></td>
                      <td className="py-3 px-4 font-medium">{doctor.name}</td>
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">{doctor.username}</span></td>
                      <td className="py-3 px-4">{doctor.email}</td>
                      <td className="py-3 px-4">{doctor.specialization || 'Not specified'}</td>
                      <td className="py-3 px-4">{formatDate(doctor.createdAt)}</td>
                      <td className="py-3 px-4">
                        <button onClick={() => handleDeleteDoctor(doctor.id, doctor.name)} className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors duration-200">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Patient Accounts</h2>
          {patients.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <User className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No patient accounts created yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Name</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Username</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Phone</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Created</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient) => (
                    <tr key={patient.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{patient.name}</td>
                      <td className="py-3 px-4"><span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">{patient.username}</span></td>
                      <td className="py-3 px-4">{patient.email}</td>
                      <td className="py-3 px-4">{patient.phone || 'Not provided'}</td>
                      <td className="py-3 px-4">{formatDate(patient.createdAt)}</td>
                      <td className="py-3 px-4">
                        <button onClick={() => handleDeleteUser(patient.id, patient.name)} className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors duration-200">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Create Doctor Modal */}
        {isCreateDialogOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md mx-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Create Doctor Account</h3>
                <button 
                  onClick={() => setIsCreateDialogOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              
              <form onSubmit={handleCreateDoctor} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input 
                    type="text" 
                    name="name" 
                    required 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="Dr. John Smith"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input 
                    type="email" 
                    name="email" 
                    required 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="doctor@ayurdiet.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                  <input 
                    type="text" 
                    name="username" 
                    required 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="dr.johnsmith"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <input 
                    type="password" 
                    name="password" 
                    required 
                    minLength="6"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                  <input 
                    type="text" 
                    name="specialization" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="Cardiology, Nutrition, etc."
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button 
                    type="button"
                    onClick={() => setIsCreateDialogOpen(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors duration-200"
                  >
                    Create Doctor
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
