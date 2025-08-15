import React, { useState, useRef, useEffect } from 'react'
import { Volume2, VolumeX, Play, Pause, SkipBack, SkipForward, Mic, MicOff } from 'lucide-react'

interface AudioControllerProps {
  lastAudio: string
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
  const [audioFiles, setAudioFiles] = useState<string[]>([
    'system-startup.mp3',
    'task-complete.mp3',
    'agent-notification.mp3',
    'error-alert.mp3'
  ])

  // Mock audio visualizer data
  const [audioData, setAudioData] = useState<number[]>(
    Array.from({ length: 40 }, () => Math.random() * 100)
  )

  useEffect(() => {
    // Simulate real-time audio visualization
    if (isPlaying || isRecording) {
      const interval = setInterval(() => {
        setAudioData(prev => prev.map(() => Math.random() * 100))
      }, 100)
      return () => clearInterval(interval)
    }
  }, [isPlaying, isRecording])

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

  return (
    <div className="audio-controller">
      <div className="card-header">
        <h2 className="card-title">
          <Volume2 size={20} />
          Audio Controller
        </h2>
        <div className="text-sm text-muted">
          Last: {lastAudio || 'No recent audio'}
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

      {/* Audio File List */}
      <div className="mt-6">
        <h3 className="font-medium mb-3">Audio Files</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {audioFiles.map((file, index) => (
            <div
              key={index}
              className={`flex items-center justify-between p-2 rounded bg-secondary hover:bg-tertiary transition-colors cursor-pointer ${
                file === lastAudio ? 'border-l-2 border-accent-primary' : ''
              }`}
              onClick={() => console.log('Load audio file:', file)}
            >
              <span className="text-sm">{file}</span>
              <button className="btn btn-secondary text-xs">
                Load
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

      {/* Audio Settings */}
      <div className="mt-6 p-4 bg-secondary rounded-lg">
        <h3 className="font-medium mb-3">Audio Settings</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">Output Device</label>
            <select className="w-full text-sm">
              <option>Default</option>
              <option>Speakers</option>
              <option>Headphones</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1">Quality</label>
            <select className="w-full text-sm">
              <option>High (320kbps)</option>
              <option>Medium (192kbps)</option>
              <option>Low (128kbps)</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <span className="text-sm">Auto-play notifications</span>
          <input type="checkbox" defaultChecked />
        </div>
        
        <div className="mt-2 flex items-center justify-between">
          <span className="text-sm">Reduce background noise</span>
          <input type="checkbox" defaultChecked />
        </div>
      </div>
    </div>
  )
}