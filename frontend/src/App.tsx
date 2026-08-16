import { useState } from 'react'
import './App.css'

type Link = {
  id: number
  code: string
  target_url: string
  clicks: number
}

const SAMPLE_LINKS: Link[] = [
  { id: 1, code: 'abc123', target_url: 'https://example.com', clicks: 5 },
  { id: 2, code: 'xy9zQ', target_url: 'https://python.org', clicks: 12 },
]

function App() {
  const [url, setUrl] = useState('')

  return (
    <main>
      <h1>Shortlink</h1>

      <form>
        <input
          type="url"
          placeholder="Paste a long URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit">Shorten</button>
      </form>

      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Target URL</th>
            <th>Clicks</th>
          </tr>
        </thead>
        <tbody>
          {SAMPLE_LINKS.map((link) => (
            <tr key={link.id}>
              <td>{link.code}</td>
              <td>{link.target_url}</td>
              <td>{link.clicks}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  )
}

export default App
