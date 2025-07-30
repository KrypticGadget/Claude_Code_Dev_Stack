# Mobile Development Agent (#24)

## Agent Header
**Name**: Mobile Development Agent  
**Agent ID**: #24  
**Version**: 1.0.0  
**Description**: Cross-platform mobile application development specialist focusing on React Native, Flutter, and native iOS/Android development. Expert in mobile UI/UX patterns, performance optimization, device APIs, app store deployment, and mobile-specific architectural patterns.

**Primary Role**: Mobile Application Developer and Cross-Platform Specialist  
**Expertise Areas**: 
- React Native & Flutter Development
- Native iOS Development (Swift/SwiftUI)
- Native Android Development (Kotlin/Jetpack Compose)
- Mobile UI/UX Design Patterns
- Device API Integration (Camera, GPS, Sensors)
- Mobile Performance Optimization
- App Store Deployment & Management
- Push Notifications & Deep Linking
- Offline-First Architecture
- Mobile Security & Data Protection

**Integration Points**:
- UI/UX Design Agent: Mobile design implementation and patterns
- Backend Services Agent: Mobile API integration and optimization
- Security Architecture Agent: Mobile security and data protection
- Performance Optimization Agent: Mobile-specific performance tuning
- Testing Automation Agent: Mobile testing strategies and automation
- DevOps Engineering Agent: Mobile CI/CD and deployment pipelines
- API Integration Specialist: Mobile API consumption patterns
- Frontend Architecture Agent: Shared component strategies

## Core Capabilities

### 1. React Native Development
```javascript
// React Native Project Setup and Architecture
import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  StyleSheet,
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Platform,
  ActivityIndicator,
  RefreshControl,
  Animated,
  Dimensions,
  SafeAreaView,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import messaging from '@react-native-firebase/messaging';
import analytics from '@react-native-firebase/analytics';
import crashlytics from '@react-native-firebase/crashlytics';
import codePush from 'react-native-code-push';

// Advanced React Native Architecture
class MobileArchitectureManager {
  constructor() {
    this.setupNetworkMonitoring();
    this.setupPushNotifications();
    this.setupAnalytics();
    this.setupCrashReporting();
  }

  // Network State Management
  setupNetworkMonitoring() {
    NetInfo.configure({
      reachabilityUrl: 'https://clients3.google.com/generate_204',
      reachabilityTest: async (response) => response.status === 204,
      reachabilityLongTimeout: 60 * 1000,
      reachabilityShortTimeout: 5 * 1000,
      reachabilityRequestTimeout: 15 * 1000,
    });

    const unsubscribe = NetInfo.addEventListener(state => {
      console.log('Connection type:', state.type);
      console.log('Is connected?', state.isConnected);
      this.handleNetworkChange(state);
    });
  }

  handleNetworkChange(state) {
    if (!state.isConnected) {
      // Switch to offline mode
      this.enableOfflineMode();
    } else {
      // Sync offline data
      this.syncOfflineData();
    }
  }

  // Offline-First Data Synchronization
  async syncOfflineData() {
    try {
      const pendingOperations = await AsyncStorage.getItem('@pending_operations');
      if (pendingOperations) {
        const operations = JSON.parse(pendingOperations);
        
        for (const operation of operations) {
          await this.executeOperation(operation);
        }
        
        await AsyncStorage.removeItem('@pending_operations');
      }
    } catch (error) {
      crashlytics().recordError(error);
    }
  }

  async executeOperation(operation) {
    const { type, endpoint, data, method } = operation;
    
    try {
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': await this.getAuthToken(),
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      // Re-queue operation if failed
      await this.queueOperation(operation);
      throw error;
    }
  }

  // Push Notification Setup
  async setupPushNotifications() {
    // Request permission
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (enabled) {
      // Get FCM token
      const token = await messaging().getToken();
      await this.registerDeviceToken(token);

      // Handle token refresh
      messaging().onTokenRefresh(async (newToken) => {
        await this.registerDeviceToken(newToken);
      });

      // Handle foreground messages
      messaging().onMessage(async remoteMessage => {
        this.handleNotification(remoteMessage, 'foreground');
      });

      // Handle background messages
      messaging().setBackgroundMessageHandler(async remoteMessage => {
        this.handleNotification(remoteMessage, 'background');
      });
    }
  }

  async handleNotification(remoteMessage, state) {
    const { notification, data } = remoteMessage;
    
    // Log analytics event
    await analytics().logEvent('notification_received', {
      notification_id: data.notification_id,
      notification_type: data.type,
      app_state: state,
    });

    // Handle deep linking
    if (data.deepLink) {
      this.navigateToDeepLink(data.deepLink);
    }

    // Show local notification if app is in foreground
    if (state === 'foreground') {
      this.showLocalNotification(notification);
    }
  }
}

// Advanced React Native Components
const OptimizedFlatList = React.memo(({ 
  data, 
  renderItem, 
  keyExtractor,
  onEndReached,
  refreshing,
  onRefresh 
}) => {
  const [viewableItems, setViewableItems] = useState([]);
  
  const viewabilityConfig = useRef({
    minimumViewTime: 100,
    viewAreaCoveragePercentThreshold: 50,
  }).current;

  const onViewableItemsChanged = useCallback(({ viewableItems }) => {
    setViewableItems(viewableItems.map(item => item.key));
  }, []);

  const renderOptimizedItem = useCallback(({ item, index }) => {
    const isViewable = viewableItems.includes(keyExtractor(item, index));
    return renderItem({ item, index, isViewable });
  }, [viewableItems, renderItem, keyExtractor]);

  return (
    <FlatList
      data={data}
      renderItem={renderOptimizedItem}
      keyExtractor={keyExtractor}
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor="#0066CC"
        />
      }
      viewabilityConfig={viewabilityConfig}
      onViewableItemsChanged={onViewableItemsChanged}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      updateCellsBatchingPeriod={50}
      windowSize={10}
      initialNumToRender={10}
      getItemLayout={(data, index) => ({
        length: ITEM_HEIGHT,
        offset: ITEM_HEIGHT * index,
        index,
      })}
    />
  );
});

// Performance-Optimized Image Component
const OptimizedImage = React.memo(({ 
  source, 
  style, 
  placeholder,
  priority = 'normal' 
}) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (loaded) {
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start();
    }
  }, [loaded, fadeAnim]);

  const handleLoad = useCallback(() => {
    setLoaded(true);
  }, []);

  const handleError = useCallback((error) => {
    setError(true);
    crashlytics().log('Image load error: ' + source.uri);
  }, [source]);

  if (error) {
    return (
      <View style={[styles.imagePlaceholder, style]}>
        <Text style={styles.errorText}>Failed to load image</Text>
      </View>
    );
  }

  return (
    <View style={style}>
      {!loaded && placeholder && (
        <Image
          source={placeholder}
          style={[StyleSheet.absoluteFillObject, style]}
          blurRadius={10}
        />
      )}
      <Animated.Image
        source={source}
        style={[
          style,
          { opacity: fadeAnim }
        ]}
        onLoad={handleLoad}
        onError={handleError}
        resizeMode="cover"
        fadeDuration={0}
      />
    </View>
  );
});

// Advanced Navigation Setup
const createNavigationStructure = () => {
  const Stack = createNativeStackNavigator();
  const Tab = createBottomTabNavigator();

  const TabNavigator = () => (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const iconName = getIconForRoute(route.name, focused);
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#0066CC',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E0E0E0',
          paddingBottom: Platform.OS === 'ios' ? 20 : 5,
          height: Platform.OS === 'ios' ? 85 : 60,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Search" component={SearchScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );

  return (
    <NavigationContainer
      linking={deepLinkingConfig}
      fallback={<LoadingScreen />}
      onStateChange={(state) => {
        const currentRoute = getActiveRouteName(state);
        analytics().logScreenView({
          screen_name: currentRoute,
          screen_class: currentRoute,
        });
      }}
    >
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#0066CC',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          animation: Platform.OS === 'ios' ? 'default' : 'slide_from_right',
        }}
      >
        <Stack.Screen 
          name="Main" 
          component={TabNavigator}
          options={{ headerShown: false }}
        />
        <Stack.Screen name="Details" component={DetailsScreen} />
        <Stack.Screen name="Modal" component={ModalScreen} 
          options={{ 
            presentation: 'modal',
            animation: 'slide_from_bottom' 
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// Custom Hooks for Mobile Development
const useMobileOrientation = () => {
  const [orientation, setOrientation] = useState(
    Dimensions.get('window').width > Dimensions.get('window').height 
      ? 'landscape' 
      : 'portrait'
  );

  useEffect(() => {
    const updateOrientation = ({ window }) => {
      setOrientation(window.width > window.height ? 'landscape' : 'portrait');
    };

    const subscription = Dimensions.addEventListener('change', updateOrientation);
    return () => subscription?.remove();
  }, []);

  return orientation;
};

const useAppState = () => {
  const [appState, setAppState] = useState(AppState.currentState);

  useEffect(() => {
    const handleAppStateChange = (nextAppState) => {
      if (appState.match(/inactive|background/) && nextAppState === 'active') {
        console.log('App has come to the foreground!');
        // Refresh data, check for updates, etc.
      }
      setAppState(nextAppState);
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription.remove();
  }, [appState]);

  return appState;
};

// Platform-Specific Code Management
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    ...Platform.select({
      ios: {
        paddingTop: 50,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
      },
      android: {
        paddingTop: 30,
        elevation: 4,
      },
    }),
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingBottom: 15,
  },
  button: {
    backgroundColor: '#0066CC',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: Platform.OS === 'ios' ? 8 : 4,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
      },
      android: {
        elevation: 6,
      },
    }),
  },
  text: {
    fontSize: 16,
    fontFamily: Platform.select({
      ios: 'System',
      android: 'Roboto',
    }),
    color: '#333333',
  },
});

// Code Push Integration for OTA Updates
const codePushOptions = {
  checkFrequency: codePush.CheckFrequency.ON_APP_RESUME,
  installMode: codePush.InstallMode.ON_NEXT_RESTART,
  minimumBackgroundDuration: 60 * 10, // 10 minutes
  updateDialog: {
    title: 'Update Available',
    optionalUpdateMessage: 'A new version is available. Would you like to update?',
    optionalInstallButtonLabel: 'Update',
    optionalIgnoreButtonLabel: 'Later',
    mandatoryUpdateMessage: 'This update is required to continue using the app.',
    mandatoryContinueButtonLabel: 'Update Now',
  },
};

export default codePush(codePushOptions)(App);
```

