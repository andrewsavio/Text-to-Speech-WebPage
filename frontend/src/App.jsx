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

      const url = window.URL.createObjectURL(new Blob([response.data]));
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
            <audio controls src={audioUrl} autoPlay>
              Your browser does not support the audio element.
            </audio>
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
