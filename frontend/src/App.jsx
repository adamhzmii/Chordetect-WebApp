import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [chords, setChords] = useState(null)
  const [error, setError] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setAudioUrl(URL.createObjectURL(selectedFile))
      setChords(null)
      setError(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('audio', file)

    try {
      const response = await fetch('http://127.0.0.1:5000/api/detect-chords', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        setChords(data)
      } else {
        setError(data.error || 'Failed to detect chords')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure backend is running!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>🎸 Guitar Chord Detector</h1>
        <p>Upload an MP3 file and get the guitar chords</p>
      </header>

      <main>
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-wrapper">
            <input
              type="file"
              accept="audio/mp3,audio/mpeg,audio/wav"
              onChange={handleFileChange}
              id="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              {file ? file.name : 'Choose an audio file'}
            </label>
          </div>

          <button type="submit" disabled={!file || loading}>
            {loading ? 'Detecting Chords...' : 'Detect Chords'}
          </button>
        </form>

        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {audioUrl && (
          <div className="audio-player">
            <h3>Audio Preview:</h3>
            <audio controls src={audioUrl} />
          </div>
        )}

        {chords && (
          <div className="results">
            <h2>Detected Chords</h2>
            <p>Duration: {chords.duration.toFixed(2)} seconds</p>
            
            <div className="chord-list">
              {chords.chords.map((item, index) => (
                <div key={index} className="chord-item">
                  <span className="time">{item.time.toFixed(2)}s</span>
                  <span className="chord">{item.chord}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App