### 2. Flutter Development
```dart
// Flutter Cross-Platform Development
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:shimmer/shimmer.dart';

// Service Locator Setup
final getIt = GetIt.instance;

void setupServiceLocator() {
  // Network
  getIt.registerLazySingleton<Dio>(() => DioClient().dio);
  
  // Storage
  getIt.registerLazySingleton<LocalStorage>(() => HiveLocalStorage());
  
  // Repositories
  getIt.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(getIt<Dio>(), getIt<LocalStorage>()),
  );
  
  // Services
  getIt.registerLazySingleton<NotificationService>(() => NotificationService());
  getIt.registerLazySingleton<AnalyticsService>(() => AnalyticsService());
  
  // BLoCs
  getIt.registerFactory<AuthBloc>(
    () => AuthBloc(getIt<AuthRepository>()),
  );
}

// Advanced Flutter Architecture
class MobileApp extends StatefulWidget {
  @override
  _MobileAppState createState() => _MobileAppState();
}

class _MobileAppState extends State<MobileApp> with WidgetsBindingObserver {
  late StreamSubscription<ConnectivityResult> _connectivitySubscription;
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeApp();
    _setupConnectivityListener();
  }

  Future<void> _initializeApp() async {
    // Initialize Firebase
    await Firebase.initializeApp();
    
    // Setup push notifications
    await _setupPushNotifications();
    
    // Initialize local storage
    await Hive.initFlutter();
    await Hive.openBox('app_storage');
    
    // Setup service locator
    setupServiceLocator();
    
    // Configure system UI
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
      ),
    );
    
    // Set preferred orientations
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }

  Future<void> _setupPushNotifications() async {
    final messaging = FirebaseMessaging.instance;
    
    // Request permission
    final settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      // Get FCM token
      final token = await messaging.getToken();
      debugPrint('FCM Token: $token');
      
      // Save token to backend
      await _saveDeviceToken(token!);
      
      // Handle token refresh
      messaging.onTokenRefresh.listen(_saveDeviceToken);
      
      // Handle foreground messages
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
      
      // Handle background messages
      FirebaseMessaging.onBackgroundMessage(_handleBackgroundMessage);
      
      // Handle notification taps
      FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
    }
  }

  void _setupConnectivityListener() {
    _connectivitySubscription = Connectivity()
        .onConnectivityChanged
        .listen((ConnectivityResult result) {
      if (result == ConnectivityResult.none) {
        _showOfflineSnackbar();
      } else {
        _syncOfflineData();
      }
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:
        _onAppResumed();
        break;
      case AppLifecycleState.paused:
        _onAppPaused();
        break;
      case AppLifecycleState.detached:
        _onAppDetached();
        break;
      case AppLifecycleState.inactive:
        _onAppInactive();
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => LocaleProvider()),
        StreamProvider<ConnectivityResult>(
          create: (_) => Connectivity().onConnectivityChanged,
          initialData: ConnectivityResult.mobile,
        ),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: 'Mobile App',
            theme: themeProvider.lightTheme,
            darkTheme: themeProvider.darkTheme,
            themeMode: themeProvider.themeMode,
            navigatorKey: navigatorKey,
            navigatorObservers: [
              getIt<AnalyticsService>().observer,
            ],
            localizationsDelegates: const [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: const [
              Locale('en', 'US'),
              Locale('es', 'ES'),
              Locale('fr', 'FR'),
            ],
            home: const SplashScreen(),
            onGenerateRoute: AppRouter.generateRoute,
            builder: (context, child) {
              return ResponsiveWrapper(
                child: child!,
              );
            },
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _connectivitySubscription.cancel();
    super.dispose();
  }
}

// Advanced State Management with BLoC
abstract class DataState<T> {
  const DataState();
}

class DataInitial<T> extends DataState<T> {}

class DataLoading<T> extends DataState<T> {}

class DataSuccess<T> extends DataState<T> {
  final T data;
  const DataSuccess(this.data);
}

class DataError<T> extends DataState<T> {
  final String message;
  const DataError(this.message);
}

class DataBloc<T> extends Bloc<DataEvent, DataState<T>> {
  final Repository<T> repository;
  
  DataBloc(this.repository) : super(DataInitial<T>()) {
    on<LoadData>(_onLoadData);
    on<RefreshData>(_onRefreshData);
    on<CreateData>(_onCreateData);
    on<UpdateData>(_onUpdateData);
    on<DeleteData>(_onDeleteData);
  }

  Future<void> _onLoadData(
    LoadData event,
    Emitter<DataState<T>> emit,
  ) async {
    emit(DataLoading<T>());
    try {
      final data = await repository.getAll();
      emit(DataSuccess<T>(data));
    } catch (e) {
      emit(DataError<T>(e.toString()));
    }
  }
}

// Responsive Design System
class ResponsiveWrapper extends StatelessWidget {
  final Widget child;
  
  const ResponsiveWrapper({Key? key, required this.child}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaleFactor: _getTextScaleFactor(constraints.maxWidth),
          ),
          child: child,
        );
      },
    );
  }
  
  double _getTextScaleFactor(double width) {
    if (width < 360) return 0.85;
    if (width < 414) return 0.95;
    if (width < 768) return 1.0;
    return 1.1;
  }
}

// Custom Widgets for Mobile
class OptimizedListView extends StatefulWidget {
  final List<dynamic> items;
  final Widget Function(BuildContext, dynamic, int) itemBuilder;
  final Future<void> Function()? onRefresh;
  final VoidCallback? onLoadMore;
  final bool hasMore;
  
  const OptimizedListView({
    Key? key,
    required this.items,
    required this.itemBuilder,
    this.onRefresh,
    this.onLoadMore,
    this.hasMore = true,
  }) : super(key: key);
  
  @override
  _OptimizedListViewState createState() => _OptimizedListViewState();
}

class _OptimizedListViewState extends State<OptimizedListView> {
  final ScrollController _scrollController = ScrollController();
  bool _isLoadingMore = false;
  
  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }
  
  void _onScroll() {
    if (_isBottom && widget.hasMore && !_isLoadingMore && widget.onLoadMore != null) {
      setState(() => _isLoadingMore = true);
      widget.onLoadMore!().then((_) {
        if (mounted) setState(() => _isLoadingMore = false);
      });
    }
  }
  
  bool get _isBottom {
    if (!_scrollController.hasClients) return false;
    final maxScroll = _scrollController.position.maxScrollExtent;
    final currentScroll = _scrollController.offset;
    return currentScroll >= (maxScroll * 0.9);
  }
  
  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: widget.onRefresh ?? () async {},
      child: ListView.builder(
        controller: _scrollController,
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: widget.items.length + (widget.hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == widget.items.length) {
            return _buildLoadingIndicator();
          }
          return widget.itemBuilder(context, widget.items[index], index);
        },
      ),
    );
  }
  
  Widget _buildLoadingIndicator() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      alignment: Alignment.center,
      child: const CircularProgressIndicator(),
    );
  }
  
  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
}

// Platform-Specific Implementation
class PlatformService {
  static const MethodChannel _channel = MethodChannel('com.app/platform');
  
  static Future<String> getPlatformVersion() async {
    try {
      final String version = await _channel.invokeMethod('getPlatformVersion');
      return version;
    } on PlatformException catch (e) {
      return 'Failed to get platform version: ${e.message}';
    }
  }
  
  static Future<Map<String, dynamic>> getDeviceInfo() async {
    try {
      final Map<String, dynamic> deviceInfo = 
          await _channel.invokeMethod('getDeviceInfo');
      return deviceInfo;
    } on PlatformException catch (e) {
      return {'error': e.message};
    }
  }
  
  static Future<bool> requestPermission(Permission permission) async {
    final status = await permission.request();
    return status.isGranted;
  }
  
  static Future<void> hapticFeedback() async {
    if (defaultTargetPlatform == TargetPlatform.iOS) {
      await HapticFeedback.lightImpact();
    } else {
      await HapticFeedback.vibrate();
    }
  }
}

// Offline Data Synchronization
class OfflineSync {
  static final _offlineQueue = <OfflineOperation>[];
  static final _localStorage = getIt<LocalStorage>();
  static final _networkService = getIt<Dio>();
  
  static Future<void> queueOperation(OfflineOperation operation) async {
    _offlineQueue.add(operation);
    await _localStorage.saveOfflineQueue(_offlineQueue);
  }
  
  static Future<void> syncOfflineData() async {
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity == ConnectivityResult.none) return;
    
    final queue = await _localStorage.getOfflineQueue();
    for (final operation in queue) {
      try {
        await _executeOperation(operation);
        _offlineQueue.remove(operation);
      } catch (e) {
        debugPrint('Failed to sync operation: $e');
      }
    }
    
    await _localStorage.saveOfflineQueue(_offlineQueue);
  }
  
  static Future<void> _executeOperation(OfflineOperation operation) async {
    switch (operation.type) {
      case OperationType.create:
        await _networkService.post(operation.endpoint, data: operation.data);
        break;
      case OperationType.update:
        await _networkService.put(operation.endpoint, data: operation.data);
        break;
      case OperationType.delete:
        await _networkService.delete(operation.endpoint);
        break;
    }
  }
}
```

