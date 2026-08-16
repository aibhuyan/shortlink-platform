import { useEffect, useState, type FormEvent } from 'react'
import './App.css'

type Link = {
  id: number
  code: string
  target_url: string
  clicks: number
}

function App() {
  const [url, setUrl] = useState('')
  const [links, setLinks] = useState<Link[]>([])

  async function loadLinks() {
    const res = await fetch('/api/links')
    const data = await res.json()
    setLinks(data)
  }

  useEffect(() => {
    loadLinks()
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    await fetch('/api/links', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_url: url }),
    })
    setUrl('')
    loadLinks()
  }

  return (
    <main>
      <h1>Shortlink</h1>

      <form onSubmit={handleSubmit}>
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
          {links.map((link) => (
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
