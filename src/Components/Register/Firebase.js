// src/firebase/config.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyAGy8KxmFvVP-3tdV_9e59HccP3nuFtJi8",
  authDomain: "ayudiet-505fa.firebaseapp.com",
  projectId: "ayudiet-505fa",
  storageBucket: "ayudiet-505fa.appspot.com", // ✅ fixed
  messagingSenderId: "107247702220",
  appId: "1:107247702220:web:74d0149fa46191465c3269",
  measurementId: "G-1PPDS25LTR"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Export Firebase services
const db = getFirestore(app);
const auth = getAuth(app);
const storage = getStorage(app);

export { app, db, auth, storage };