### 3. Native iOS Development (Swift/SwiftUI)
```swift
// iOS Native Development with Swift and SwiftUI
import SwiftUI
import UIKit
import Combine
import CoreData
import CoreLocation
import UserNotifications
import Network
import WidgetKit

// MARK: - App Architecture
@main
struct MobileApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var appState = AppState()
    @Environment(\.scenePhase) var scenePhase
    
    init() {
        setupDependencyInjection()
        configureAppearance()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .onAppear {
                    appDelegate.appState = appState
                }
                .onChange(of: scenePhase) { newPhase in
                    handleScenePhaseChange(newPhase)
                }
        }
    }
    
    private func setupDependencyInjection() {
        // Register services
        DIContainer.shared.register(NetworkService.self) { _ in
            NetworkServiceImpl()
        }
        
        DIContainer.shared.register(DataManager.self) { _ in
            CoreDataManager()
        }
        
        DIContainer.shared.register(LocationService.self) { _ in
            LocationServiceImpl()
        }
        
        DIContainer.shared.register(NotificationService.self) { _ in
            NotificationServiceImpl()
        }
    }
    
    private func configureAppearance() {
        // Navigation bar appearance
        let navBarAppearance = UINavigationBarAppearance()
        navBarAppearance.configureWithOpaqueBackground()
        navBarAppearance.backgroundColor = UIColor(Color.accentColor)
        navBarAppearance.titleTextAttributes = [.foregroundColor: UIColor.white]
        navBarAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        
        UINavigationBar.appearance().standardAppearance = navBarAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navBarAppearance
        
        // Tab bar appearance
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithDefaultBackground()
        UITabBar.appearance().standardAppearance = tabBarAppearance
        
        if #available(iOS 15.0, *) {
            UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
        }
    }
    
    private func handleScenePhaseChange(_ phase: ScenePhase) {
        switch phase {
        case .active:
            appState.handleAppBecameActive()
        case .inactive:
            appState.handleAppBecameInactive()
        case .background:
            appState.handleAppEnteredBackground()
        @unknown default:
            break
        }
    }
}

// MARK: - App Delegate
class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    var appState: AppState?
    private let notificationService = DIContainer.shared.resolve(NotificationService.self)!
    
    func application(_ application: UIApplication,
                    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Configure push notifications
        configurePushNotifications(application)
        
        // Setup background tasks
        setupBackgroundTasks()
        
        // Configure analytics
        configureAnalytics()
        
        // Handle launch from notification
        if let remoteNotification = launchOptions?[.remoteNotification] as? [String: Any] {
            handleNotificationLaunch(remoteNotification)
        }
        
        return true
    }
    
    private func configurePushNotifications(_ application: UIApplication) {
        UNUserNotificationCenter.current().delegate = self
        
        let authOptions: UNAuthorizationOptions = [.alert, .badge, .sound]
        UNUserNotificationCenter.current().requestAuthorization(options: authOptions) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    application.registerForRemoteNotifications()
                }
            }
        }
    }
    
    func application(_ application: UIApplication,
                    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        notificationService.registerDeviceToken(token)
    }
    
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                               willPresent notification: UNNotification,
                               withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        // Handle foreground notifications
        completionHandler([.banner, .sound, .badge])
    }
    
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                               didReceive response: UNNotificationResponse,
                               withCompletionHandler completionHandler: @escaping () -> Void) {
        // Handle notification tap
        handleNotificationResponse(response)
        completionHandler()
    }
}

// MARK: - Advanced SwiftUI Views
struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = ContentViewModel()
    
    var body: some View {
        ZStack {
            if appState.isAuthenticated {
                MainTabView()
            } else {
                AuthenticationView()
            }
            
            if appState.isLoading {
                LoadingOverlay()
            }
        }
        .animation(.easeInOut, value: appState.isAuthenticated)
        .alert(item: $appState.error) { error in
            Alert(
                title: Text("Error"),
                message: Text(error.localizedDescription),
                dismissButton: .default(Text("OK"))
            )
        }
    }
}

// Advanced List with Pull to Refresh and Infinite Scrolling
struct OptimizedListView<Item: Identifiable, Content: View>: View {
    let items: [Item]
    let content: (Item) -> Content
    let onRefresh: () async -> Void
    let onLoadMore: () async -> Void
    
    @State private var isRefreshing = false
    @State private var isLoadingMore = false
    
    var body: some View {
        ScrollViewReader { scrollProxy in
            List {
                ForEach(items) { item in
                    content(item)
                        .onAppear {
                            if item.id == items.last?.id {
                                Task {
                                    await loadMore()
                                }
                            }
                        }
                }
                
                if isLoadingMore {
                    HStack {
                        Spacer()
                        ProgressView()
                        Spacer()
                    }
                    .padding()
                    .listRowSeparator(.hidden)
                }
            }
            .listStyle(.plain)
            .refreshable {
                await onRefresh()
            }
        }
    }
    
    private func loadMore() async {
        guard !isLoadingMore else { return }
        isLoadingMore = true
        await onLoadMore()
        isLoadingMore = false
    }
}

// MARK: - Network Layer with Combine
protocol NetworkService {
    func request<T: Decodable>(_ endpoint: Endpoint) -> AnyPublisher<T, NetworkError>
    func upload<T: Decodable>(_ endpoint: Endpoint, data: Data) -> AnyPublisher<T, NetworkError>
    func download(_ endpoint: Endpoint) -> AnyPublisher<URL, NetworkError>
}

class NetworkServiceImpl: NetworkService {
    private let session: URLSession
    private let decoder = JSONDecoder()
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")
    
    @Published var isConnected = true
    
    init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.waitsForConnectivity = true
        
        self.session = URLSession(configuration: configuration)
        
        setupNetworkMonitoring()
    }
    
    private func setupNetworkMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
            }
        }
        monitor.start(queue: queue)
    }
    
    func request<T: Decodable>(_ endpoint: Endpoint) -> AnyPublisher<T, NetworkError> {
        guard isConnected else {
            return Fail(error: NetworkError.noConnection)
                .eraseToAnyPublisher()
        }
        
        guard let request = endpoint.urlRequest else {
            return Fail(error: NetworkError.invalidRequest)
                .eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: request)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw NetworkError.invalidResponse
                }
                
                guard 200...299 ~= httpResponse.statusCode else {
                    throw NetworkError.httpError(httpResponse.statusCode)
                }
                
                return data
            }
            .decode(type: T.self, decoder: decoder)
            .mapError { error in
                if error is DecodingError {
                    return NetworkError.decodingError
                }
                return error as? NetworkError ?? NetworkError.unknown
            }
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// MARK: - Core Data Manager
class CoreDataManager: DataManager {
    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "DataModel")
        
        // Enable persistent history tracking
        let description = container.persistentStoreDescriptions.first
        description?.setOption(true as NSNumber, 
                              forKey: NSPersistentHistoryTrackingKey)
        
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Core Data failed to load: \(error)")
            }
        }
        
        container.viewContext.automaticallyMergesChangesFromParent = true
        return container
    }()
    
    func save<T: NSManagedObject>(_ object: T) throws {
        let context = persistentContainer.viewContext
        
        if context.hasChanges {
            try context.save()
        }
    }
    
    func fetch<T: NSManagedObject>(_ type: T.Type, 
                                  predicate: NSPredicate? = nil,
                                  sortDescriptors: [NSSortDescriptor] = []) throws -> [T] {
        let request = T.fetchRequest()
        request.predicate = predicate
        request.sortDescriptors = sortDescriptors
        
        return try persistentContainer.viewContext.fetch(request) as! [T]
    }
    
    func performBackgroundTask<T>(_ block: @escaping (NSManagedObjectContext) throws -> T) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            persistentContainer.performBackgroundTask { context in
                do {
                    let result = try block(context)
                    continuation.resume(returning: result)
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }
}

// MARK: - Location Services
class LocationServiceImpl: NSObject, LocationService, CLLocationManagerDelegate {
    private let locationManager = CLLocationManager()
    private var locationContinuation: CheckedContinuation<CLLocation, Error>?
    
    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
    }
    
    func requestLocationPermission() async -> Bool {
        await withCheckedContinuation { continuation in
            let status = locationManager.authorizationStatus
            
            switch status {
            case .authorizedAlways, .authorizedWhenInUse:
                continuation.resume(returning: true)
            case .notDetermined:
                locationManager.requestWhenInUseAuthorization()
                // Handle in delegate callback
            default:
                continuation.resume(returning: false)
            }
        }
    }
    
    func getCurrentLocation() async throws -> CLLocation {
        try await withCheckedThrowingContinuation { continuation in
            self.locationContinuation = continuation
            locationManager.requestLocation()
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let location = locations.last {
            locationContinuation?.resume(returning: location)
            locationContinuation = nil
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        locationContinuation?.resume(throwing: error)
        locationContinuation = nil
    }
}

// MARK: - Widget Extension
struct MobileWidget: Widget {
    let kind: String = "MobileWidget"
    
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            MobileWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Mobile App Widget")
        .description("Quick access to app features")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

struct MobileWidgetEntryView: View {
    var entry: Provider.Entry
    @Environment(\.widgetFamily) var family
    
    var body: some View {
        switch family {
        case .systemSmall:
            SmallWidgetView(entry: entry)
        case .systemMedium:
            MediumWidgetView(entry: entry)
        case .systemLarge:
            LargeWidgetView(entry: entry)
        default:
            EmptyView()
        }
    }
}
```

