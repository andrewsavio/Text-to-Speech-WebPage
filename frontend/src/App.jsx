import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Mic, Play, Download, Loader2, Volume2, Upload, Music } from 'lucide-react';
import './index.css';

const API_BASE_URL = 'http://localhost:8000'; // Adjust if needed

function App() {
  const [text, setText] = useState('');
  const [voiceFile, setVoiceFile] = useState(null);
  const [voiceUrl, setVoiceUrl] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [voices, setVoices] = useState([]);
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 3000); // 3 seconds splash
    return () => clearTimeout(timer);
  }, []);

  // Default presest voices
  // Default presest voices
  // Using keys recognized by pocket-tts for non-gated access
  const PRESETS = [
    { id: 'default', name: 'Select a Voice Preset...' },
    { id: 'alba', name: 'Alba (Casual)', url: 'alba' },
    { id: 'marius', name: 'Marius (Selfie)', url: 'marius' },
    { id: 'javert', name: 'Javert (Butter)', url: 'javert' },
    { id: 'jean', name: 'Jean (Freeform)', url: 'jean' },
    { id: 'fantine', name: 'Fantine', url: 'fantine' },
    { id: 'cosette', name: 'Cosette', url: 'cosette' },
    { id: 'eponine', name: 'Eponine', url: 'eponine' },
    { id: 'azelma', name: 'Azelma', url: 'azelma' },
  ];

  const handleGenerate = async () => {
    if (!text) return;
    setIsGenerating(true);
    setAudioUrl(null);

    const formData = new FormData();
    formData.append('text', text);

    if (voiceFile) {
      formData.append('voice_file', voiceFile);
    } else if (voiceUrl) {
      formData.append('voice_url', voiceUrl);
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, formData, {
        responseType: 'blob', // Important for audio
      });

      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'audio/wav' }));
      setAudioUrl(url);
    } catch (error) {
      console.error("Generation failed:", error);
      alert("Failed to generate audio. Check backend console.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setVoiceFile(e.target.files[0]);
      setVoiceUrl(''); // Clear preset if file uploaded
    }
  };

  const handlePresetChange = (e) => {
    const url = e.target.value;
    setVoiceUrl(url);
    setVoiceFile(null); // Clear file if preset selected
  };

  const handleDownload = async () => {
    if (!audioUrl) return;

    // Check if running in pywebview
    if (window.pywebview && window.pywebview.api) {
      try {
        // Convert blob URL to blob
        const blob = await fetch(audioUrl).then(r => r.blob());

        // Convert blob to base64
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = async () => {
          const base64data = reader.result;
          await window.pywebview.api.save_audio(base64data);
        };
      } catch (e) {
        console.error("Native save failed:", e);
        alert("Failed to save file natively.");
      }
    } else {
      // Fallback for web browser
      const link = document.createElement('a');
      link.href = audioUrl;
      link.download = 'generated_speech.wav';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <>
      <div className="background-mesh">
        <div className="mesh-blob mesh-1"></div>
        <div className="mesh-blob mesh-2"></div>
        <div className="mesh-blob mesh-3"></div>
      </div>

      <div className="glass-card">
        <div className="header">
          <h1>Pocket TTS</h1>
          <p>Instant high-quality text-to-speech on CPU</p>
        </div>

        <div className="input-group">
          <label>Your Text</label>
          <textarea
            placeholder="Type something amazing here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        <div className="input-group">
          <label>Voice Control</label>
          <div className="controls-row">
            <div className="select-wrapper">
              <select onChange={handlePresetChange} value={voiceUrl}>
                {PRESETS.map(v => (
                  <option key={v.id} value={v.url || ''}>{v.name}</option>
                ))}
              </select>
            </div>

            <label className="file-upload-btn">
              <Upload size={18} />
              {voiceFile ? voiceFile.name.substring(0, 10) + '...' : 'Upload Clone'}
              <input
                type="file"
                accept=".wav"
                hidden
                onChange={handleFileChange}
              />
            </label>
          </div>
        </div>

        <button
          className="generate-btn"
          onClick={handleGenerate}
          disabled={isGenerating || !text}
        >
          {isGenerating ? (
            <>
              <Loader2 className="spinner" /> Generating Audio...
            </>
          ) : (
            <>
              <Volume2 size={24} /> Generate Speech
            </>
          )}
        </button>

        {audioUrl && (
          <div className="audio-result glass-card" style={{ padding: '20px', marginTop: '10px', background: 'rgba(0,0,0,0.2)' }}>
            <audio controls src={audioUrl} autoPlay style={{ width: '100%', marginBottom: '10px' }} controlsList="nodownload">
              Your browser does not support the audio element.
            </audio>

            <button
              onClick={handleDownload}
              className="generate-btn"
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                marginTop: '10px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                textDecoration: 'none',
                fontSize: '0.9rem',
                width: '100%',
                cursor: 'pointer',
                border: 'none',
                color: 'white'
              }}
            >
              <Download size={18} style={{ marginRight: '8px' }} /> Download Audio
            </button>
          </div>
        )}
      </div>

      {showSplash && (
        <div className="splash-screen">
          <div className="splash-content">
            <img src="/andrew.png" alt="Logo" className="splash-logo" />
            <h1 className="splash-title">Andrew's TTS</h1>
            <div className="splash-loader"></div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
