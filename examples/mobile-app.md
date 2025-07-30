# Example: Cross-Platform Mobile App with Backend API

This example shows how to build a fitness tracking mobile app with real-time sync and social features.

## Project Description
"Cross-platform fitness tracking mobile app with workout plans, progress tracking, social challenges, and wearable device integration"

## Development Workflow

### Phase 1: Strategic Planning

```bash
> Use the master-orchestrator agent to begin new project: "Cross-platform fitness tracking mobile app with workout plans, progress tracking, social challenges, and wearable device integration"
```

**Business Analysis Results**:
- Target market: 25-45 health-conscious individuals
- Monetization: Freemium model with premium plans
- Competition: MyFitnessPal, Strava, Nike Training
- Differentiator: AI-powered personalized workouts

### Phase 2: Mobile Architecture

```bash
> Use the mobile-development agent to design cross-platform architecture for iOS and Android
```

**Architecture Decisions**:
- Framework: React Native with native modules
- State management: Redux + Redux Persist
- Navigation: React Navigation v6
- Backend sync: GraphQL with Apollo Client

### Phase 3: Backend Development

```bash
> Use the backend-services agent to design API for mobile app with real-time sync
```

**API Implementation**:
```javascript
// GraphQL Schema highlights
type User {
  id: ID!
  profile: UserProfile!
  workouts: [Workout!]!
  challenges: [Challenge!]!
  devices: [WearableDevice!]!
}

type Workout {
  id: ID!
  type: WorkoutType!
  duration: Int!
  calories: Int
  heartRateData: [HeartRatePoint!]
  gpsData: [GPSPoint!]
}

type Challenge {
  id: ID!
  participants: [User!]!
  leaderboard: [LeaderboardEntry!]!
  endDate: DateTime!
}
```

### Phase 4: Mobile UI/UX

```bash
> Use the ui-ux-design agent to create mobile-first design system for fitness app
```

**Design Components**:
- Onboarding flow with fitness assessment
- Dashboard with daily goals
- Workout tracking interface
- Social feed and challenges
- Progress charts and analytics

### Phase 5: Core Features Implementation

```bash
> Use the production-frontend agent to implement React Native components
```

**Key Features Built**:

1. **Workout Tracking**
   - Real-time GPS tracking
   - Heart rate monitoring
   - Exercise form detection (using camera)
   - Voice coaching

2. **Social Features**
   - Friend challenges
   - Leaderboards
   - Activity sharing
   - Group workouts

3. **Device Integration**
   - Apple HealthKit
   - Google Fit
   - Fitbit API
   - Garmin Connect

### Phase 6: Performance & Security

```bash
> Use the performance-optimization agent to optimize mobile app performance
```

**Optimizations**:
- Lazy loading for screens
- Image optimization and caching
- Background sync optimization
- Battery usage minimization

```bash
> Use the security-architecture agent to implement mobile security best practices
```

**Security Implementation**:
- Biometric authentication
- Secure token storage
- Certificate pinning
- Data encryption at rest

## Technical Implementation Details

### Mobile App Structure
```
mobile-app/
├── src/
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   ├── services/
│   ├── store/
│   └── utils/
├── ios/
│   └── [Native iOS modules]
├── android/
│   └── [Native Android modules]
└── shared/
    └── [Shared business logic]
```

### Backend Architecture
```
backend/
├── graphql/
│   ├── schema/
│   ├── resolvers/
│   └── subscriptions/
├── services/
│   ├── auth/
│   ├── workout/
│   ├── social/
│   └── integrations/
├── workers/
│   ├── sync/
│   └── notifications/
└── infrastructure/
```

## Deployment Strategy

### Mobile Deployment
```bash
> Use the devops-engineering agent to setup mobile CI/CD pipeline
```

- **iOS**: Fastlane + TestFlight
- **Android**: Fastlane + Google Play Console
- **Code signing**: Automated with CI/CD
- **Beta testing**: 500 users via TestFlight/Play Console

### Backend Deployment
- **API**: AWS ECS with auto-scaling
- **Database**: Aurora PostgreSQL
- **Cache**: ElastiCache Redis
- **CDN**: CloudFront for static assets

## Results & Metrics

### App Performance
- Cold start: <2 seconds
- API response time: <200ms
- Offline capability: Full workout tracking
- Battery usage: <5% per hour during tracking

### User Metrics (First 3 Months)
- Downloads: 50,000+
- DAU: 15,000
- Retention (Day 30): 42%
- Premium conversion: 8%
- App Store rating: 4.6/5

### Technical Achievements
- 99.9% crash-free sessions
- 95% code sharing between platforms
- 80% test coverage
- Zero security incidents

## Integration Examples

### HealthKit Integration
```swift
// iOS Native Module
@objc(HealthKitManager)
class HealthKitManager: NSObject {
  @objc
  func syncWorkoutData(_ workoutData: NSDictionary, 
                       resolver: @escaping RCTPromiseResolveBlock,
                       rejecter: @escaping RCTPromiseRejectBlock) {
    // HealthKit sync implementation
  }
}
```

### Wearable Device Sync
```javascript
// React Native implementation
const syncWearableData = async () => {
  const devices = await WearableManager.getConnectedDevices();
  
  for (const device of devices) {
    const data = await device.getLatestWorkoutData();
    await WorkoutService.syncDeviceData(data);
  }
};
```

## Key Learnings

1. **Native Modules**: Critical for performance-sensitive features
2. **Offline-First**: Essential for fitness tracking reliability
3. **Battery Optimization**: Major factor in user retention
4. **Social Features**: Significantly increased engagement

## Commands Sequence

```bash
# Project initialization
> Use the master-orchestrator agent to begin new project: "Cross-platform fitness tracking mobile app..."

# Architecture & planning
> Use the mobile-development agent to plan React Native architecture
> Use the backend-services agent to design GraphQL API schema

# Development
> Use the frontend-mockup agent to create mobile UI prototypes
> Use the api-integration-specialist agent to integrate wearable device APIs
> Use the testing-automation agent to implement mobile app testing

# Optimization & deployment
> Use the performance-optimization agent to optimize app startup time
> Use the devops-engineering agent to setup mobile CI/CD with Fastlane
```

This example showcases how the agent system handles complex mobile development with native integrations, real-time features, and cross-platform deployment.