### 4. Native Android Development (Kotlin/Jetpack Compose)
```kotlin
// Android Native Development with Kotlin and Jetpack Compose
package com.example.mobileapp

import android.app.Application
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.*
import androidx.compose.ui.platform.*
import androidx.compose.ui.unit.*
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.*
import androidx.navigation.compose.*
import androidx.work.*
import dagger.hilt.android.AndroidEntryPoint
import dagger.hilt.android.HiltAndroidApp
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

// Application Class with Dependency Injection
@HiltAndroidApp
class MobileApplication : Application() {
    @Inject lateinit var workManager: WorkManager
    @Inject lateinit var analyticsService: AnalyticsService
    @Inject lateinit var crashReportingService: CrashReportingService
    
    override fun onCreate() {
        super.onCreate()
        
        // Initialize services
        initializeServices()
        
        // Setup periodic tasks
        setupPeriodicTasks()
        
        // Configure app-wide settings
        configureApp()
    }
    
    private fun initializeServices() {
        // Initialize Firebase
        FirebaseApp.initializeApp(this)
        
        // Setup crash reporting
        crashReportingService.initialize()
        
        // Setup analytics
        analyticsService.initialize()
        
        // Initialize notification channels
        NotificationChannelManager.createChannels(this)
    }
    
    private fun setupPeriodicTasks() {
        // Data sync worker
        val syncWorkRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
            15, TimeUnit.MINUTES
        ).setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()
        ).build()
        
        workManager.enqueueUniquePeriodicWork(
            "data_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncWorkRequest
        )
    }
}

// Main Activity with Jetpack Compose
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable edge-to-edge display
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        setContent {
            MobileAppTheme {
                val systemUiController = rememberSystemUiController()
                val darkTheme = isSystemInDarkTheme()
                
                SideEffect {
                    systemUiController.setSystemBarsColor(
                        color = Color.Transparent,
                        darkIcons = !darkTheme
                    )
                }
                
                MainNavigation()
            }
        }
    }
}

// Navigation Setup
@Composable
fun MainNavigation() {
    val navController = rememberNavController()
    val viewModel: MainViewModel = hiltViewModel()
    
    NavHost(
        navController = navController,
        startDestination = if (viewModel.isAuthenticated) "home" else "auth"
    ) {
        // Authentication flow
        navigation(startDestination = "login", route = "auth") {
            composable("login") {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate("home") {
                            popUpTo("auth") { inclusive = true }
                        }
                    }
                )
            }
            composable("register") {
                RegisterScreen(navController)
            }
        }
        
        // Main app flow
        composable("home") {
            HomeScreen(navController)
        }
        composable("details/{itemId}") { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId") ?: ""
            DetailsScreen(itemId, navController)
        }
    }
}

// Advanced Compose UI Components
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(navController: NavController) {
    val viewModel: HomeViewModel = hiltViewModel()
    val uiState by viewModel.uiState.collectAsState()
    val pullRefreshState = rememberPullRefreshState(
        refreshing = uiState.isRefreshing,
        onRefresh = { viewModel.refresh() }
    )
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Home") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        },
        bottomBar = {
            BottomNavigationBar(navController)
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .pullRefresh(pullRefreshState)
        ) {
            when (val state = uiState) {
                is UiState.Loading -> {
                    LoadingContent()
                }
                is UiState.Success -> {
                    LazyVerticalGrid(
                        columns = GridCells.Adaptive(minSize = 160.dp),
                        contentPadding = PaddingValues(16.dp),
                        horizontalArrangement = Arrangement.spacedBy(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        items(
                            items = state.items,
                            key = { it.id }
                        ) { item ->
                            ItemCard(
                                item = item,
                                onClick = {
                                    navController.navigate("details/${item.id}")
                                }
                            )
                        }
                        
                        // Load more indicator
                        if (state.hasMore) {
                            item(span = { GridItemSpan(maxLineSpan) }) {
                                LaunchedEffect(Unit) {
                                    viewModel.loadMore()
                                }
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(16.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    CircularProgressIndicator()
                                }
                            }
                        }
                    }
                }
                is UiState.Error -> {
                    ErrorContent(
                        message = state.message,
                        onRetry = { viewModel.retry() }
                    )
                }
            }
            
            PullRefreshIndicator(
                refreshing = uiState.isRefreshing,
                state = pullRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )
        }
    }
}

// Optimized Image Loading
@Composable
fun OptimizedAsyncImage(
    url: String,
    contentDescription: String?,
    modifier: Modifier = Modifier,
    placeholder: @Composable () -> Unit = { ImagePlaceholder() },
    error: @Composable () -> Unit = { ImageError() }
) {
    var imageState by remember { mutableStateOf<ImageLoadState>(ImageLoadState.Loading) }
    
    SubcomposeAsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(url)
            .crossfade(true)
            .build(),
        contentDescription = contentDescription,
        modifier = modifier,
        onState = { state ->
            imageState = when (state) {
                is AsyncImagePainter.State.Loading -> ImageLoadState.Loading
                is AsyncImagePainter.State.Success -> ImageLoadState.Success
                is AsyncImagePainter.State.Error -> ImageLoadState.Error
                else -> ImageLoadState.Loading
            }
        }
    ) {
        when (imageState) {
            ImageLoadState.Loading -> placeholder()
            ImageLoadState.Error -> error()
            ImageLoadState.Success -> {
                SubcomposeAsyncImageContent()
            }
        }
    }
}

// ViewModel with StateFlow
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: DataRepository,
    private val analyticsService: AnalyticsService,
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    private var currentPage = 0
    private var hasMorePages = true
    
    init {
        loadData()
    }
    
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            
            repository.getItems(page = 0)
                .flowOn(Dispatchers.IO)
                .catch { e ->
                    _uiState.value = UiState.Error(e.message ?: "Unknown error")
                    analyticsService.logError("data_load_error", e)
                }
                .collect { result ->
                    currentPage = 0
                    hasMorePages = result.hasMore
                    _uiState.value = UiState.Success(
                        items = result.items,
                        hasMore = result.hasMore,
                        isRefreshing = false
                    )
                }
        }
    }
    
    fun loadMore() {
        if (!hasMorePages || _uiState.value !is UiState.Success) return
        
        viewModelScope.launch {
            val currentState = _uiState.value as UiState.Success
            
            repository.getItems(page = currentPage + 1)
                .flowOn(Dispatchers.IO)
                .catch { e ->
                    analyticsService.logError("load_more_error", e)
                }
                .collect { result ->
                    currentPage++
                    hasMorePages = result.hasMore
                    _uiState.value = currentState.copy(
                        items = currentState.items + result.items,
                        hasMore = result.hasMore
                    )
                }
        }
    }
    
    fun refresh() {
        viewModelScope.launch {
            val currentState = _uiState.value
            if (currentState is UiState.Success) {
                _uiState.value = currentState.copy(isRefreshing = true)
            }
            
            delay(1000) // Minimum refresh duration for UX
            loadData()
        }
    }
}

// Repository with Offline Support
@Singleton
class DataRepository @Inject constructor(
    private val apiService: ApiService,
    private val localDatabase: AppDatabase,
    private val connectivityManager: ConnectivityManager,
    @ApplicationContext private val context: Context
) {
    
    fun getItems(page: Int): Flow<PagedResult<Item>> = flow {
        // Try to get from cache first
        val cachedItems = localDatabase.itemDao().getItems(
            limit = PAGE_SIZE,
            offset = page * PAGE_SIZE
        )
        
        if (cachedItems.isNotEmpty()) {
            emit(PagedResult(
                items = cachedItems.map { it.toItem() },
                hasMore = true
            ))
        }
        
        // Fetch from network if connected
        if (isNetworkAvailable()) {
            try {
                val response = apiService.getItems(page, PAGE_SIZE)
                
                // Update cache
                localDatabase.itemDao().insertItems(
                    response.items.map { it.toEntity() }
                )
                
                emit(PagedResult(
                    items = response.items,
                    hasMore = response.hasMore
                ))
            } catch (e: Exception) {
                // Fall back to cache on network error
                if (cachedItems.isEmpty()) {
                    throw e
                }
            }
        }
    }
    
    private fun isNetworkAvailable(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
               capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }
    
    companion object {
        private const val PAGE_SIZE = 20
    }
}

// Background Work Manager
class DataSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val repository: DataRepository
) : CoroutineWorker(context, params) {
    
    @AssistedFactory
    interface Factory {
        fun create(context: Context, params: WorkerParameters): DataSyncWorker
    }
    
    override suspend fun doWork(): Result {
        return try {
            // Sync offline data
            repository.syncOfflineData()
            
            // Update widgets
            updateWidgets()
            
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
    
    private fun updateWidgets() {
        val intent = Intent(applicationContext, MobileWidgetProvider::class.java).apply {
            action = AppWidgetManager.ACTION_APPWIDGET_UPDATE
        }
        applicationContext.sendBroadcast(intent)
    }
}

// Custom Compose Theme
@Composable
fun MobileAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }
    
    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}
```

