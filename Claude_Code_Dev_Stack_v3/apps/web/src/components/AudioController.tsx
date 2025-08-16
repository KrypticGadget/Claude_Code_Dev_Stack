import React, { useState, useRef, useEffect } from 'react'
import { Volume2, VolumeX, Play, Pause, SkipBack, SkipForward, Mic, MicOff, Settings, Activity } from 'lucide-react'

interface AudioControllerProps {
  lastAudio: string
}

interface AudioEvent {
  id: string
  type: 'system' | 'agent' | 'phase' | 'error' | 'success'
  phase: string
  agent?: string
  operation: string
  timestamp: number
  audioFile?: string
}

interface PhaseAudioSettings {
  enabled: boolean
  volume: number
  frequency: 'low' | 'normal' | 'high'
}

export const AudioController: React.FC<AudioControllerProps> = ({ lastAudio }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [volume, setVolume] = useState(0.7)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  
  // Enhanced audio system state
  const [currentPhase, setCurrentPhase] = useState('initialization')
  const [activeAgents, setActiveAgents] = useState<string[]>([])
  const [audioEvents, setAudioEvents] = useState<AudioEvent[]>([])
  const [phaseSettings, setPhaseSettings] = useState<Record<string, PhaseAudioSettings>>({
    initialization: { enabled: true, volume: 0.8, frequency: 'high' },
    planning: { enabled: true, volume: 0.6, frequency: 'normal' },
    implementation: { enabled: true, volume: 0.5, frequency: 'normal' },
    testing: { enabled: true, volume: 0.7, frequency: 'high' },
    deployment: { enabled: true, volume: 0.9, frequency: 'high' }
  })
  const [showSettings, setShowSettings] = useState(false)
  
  // Complete audio file list from the system
  const [audioFiles, setAudioFiles] = useState<string[]>([
    'startup.wav',
    'ready_for_input.wav',
    'agent_activated.wav',
    'pipeline_complete.wav',
    'pipeline_initiated.wav',
    'confirm_required.wav',
    'file_operation_complete.wav',
    'command_successful.wav',
    'phase_complete.wav',
    'milestone_complete.wav',
    'build_successful.wav',
    'tests_passed.wav',
    'git_commit.wav',
    'frontend_agent.wav',
    'backend_agent.wav',
    'database_agent.wav',
    'master_orchestrator.wav',
    'v3_feature_activated.wav'
  ])

  // Mock audio visualizer data
  const [audioData, setAudioData] = useState<number[]>(
    Array.from({ length: 40 }, () => Math.random() * 100)
  )

  // API connection for real-time audio events
  useEffect(() => {
    // Simulate real-time audio visualization
    if (isPlaying || isRecording) {
      const interval = setInterval(() => {
        setAudioData(prev => prev.map(() => Math.random() * 100))
      }, 100)
      return () => clearInterval(interval)
    }
  }, [isPlaying, isRecording])

  // Listen for phase-aware audio events
  useEffect(() => {
    // Simulate receiving audio events from the backend
    const interval = setInterval(() => {
      // Mock event generation
      if (Math.random() > 0.8) {
        const mockEvent: AudioEvent = {
          id: `event_${Date.now()}`,
          type: ['system', 'agent', 'phase', 'success', 'error'][Math.floor(Math.random() * 5)] as any,
          phase: currentPhase,
          agent: activeAgents[Math.floor(Math.random() * activeAgents.length)],
          operation: ['file_edit', 'git_commit', 'test_run', 'build'][Math.floor(Math.random() * 4)],
          timestamp: Date.now(),
          audioFile: audioFiles[Math.floor(Math.random() * audioFiles.length)]
        }
        
        setAudioEvents(prev => [mockEvent, ...prev.slice(0, 49)]) // Keep last 50 events
        
        // Auto-play if enabled
        if (phaseSettings[currentPhase]?.enabled) {
          playAudioEvent(mockEvent)
        }
      }
    }, 5000)
    
    return () => clearInterval(interval)
  }, [currentPhase, activeAgents, audioFiles, phaseSettings])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration || 0)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [])

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play().catch(console.error)
    }
    setIsPlaying(!isPlaying)
  }

  const toggleMute = () => {
    const audio = audioRef.current
    if (!audio) return

    audio.muted = !isMuted
    setIsMuted(!isMuted)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)
    
    const audio = audioRef.current
    if (audio) {
      audio.volume = newVolume
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value)
    setCurrentTime(newTime)
    
    const audio = audioRef.current
    if (audio) {
      audio.currentTime = newTime
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      
      const chunks: BlobPart[] = []
      
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data)
      }
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(blob)
        const fileName = `recording-${Date.now()}.wav`
        setAudioFiles(prev => [...prev, fileName])
        console.log('Recording saved:', fileName)
      }
      
      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      setIsRecording(false)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const playAudioEvent = (event: AudioEvent) => {
    if (event.audioFile && !isMuted) {
      const audio = new Audio(`/audio/${event.audioFile}`)
      const phaseVol = phaseSettings[event.phase]?.volume || volume
      audio.volume = phaseVol
      audio.play().catch(console.error)
    }
  }

  const handlePhaseChange = (newPhase: string) => {
    setCurrentPhase(newPhase)
    // Trigger phase transition sound
    const phaseEvent: AudioEvent = {
      id: `phase_${Date.now()}`,
      type: 'phase',
      phase: newPhase,
      operation: 'phase_transition',
      timestamp: Date.now(),
      audioFile: 'phase_complete.wav'
    }
    setAudioEvents(prev => [phaseEvent, ...prev.slice(0, 49)])
    playAudioEvent(phaseEvent)
  }

  const addAgent = (agentName: string) => {
    if (!activeAgents.includes(agentName)) {
      setActiveAgents(prev => [...prev, agentName])
      const agentEvent: AudioEvent = {
        id: `agent_${Date.now()}`,
        type: 'agent',
        phase: currentPhase,
        agent: agentName,
        operation: 'agent_activate',
        timestamp: Date.now(),
        audioFile: 'agent_activated.wav'
      }
      setAudioEvents(prev => [agentEvent, ...prev.slice(0, 49)])
      playAudioEvent(agentEvent)
    }
  }

  const removeAgent = (agentName: string) => {
    setActiveAgents(prev => prev.filter(agent => agent !== agentName))
  }

  const testAudioFile = (filename: string) => {
    const audio = new Audio(`/audio/${filename}`)
    audio.volume = volume
    audio.play().catch(console.error)
  }

  const getEventTypeColor = (type: string) => {
    const colors = {
      system: 'bg-blue-500',
      agent: 'bg-green-500',
      phase: 'bg-purple-500',
      success: 'bg-green-600',
      error: 'bg-red-500'
    }
    return colors[type as keyof typeof colors] || 'bg-gray-500'
  }

  return (
    <div className="audio-controller">
      <div className="card-header">
        <h2 className="card-title">
          <Volume2 size={20} />
          Phase-Aware Audio Controller
        </h2>
        <div className="flex items-center gap-4 text-sm text-muted">
          <span>Phase: <strong className="text-accent-primary">{currentPhase}</strong></span>
          <span>Agents: <strong className="text-accent-primary">{activeAgents.length}</strong></span>
          <span>Events: <strong className="text-accent-primary">{audioEvents.length}</strong></span>
        </div>
      </div>

      {/* Phase Controls */}
      <div className="mb-4 p-3 bg-secondary rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium">Development Phase</h3>
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className="btn btn-secondary text-xs"
          >
            <Settings size={14} />
          </button>
        </div>
        
        <div className="grid grid-cols-3 gap-2">
          {Object.keys(phaseSettings).map(phase => (
            <button
              key={phase}
              onClick={() => handlePhaseChange(phase)}
              className={`btn text-xs py-2 ${
                currentPhase === phase 
                  ? 'btn-primary' 
                  : 'btn-secondary'
              }`}
            >
              {phase.charAt(0).toUpperCase() + phase.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Active Agents */}
      <div className="mb-4 p-3 bg-secondary rounded-lg">
        <h3 className="font-medium mb-2">Active Agents</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {activeAgents.map(agent => (
            <span 
              key={agent}
              className="px-2 py-1 bg-accent-primary text-white rounded text-xs flex items-center gap-1"
            >
              <Activity size={12} />
              {agent}
              <button 
                onClick={() => removeAgent(agent)}
                className="ml-1 hover:bg-white hover:bg-opacity-20 rounded"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          {['frontend', 'backend', 'database', 'mobile', 'testing', 'orchestrator'].map(agent => (
            <button
              key={agent}
              onClick={() => addAgent(agent)}
              disabled={activeAgents.includes(agent)}
              className="btn btn-outline text-xs py-1 disabled:opacity-50"
            >
              Add {agent}
            </button>
          ))}
        </div>
      </div>

      {/* Audio Controls */}
      <div className="audio-controls">
        <button className="audio-button" onClick={() => console.log('Previous track')}>
          <SkipBack size={16} />
        </button>
        
        <button className="audio-button" onClick={togglePlay}>
          {isPlaying ? <Pause size={20} /> : <Play size={20} />}
        </button>
        
        <button className="audio-button" onClick={() => console.log('Next track')}>
          <SkipForward size={16} />
        </button>
        
        <button className="audio-button" onClick={toggleMute}>
          {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </button>
        
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={handleVolumeChange}
          className="w-24"
        />
        
        <button 
          className={`audio-button ${isRecording ? 'bg-red-500' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
        >
          {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
        </button>
      </div>

      {/* Audio Visualizer */}
      <div className="audio-waveform">
        <div className="flex items-end justify-center h-full gap-1 px-4">
          {audioData.map((value, index) => (
            <div
              key={index}
              className="bg-white bg-opacity-30 rounded-sm transition-all duration-75"
              style={{
                height: `${Math.max(2, value)}%`,
                width: '3px'
              }}
            />
          ))}
        </div>
        {(isPlaying || isRecording) && <div className="waveform-animation" />}
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="flex items-center gap-3 text-sm">
          <span className="font-mono">{formatTime(currentTime)}</span>
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={currentTime}
            onChange={handleSeek}
            className="flex-1"
            disabled={!duration}
          />
          <span className="font-mono">{formatTime(duration)}</span>
        </div>
      </div>

      {/* Audio Events Log */}
      <div className="mt-6">
        <h3 className="font-medium mb-3">Recent Audio Events</h3>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {audioEvents.slice(0, 10).map((event) => (
            <div
              key={event.id}
              className="flex items-center justify-between p-2 rounded bg-secondary hover:bg-tertiary transition-colors"
            >
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${getEventTypeColor(event.type)}`} />
                <div className="text-sm">
                  <div className="font-medium">{event.operation}</div>
                  <div className="text-xs text-muted">
                    {event.agent && `${event.agent} • `}
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
              <button 
                onClick={() => event.audioFile && testAudioFile(event.audioFile)}
                className="btn btn-secondary text-xs"
                disabled={!event.audioFile}
              >
                Play
              </button>
            </div>
          ))}
          {audioEvents.length === 0 && (
            <div className="text-center text-muted text-sm py-4">
              No audio events yet
            </div>
          )}
        </div>
      </div>

      {/* Audio File Library */}
      <div className="mt-6">
        <h3 className="font-medium mb-3">Audio Library ({audioFiles.length} files)</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {audioFiles.map((file, index) => (
            <div
              key={index}
              className={`flex items-center justify-between p-2 rounded bg-secondary hover:bg-tertiary transition-colors ${
                file === lastAudio ? 'border-l-2 border-accent-primary' : ''
              }`}
            >
              <span className="text-sm font-mono">{file}</span>
              <button 
                className="btn btn-secondary text-xs"
                onClick={() => testAudioFile(file)}
              >
                Test
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Audio Element */}
      <audio
        ref={audioRef}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        preload="metadata"
      >
        <source src="/audio/sample.mp3" type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>

      {/* Enhanced Audio Settings */}
      {showSettings && (
        <div className="mt-6 p-4 bg-secondary rounded-lg">
          <h3 className="font-medium mb-3">Phase-Aware Audio Settings</h3>
          
          {/* Global Settings */}
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">Global Settings</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm mb-1">Output Device</label>
                <select className="w-full text-sm">
                  <option>Default Audio</option>
                  <option>Speakers</option>
                  <option>Headphones</option>
                </select>
              </div>
              <div>
                <label className="block text-sm mb-1">Audio Quality</label>
                <select className="w-full text-sm">
                  <option>High Quality</option>
                  <option>Standard</option>
                  <option>Low Bandwidth</option>
                </select>
              </div>
            </div>
          </div>

          {/* Phase-Specific Settings */}
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">Phase-Specific Settings</h4>
            <div className="space-y-3">
              {Object.entries(phaseSettings).map(([phase, settings]) => (
                <div key={phase} className="p-3 bg-tertiary rounded">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium capitalize">{phase}</span>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={settings.enabled}
                        onChange={(e) => setPhaseSettings(prev => ({
                          ...prev,
                          [phase]: { ...prev[phase], enabled: e.target.checked }
                        }))}
                      />
                      Enabled
                    </label>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs mb-1">Volume</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={settings.volume}
                        onChange={(e) => setPhaseSettings(prev => ({
                          ...prev,
                          [phase]: { ...prev[phase], volume: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                      <span className="text-xs text-muted">{Math.round(settings.volume * 100)}%</span>
                    </div>
                    
                    <div>
                      <label className="block text-xs mb-1">Frequency</label>
                      <select
                        value={settings.frequency}
                        onChange={(e) => setPhaseSettings(prev => ({
                          ...prev,
                          [phase]: { ...prev[phase], frequency: e.target.value as any }
                        }))}
                        className="w-full text-xs"
                      >
                        <option value="low">Low</option>
                        <option value="normal">Normal</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Auto-play notifications</span>
              <input type="checkbox" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm">Agent transition sounds</span>
              <input type="checkbox" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm">Error emphasis</span>
              <input type="checkbox" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm">Success celebrations</span>
              <input type="checkbox" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm">Cross-platform compatibility</span>
              <input type="checkbox" defaultChecked />
            </div>
          </div>

          {/* System Info */}
          <div className="mt-4 p-3 bg-tertiary rounded">
            <h4 className="text-sm font-medium mb-2">System Information</h4>
            <div className="text-xs text-muted space-y-1">
              <div>Platform: {navigator.platform}</div>
              <div>Audio Context: {typeof AudioContext !== 'undefined' ? 'Supported' : 'Not Supported'}</div>
              <div>Web Audio API: {typeof window.AudioContext !== 'undefined' ? 'Available' : 'Unavailable'}</div>
              <div>Media Devices: {navigator.mediaDevices ? 'Supported' : 'Not Supported'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}