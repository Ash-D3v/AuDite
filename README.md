# 🏆 AuDite - Ayurvedic Diet Management Software

*Smart India Hackathon 2024 - Winning Solution*  
*AI-powered Ayurvedic diet chart generation and patient management system*

## 🌟 Overview

AuDite is a comprehensive solution for Ayurvedic hospitals to create, manage, and organize patient-specific diet charts with both accuracy and ease. The platform integrates modern nutritional metrics with Ayurvedic dietary principles, including caloric value, food properties (Hot/Cold, Easy/Difficult to digest), and the six tastes (Rasa).

## 🚀 Key Features

- **AI-Powered Analysis**: 5 ML models for comprehensive Ayurvedic analysis
- **Comprehensive Food Database**: 8,000+ food items covering Indian, multicultural, and international cuisines
- **Automated Diet Chart Generation**: Nutritionally balanced, Ayurveda-compliant plans
- **Patient Management**: Complete profiles with health parameters and dietary preferences
- **Real-time Analytics**: Progress tracking and compliance monitoring
- **PDF Reports**: Printable diet charts and comprehensive reports
- **Mobile Support**: Responsive design for mobile and tablet devices

## 🏗️ Architecture

### Backend (FastAPI + Firebase)
- **Framework**: FastAPI with async support
- **Database**: Firestore (NoSQL)
- **Authentication**: Firebase Auth
- **ML Models**: PyTorch, TensorFlow, scikit-learn
- **Storage**: Google Cloud Storage
- **Deployment**: Docker + Cloud Run

### Frontend (React + Vite)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS
- **State Management**: React Hooks

## 📁 Clean Project Structure

```
AuDite/
├── backend/                    # FastAPI Backend
│   ├── app.py                 # Main FastAPI application
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   └── src/
│       ├── middleware/        # Authentication, rate limiting, logging
│       ├── routers/          # API endpoints
│       ├── services/         # Business logic and ML models
│       │   ├── ml/          # Machine learning services
│       │   └── ayurvedic/   # Ayurvedic calculation services
│       ├── models/          # Data models and schemas
│       ├── utils/           # Utility functions
│       └── tests/           # Unit and integration tests
├── frontend/                  # React Frontend
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.js       # Vite configuration
│   └── index.html           # Main HTML file
├── model/                    # ML Model files
│   ├── dosha_classifier.pkl
│   ├── ayurvedic_compatibility_gnn.h5
│   ├── compatibility_encoders.pkl
│   └── agni_predictor.h5
├── Dockerfile               # Backend containerization
├── docker-compose.yml       # Local development setup
├── requirements.txt         # Python dependencies
├── nginx.conf              # Reverse proxy configuration
└── README.md               # This file
```

## 🤖 ML Models

| Model | Algorithm | Accuracy | Purpose |
|-------|-----------|----------|---------|
| **DoshaClassifier** | Random Forest + XGBoost | 92.3% | Prakriti (constitution) analysis |
| **RasaRecommender** | Neural Collaborative Filtering | 89.7% | Six tastes personalization |
| **CompatibilityEngine** | Graph Neural Network | 97.0% | Viruddha Ahara detection |
| **NutrientCalculator** | Gradient Boosting | 94.5% | Macro/micronutrient estimation |
| **AgniPredictor** | LSTM Time Series | 88.2% | Digestive power assessment |

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Firebase project with Firestore enabled

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Firebase**
   - Create a Firebase project
   - Download Firebase Admin SDK key
   - Place it in `secrets/firebase-adminsdk.json`
   - Update `GOOGLE_CLOUD_PROJECT` in `.env`

4. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

5. **Or run locally**
   ```bash
   uvicorn app:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## 📚 API Documentation

Once the backend server is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile

#### Patient Management
- `POST /patients` - Create patient profile
- `GET /patients` - List patients
- `GET /patients/{patient_id}` - Get patient details
- `PUT /patients/{patient_id}` - Update patient info
- `POST /patients/{patient_id}/analyze-prakriti` - Analyze dosha constitution

#### Diet Management
- `POST /diet/analyze-prakriti` - Analyze patient constitution
- `POST /diet/analyze-foods` - Analyze food compatibility
- `POST /diet/predict-agni-trend` - Predict Agni trend using LSTM model
- `POST /diet/assess-daily-agni` - Assess daily Agni using ML model
- `POST /diet/predict-meal-agni-impact` - Predict meal impact on Agni
- `POST /diet/generate` - Generate AI-powered diet chart
- `GET /diet/charts/{chart_id}` - Get diet chart
- `PUT /diet/charts/{chart_id}` - Update diet chart

#### Analytics & Reports
- `GET /analytics/patient/{patient_id}` - Patient analytics
- `GET /analytics/compliance/{chart_id}` - Compliance metrics
- `GET /reports/diet-chart/{chart_id}/pdf` - Generate PDF report

## 🧪 Testing

### Backend Tests
```bash
cd backend
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests
```bash
cd frontend
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with docker-compose
docker-compose up --build

# Or build individual services
docker build -t audite-backend .
docker run -p 8000:8000 audite-backend
```

### Production Deployment
```bash
# Backend - Deploy to Cloud Run
gcloud run deploy audite-backend --source backend/

# Frontend - Deploy to Vercel/Netlify
cd frontend
npm run build
# Deploy dist/ folder to your hosting service
```

## 📊 Monitoring & Analytics

- **Health Check**: `GET /health`
- **Structured Logging**: JSON format with correlation IDs
- **Error Tracking**: Sentry integration
- **Performance Metrics**: Response times, error rates, ML model accuracy

## 🔒 Security & Compliance

- **Authentication**: Firebase Auth with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: AES-256 encryption for sensitive data
- **HIPAA Compliance**: Comprehensive audit logging
- **Rate Limiting**: Firestore-based rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **Team AyurTech** - Smart India Hackathon 2024
- **Ayurvedic Practitioners** - For domain expertise
- **Open Source Community** - For amazing tools and libraries

## 📞 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/Ash-D3v/AuDite/issues)
- **Email**: support@audite.io

---

*"Bridging ancient Ayurvedic wisdom with modern AI technology for holistic healthcare"*

**Built with ❤️ by Team AyurTech - Smart India Hackathon 2024**

## 🔗 Repository Links

- **GitHub Repository**: [https://github.com/Ash-D3v/AuDite](https://github.com/Ash-D3v/AuDite)
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