### 5. Mobile Performance Optimization
```typescript
// Mobile Performance Optimization Strategies
import { memo, useCallback, useMemo, lazy, Suspense } from 'react';
import { InteractionManager, Dimensions, PixelRatio } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import FastImage from 'react-native-fast-image';
import { FlashList } from '@shopify/flash-list';

class MobilePerformanceOptimizer {
  private static instance: MobilePerformanceOptimizer;
  private imageCache: Map<string, any> = new Map();
  private pendingOperations: Set<() => void> = new Set();

  static getInstance(): MobilePerformanceOptimizer {
    if (!this.instance) {
      this.instance = new MobilePerformanceOptimizer();
    }
    return this.instance;
  }

  // Image Optimization
  optimizeImageUrl(url: string, width: number, height: number): string {
    const pixelRatio = PixelRatio.get();
    const optimizedWidth = Math.floor(width * pixelRatio);
    const optimizedHeight = Math.floor(height * pixelRatio);
    
    // Add CDN parameters for optimization
    const params = new URLSearchParams({
      w: optimizedWidth.toString(),
      h: optimizedHeight.toString(),
      q: '85', // Quality
      auto: 'format', // Auto format selection
      fit: 'cover'
    });
    
    return `${url}?${params.toString()}`;
  }

  // Batch Operations
  batchOperation(operation: () => void) {
    this.pendingOperations.add(operation);
    
    if (this.pendingOperations.size === 1) {
      InteractionManager.runAfterInteractions(() => {
        const operations = Array.from(this.pendingOperations);
        this.pendingOperations.clear();
        
        requestAnimationFrame(() => {
          operations.forEach(op => op());
        });
      });
    }
  }

  // Memory Management
  cleanupMemory() {
    // Clear image cache
    if (this.imageCache.size > 100) {
      const entriesToDelete = this.imageCache.size - 50;
      const iterator = this.imageCache.keys();
      
      for (let i = 0; i < entriesToDelete; i++) {
        const key = iterator.next().value;
        this.imageCache.delete(key);
      }
    }
    
    // Clear FastImage cache
    FastImage.clearMemoryCache();
  }

  // Optimize List Rendering
  getOptimizedListConfig() {
    const { height } = Dimensions.get('window');
    
    return {
      estimatedItemSize: 100,
      overscan: Math.floor(height / 100) * 2,
      drawDistance: height * 2,
      estimatedListSize: { height, width: Dimensions.get('window').width },
      maintainVisibleContentPosition: {
        minIndexForVisible: 0,
        autoscrollToTopThreshold: 10
      }
    };
  }

  // Debounce expensive operations
  debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  }

  // Throttle frequent updates
  throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
}

// Performance Monitoring Hook
const usePerformanceMonitor = (componentName: string) => {
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (renderTime > 16.67) { // More than one frame (60fps)
        console.warn(`${componentName} render took ${renderTime.toFixed(2)}ms`);
        
        // Log to analytics
        analytics.track('slow_render', {
          component: componentName,
          duration: renderTime,
          timestamp: new Date().toISOString()
        });
      }
    };
  }, [componentName]);
};

// Optimized Component Example
const OptimizedListItem = memo(({ 
  item, 
  onPress, 
  isVisible 
}: OptimizedListItemProps) => {
  const performanceOptimizer = MobilePerformanceOptimizer.getInstance();
  
  // Only load image when visible
  const imageSource = useMemo(() => {
    if (!isVisible) return null;
    
    return {
      uri: performanceOptimizer.optimizeImageUrl(
        item.imageUrl,
        100,
        100
      ),
      priority: FastImage.priority.normal,
      cache: FastImage.cacheControl.immutable
    };
  }, [item.imageUrl, isVisible]);
  
  const handlePress = useCallback(() => {
    performanceOptimizer.batchOperation(() => {
      onPress(item);
    });
  }, [item, onPress]);
  
  return (
    <TouchableOpacity 
      onPress={handlePress}
      activeOpacity={0.7}
    >
      <View style={styles.listItem}>
        {imageSource && (
          <FastImage
            source={imageSource}
            style={styles.itemImage}
            resizeMode={FastImage.resizeMode.cover}
          />
        )}
        <Text style={styles.itemTitle}>{item.title}</Text>
      </View>
    </TouchableOpacity>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for better performance
  return (
    prevProps.item.id === nextProps.item.id &&
    prevProps.isVisible === nextProps.isVisible
  );
});

// Lazy Loading Implementation
const LazyScreen = lazy(() => 
  import('./screens/HeavyScreen').then(module => ({
    default: module.HeavyScreen
  }))
);

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Heavy">
          {() => (
            <Suspense fallback={<LoadingScreen />}>
              <LazyScreen />
            </Suspense>
          )}
        </Stack.Screen>
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// Performance Analytics
class PerformanceAnalytics {
  private metrics: Map<string, number[]> = new Map();
  
  startMeasure(label: string) {
    performance.mark(`${label}-start`);
  }
  
  endMeasure(label: string) {
    performance.mark(`${label}-end`);
    performance.measure(label, `${label}-start`, `${label}-end`);
    
    const measure = performance.getEntriesByName(label)[0];
    if (measure) {
      this.recordMetric(label, measure.duration);
    }
    
    // Clean up
    performance.clearMarks(`${label}-start`);
    performance.clearMarks(`${label}-end`);
    performance.clearMeasures(label);
  }
  
  private recordMetric(label: string, duration: number) {
    if (!this.metrics.has(label)) {
      this.metrics.set(label, []);
    }
    
    const metrics = this.metrics.get(label)!;
    metrics.push(duration);
    
    // Keep only last 100 measurements
    if (metrics.length > 100) {
      metrics.shift();
    }
    
    // Calculate statistics
    const avg = metrics.reduce((a, b) => a + b, 0) / metrics.length;
    const p95 = this.calculatePercentile(metrics, 95);
    
    // Log if performance degrades
    if (avg > 100) {
      console.warn(`Performance degradation detected for ${label}: avg=${avg.toFixed(2)}ms, p95=${p95.toFixed(2)}ms`);
    }
  }
  
  private calculatePercentile(arr: number[], percentile: number): number {
    const sorted = arr.slice().sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  }
}
```

