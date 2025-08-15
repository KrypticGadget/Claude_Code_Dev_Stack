/**
 * Voice recognition service
 * Ported from Flutter VoiceService (@9cat) - MIT License
 * Uses react-native-voice for speech recognition
 */

import Voice, {
  SpeechRecognizedEvent,
  SpeechResultsEvent,
  SpeechErrorEvent,
} from '@react-native-voice/voice';

export class VoiceService {
  private static instance: VoiceService;
  private isInitialized: boolean = false;
  private isListening: boolean = false;
  private resultCallback: ((text: string) => void) | null = null;

  private constructor() {}

  static getInstance(): VoiceService {
    if (!VoiceService.instance) {
      VoiceService.instance = new VoiceService();
    }
    return VoiceService.instance;
  }

  get initialized(): boolean {
    return this.isInitialized;
  }

  get listening(): boolean {
    return this.isListening;
  }

  async initialize(): Promise<boolean> {
    if (this.isInitialized) return true;

    try {
      // Set up Voice event listeners
      Voice.onSpeechStart = this.onSpeechStart.bind(this);
      Voice.onSpeechRecognized = this.onSpeechRecognized.bind(this);
      Voice.onSpeechEnd = this.onSpeechEnd.bind(this);
      Voice.onSpeechError = this.onSpeechError.bind(this);
      Voice.onSpeechResults = this.onSpeechResults.bind(this);
      Voice.onSpeechPartialResults = this.onSpeechPartialResults.bind(this);
      Voice.onSpeechVolumeChanged = this.onSpeechVolumeChanged.bind(this);

      // Check if speech recognition is available
      const available = await Voice.isAvailable();
      if (!available) {
        console.warn('Speech recognition not available on this device');
        return false;
      }

      this.isInitialized = true;
      console.log('✅ VoiceService: Initialized successfully');
      return true;
    } catch (error) {
      console.error('❌ VoiceService: Failed to initialize:', error);
      return false;
    }
  }

  async startListening(onResult: (text: string) => void): Promise<void> {
    if (!this.isInitialized || this.isListening) {
      console.warn('VoiceService: Cannot start listening - not initialized or already listening');
      return;
    }

    try {
      this.resultCallback = onResult;
      this.isListening = true;

      await Voice.start('en-US', {
        EXTRA_LANGUAGE_MODEL: 'LANGUAGE_MODEL_FREE_FORM',
        EXTRA_CALLING_PACKAGE: 'com.claudecode.mobile',
        EXTRA_PARTIAL_RESULTS: false,
        REQUEST_PERMISSIONS_AUTO: true,
      });

      console.log('🎤 VoiceService: Started listening');
    } catch (error) {
      console.error('❌ VoiceService: Failed to start listening:', error);
      this.isListening = false;
      this.resultCallback = null;
    }
  }

  async stopListening(): Promise<void> {
    if (!this.isListening) return;

    try {
      await Voice.stop();
      this.isListening = false;
      this.resultCallback = null;
      console.log('🛑 VoiceService: Stopped listening');
    } catch (error) {
      console.error('❌ VoiceService: Failed to stop listening:', error);
    }
  }

  async cancelListening(): Promise<void> {
    try {
      await Voice.cancel();
      this.isListening = false;
      this.resultCallback = null;
      console.log('❌ VoiceService: Cancelled listening');
    } catch (error) {
      console.error('❌ VoiceService: Failed to cancel listening:', error);
    }
  }

  async getAvailableLanguages(): Promise<string[]> {
    try {
      const languages = await Voice.getSupportedLocales();
      return languages || [];
    } catch (error) {
      console.error('❌ VoiceService: Failed to get available languages:', error);
      return [];
    }
  }

  // Event handlers
  private onSpeechStart(event: any): void {
    console.log('🎤 VoiceService: Speech started');
  }

  private onSpeechRecognized(event: SpeechRecognizedEvent): void {
    console.log('🎤 VoiceService: Speech recognized');
  }

  private onSpeechEnd(event: any): void {
    console.log('🎤 VoiceService: Speech ended');
    this.isListening = false;
  }

  private onSpeechError(event: SpeechErrorEvent): void {
    console.error('❌ VoiceService: Speech error:', event.error);
    this.isListening = false;
    this.resultCallback = null;
  }

  private onSpeechResults(event: SpeechResultsEvent): void {
    const results = event.value;
    if (results && results.length > 0) {
      const recognizedText = results[0];
      console.log('✅ VoiceService: Speech result:', recognizedText);
      
      if (this.resultCallback) {
        this.resultCallback(recognizedText);
      }
      
      this.stopListening();
    }
  }

  private onSpeechPartialResults(event: SpeechResultsEvent): void {
    const results = event.value;
    if (results && results.length > 0) {
      console.log('🎤 VoiceService: Partial result:', results[0]);
    }
  }

  private onSpeechVolumeChanged(event: any): void {
    // Handle volume changes if needed
  }

  async destroy(): Promise<void> {
    try {
      await Voice.destroy();
      this.isInitialized = false;
      this.isListening = false;
      this.resultCallback = null;
      
      // Remove event listeners
      Voice.removeAllListeners();
      
      console.log('🗑️ VoiceService: Destroyed');
    } catch (error) {
      console.error('❌ VoiceService: Failed to destroy:', error);
    }
  }
}