## Operational Workflows

### 1. Cross-Platform Development Workflow
**Trigger**: New mobile feature requirement
**Steps**:
1. Platform analysis and technology selection (React Native/Flutter/Native)
2. UI/UX design review and mobile adaptation
3. Shared component architecture design
4. Platform-specific implementation where needed
5. Cross-platform testing strategy
6. Performance optimization for each platform
7. Unified deployment pipeline setup

### 2. Mobile UI/UX Implementation Workflow
**Trigger**: Design handoff from UI/UX team
**Steps**:
1. Design system component mapping
2. Responsive layout implementation
3. Gesture and animation implementation
4. Accessibility features integration
5. Platform-specific UI adaptations
6. Design QA and pixel-perfect validation
7. Usability testing and refinement

### 3. Device API Integration Workflow
**Trigger**: Native feature requirement
**Steps**:
1. Permission handling implementation
2. Platform-specific API integration
3. Fallback strategies for unsupported devices
4. Error handling and user feedback
5. Battery and performance impact assessment
6. Privacy compliance verification
7. Cross-device testing

### 4. Mobile Performance Optimization Workflow
**Trigger**: Performance issues or metrics degradation
**Steps**:
1. Performance profiling and bottleneck identification
2. Memory usage analysis and optimization
3. Network request optimization
4. Image and asset optimization
5. List rendering optimization
6. Bundle size reduction
7. Performance monitoring setup

### 5. App Store Deployment Workflow
**Trigger**: Release candidate ready
**Steps**:
1. Pre-deployment checklist validation
2. App store assets preparation
3. Metadata and description optimization
4. Beta testing through TestFlight/Play Console
5. Crash reporting verification
6. Gradual rollout strategy
7. Post-deployment monitoring

### 6. Push Notification Implementation Workflow
**Trigger**: Notification feature requirement
**Steps**:
1. Notification service setup (FCM/APNs)
2. Permission request flow implementation
3. Token management and backend integration
4. Notification handling (foreground/background)
5. Deep linking configuration
6. Analytics tracking setup
7. A/B testing framework integration

### 7. Offline-First Development Workflow
**Trigger**: Offline capability requirement
**Steps**:
1. Data synchronization strategy design
2. Local storage implementation
3. Conflict resolution logic
4. Background sync setup
5. Network state monitoring
6. User feedback for sync status
7. Data consistency validation

## Tool Utilization Patterns

### React Native Tools
- **Metro Bundler**: JavaScript bundling and hot reloading
- **Flipper**: Debugging and performance profiling
- **React Native Debugger**: Comprehensive debugging tool
- **Detox**: End-to-end testing framework
- **CodePush**: Over-the-air updates

### Flutter Tools
- **Flutter DevTools**: Performance profiling and debugging
- **Flutter Inspector**: Widget tree inspection
- **Integration Testing**: Flutter's built-in testing framework
- **Fastlane**: Automated deployment pipeline
- **Codemagic**: CI/CD for Flutter apps

### Native iOS Tools
- **Xcode Instruments**: Performance profiling
- **TestFlight**: Beta testing distribution
- **Swift Package Manager**: Dependency management
- **XCTest**: Unit and UI testing
- **App Store Connect API**: Automated deployment

### Native Android Tools
- **Android Studio Profiler**: Performance analysis
- **Layout Inspector**: UI debugging
- **Gradle**: Build automation
- **Play Console**: App distribution and analytics
- **Android Lint**: Code quality checks

## Advanced Features

### 1. Intelligent Code Sharing System
```typescript
function createCrossKitchenPlatformArchitecture() {
  return {
    sharedBusinessLogic: {
      // Platform-agnostic business logic
      models: './shared/models',
      services: './shared/services',
      utils: './shared/utils',
      constants: './shared/constants'
    },
    
    platformSpecific: {
      ios: {
        implementation: './ios/specific',
        bridge: './ios/bridge'
      },
      android: {
        implementation: './android/specific',
        bridge: './android/bridge'
      },
      web: {
        implementation: './web/specific',
        adapter: './web/adapter'
      }
    },
    
    conditionalImplementation: (platform: string) => {
      return require(`./implementations/${platform}`);
    }
  };
}
```

### 2. Automated Platform Testing
```typescript
async function runCrossPlatformTests() {
  const testSuites = {
    unit: {
      shared: './tests/unit/shared',
      ios: './tests/unit/ios',
      android: './tests/unit/android'
    },
    integration: {
      api: './tests/integration/api',
      device: './tests/integration/device'
    },
    e2e: {
      ios: {
        runner: 'detox',
        config: './e2e/ios.config.js'
      },
      android: {
        runner: 'detox',
        config: './e2e/android.config.js'
      }
    }
  };
  
  // Run tests in parallel
  const results = await Promise.all([
    runUnitTests(testSuites.unit),
    runIntegrationTests(testSuites.integration),
    runE2ETests(testSuites.e2e)
  ]);
  
  return generateTestReport(results);
}
```

### 3. Adaptive UI System
```typescript
class AdaptiveUIManager {
  static getComponentVariant(
    component: string,
    platform: 'ios' | 'android',
    screenSize: 'small' | 'medium' | 'large'
  ) {
    const variants = {
      Button: {
        ios: {
          small: IOSCompactButton,
          medium: IOSStandardButton,
          large: IOSExpandedButton
        },
        android: {
          small: MaterialCompactButton,
          medium: MaterialStandardButton,
          large: MaterialExpandedButton
        }
      }
    };
    
    return variants[component]?.[platform]?.[screenSize] || DefaultComponent;
  }
  
  static applyPlatformStyles(baseStyles: any, platform: string) {
    const platformOverrides = {
      ios: {
        fontFamily: 'System',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1
      },
      android: {
        fontFamily: 'Roboto',
        elevation: 4
      }
    };
    
    return {
      ...baseStyles,
      ...platformOverrides[platform]
    };
  }
}
```

### 4. Mobile DevOps Pipeline
```yaml
# Mobile CI/CD Pipeline Configuration
name: Mobile App Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: |
          npm install
          cd ios && pod install
          
      - name: Run tests
        run: |
          npm test
          npm run test:e2e:ios
          npm run test:e2e:android
          
  build-ios:
    needs: test
    runs-on: macos-latest
    steps:
      - name: Build iOS app
        run: |
          xcodebuild -workspace ios/App.xcworkspace \
            -scheme App \
            -configuration Release \
            -archivePath $PWD/build/App.xcarchive \
            archive
            
      - name: Export IPA
        run: |
          xcodebuild -exportArchive \
            -archivePath $PWD/build/App.xcarchive \
            -exportPath $PWD/build \
            -exportOptionsPlist ios/ExportOptions.plist
            
  build-android:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Android app
        run: |
          cd android
          ./gradlew assembleRelease
          ./gradlew bundleRelease
          
  deploy:
    needs: [build-ios, build-android]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to stores
        run: |
          fastlane ios release
          fastlane android release
```

## Quality Assurance Checklists

### Mobile Development Checklist
- [ ] Cross-platform compatibility verified
- [ ] Platform-specific features properly implemented
- [ ] Responsive design tested on multiple screen sizes
- [ ] Gesture interactions smooth and intuitive
- [ ] Offline functionality working correctly
- [ ] Push notifications tested in all states
- [ ] Deep linking configured and tested
- [ ] Performance metrics within acceptable ranges
- [ ] Memory leaks checked and fixed
- [ ] App size optimized

### Platform-Specific Checklist
- [ ] iOS: App Store guidelines compliance
- [ ] iOS: iPad compatibility (if universal app)
- [ ] iOS: Dark mode support
- [ ] Android: Material Design compliance
- [ ] Android: Back button handling
- [ ] Android: Multiple screen densities support
- [ ] Platform-specific permissions handled correctly
- [ ] Native module integration tested
- [ ] Platform-specific UI elements properly styled

### Performance Checklist
- [ ] App launch time under 2 seconds
- [ ] List scrolling at 60 FPS
- [ ] Image loading optimized with caching
- [ ] Network requests minimized and batched
- [ ] JavaScript bundle size optimized
- [ ] Memory usage profiled and optimized
- [ ] Battery usage within acceptable limits
- [ ] Background task efficiency verified

### Security Checklist
- [ ] Sensitive data encrypted in storage
- [ ] Network communication uses HTTPS
- [ ] Certificate pinning implemented
- [ ] Biometric authentication properly integrated
- [ ] Secure storage for tokens and credentials
- [ ] Input validation on all forms
- [ ] Code obfuscation enabled for release builds
- [ ] Security headers properly configured

## Integration Specifications

### Backend API Integration
- **RESTful API**: Optimized endpoints for mobile consumption
- **GraphQL**: Efficient data fetching with minimal over-fetching
- **WebSocket**: Real-time updates with connection management
- **Offline Queue**: Request queuing for offline scenarios

### Third-Party Service Integration
- **Analytics**: Firebase Analytics, Mixpanel, Amplitude
- **Crash Reporting**: Crashlytics, Sentry, Bugsnag
- **Push Notifications**: FCM, APNs, OneSignal
- **Payment Processing**: Stripe, Apple Pay, Google Pay

### Native Module Integration
- **Camera/Gallery**: Image capture and selection
- **Location Services**: GPS and geofencing
- **Biometric Auth**: Face ID, Touch ID, fingerprint
- **Bluetooth**: Device connectivity and data transfer

### CI/CD Integration
- **Build Automation**: Fastlane, Bitrise, App Center
- **Testing**: Detox, Appium, XCTest, Espresso
- **Distribution**: TestFlight, Play Console, Firebase Distribution
- **Monitoring**: Performance monitoring and crash reporting

## Error Handling and Recovery

### Network Error Handling
- **Retry Logic**: Exponential backoff for failed requests
- **Offline Detection**: Real-time network status monitoring
- **Cache Fallback**: Serve cached data when offline
- **User Feedback**: Clear error messages and retry options

### App Crash Recovery
- **Crash Reporting**: Automatic crash report collection
- **State Restoration**: Restore app state after crash
- **Safe Mode**: Fallback mode for critical errors
- **User Communication**: Inform users about issues

### Data Synchronization Errors
- **Conflict Resolution**: Automatic and manual conflict handling
- **Partial Sync**: Continue sync despite individual failures
- **Sync Status**: Visual indicators for sync state
- **Error Recovery**: Automatic retry with error tracking

## Performance Guidelines

### App Launch Performance
- **Cold Start**: Under 2 seconds to interactive
- **Warm Start**: Under 1 second to interactive
- **Splash Screen**: Immediate display with smooth transition
- **Initial Data**: Lazy load non-critical data

### Runtime Performance
- **Frame Rate**: Maintain 60 FPS for animations
- **Response Time**: UI interactions under 100ms
- **List Performance**: Smooth scrolling for 10k+ items
- **Memory Usage**: Stay within device constraints

### Network Performance
- **API Calls**: Minimize and batch requests
- **Caching**: Aggressive caching with smart invalidation
- **Compression**: Enable gzip/brotli compression
- **Image Optimization**: Multiple resolutions and formats

### Battery Performance
- **Background Tasks**: Minimize and batch background work
- **Location Updates**: Use appropriate accuracy levels
- **Network Requests**: Respect device power state
- **Wake Locks**: Minimize and properly release

## Command Reference

### React Native Commands
```bash
# Project setup and development
mobile-agent create-app --name MyApp --template typescript
mobile-agent setup-ios --configure-signing --team-id XXXXX
mobile-agent setup-android --configure-keystore --package com.company.app

# Development workflow
mobile-agent start --reset-cache --port 8082
mobile-agent run-ios --device "iPhone 14 Pro" --configuration Debug
mobile-agent run-android --variant release --device emulator-5554

# Code quality and optimization
mobile-agent analyze-bundle --platform ios --visualize
mobile-agent optimize-images --quality 85 --resize
mobile-agent check-dependencies --audit-fix --update-safe

# Testing
mobile-agent test --coverage --watch
mobile-agent test:e2e --platform both --record
mobile-agent test:performance --iterations 10 --report

# Deployment
mobile-agent build-ios --export-method app-store --upload-symbols
mobile-agent build-android --aab --upload-to-play-store
mobile-agent deploy --stage production --rollout-percentage 10
```

### Flutter Commands
```bash
# Project management
mobile-agent flutter create --platforms ios,android,web --org com.company
mobile-agent flutter analyze --fatal-warnings --no-pub
mobile-agent flutter format --line-length 100

# Development
mobile-agent flutter run --flavor development --dart-define ENV=dev
mobile-agent flutter attach --device-id XXXX --debug-port 5555
mobile-agent flutter screenshot --device ios --out screenshots/

# Building and deployment
mobile-agent flutter build appbundle --obfuscate --split-debug-info
mobile-agent flutter build ios --release --no-codesign
mobile-agent flutter deploy --track beta --release-notes "Bug fixes"

# Performance and debugging
mobile-agent flutter profile --start-paused --cache-sksl
mobile-agent flutter trace --duration 10s --out trace.json
mobile-agent flutter symbolize --input stack_trace.txt
```

### Native Platform Commands
```bash
# iOS specific
mobile-agent ios setup-certificates --type development --auto-provision
mobile-agent ios archive --workspace App.xcworkspace --upload-to-testflight
mobile-agent ios symbolicate --crash-report crash.txt --dsym MyApp.dSYM

# Android specific
mobile-agent android generate-signed-apk --keystore release.keystore
mobile-agent android analyze-apk --apk app-release.apk --human-readable
mobile-agent android profile-startup --package com.app --cold-start

# Cross-platform utilities
mobile-agent generate-icons --source icon.png --platforms all
mobile-agent generate-splash --source splash.png --background "#FFFFFF"
mobile-agent setup-push-notifications --ios-team-id XXX --android-sender-id YYY
```

### Performance and Monitoring Commands
```bash
# Performance analysis
mobile-agent profile-performance --duration 60s --cpu --memory --fps
mobile-agent analyze-memory-leaks --platform ios --detailed
mobile-agent measure-startup-time --cold --warm --iterations 10

# Monitoring setup
mobile-agent setup-crashlytics --ios-app-id XXX --android-app-id YYY
mobile-agent configure-analytics --events custom_events.json
mobile-agent setup-performance-monitoring --sample-rate 0.1

# Debugging
mobile-agent debug-network --proxy-port 8888 --log-requests
mobile-agent inspect-database --app-id com.app --table users
mobile-agent capture-view-hierarchy --format json --output hierarchy.json
```

This comprehensive Mobile Development Agent provides extensive capabilities for building high-quality mobile applications across multiple platforms, with focus on performance, user experience, and efficient cross-platform development strategies.