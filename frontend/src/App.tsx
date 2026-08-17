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
    const target = url.trim()
    if (!target) return
    await fetch('/api/links', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_url: target }),
    })
    setUrl('')
    loadLinks()
  }

  return (
    <main className="container">
      <header className="hero">
        <h1>🔗 Shortlink</h1>
        <p className="subtitle">Paste a long URL, get a short one.</p>
      </header>

      <form className="shorten-form" onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="https://example.com/very/long/url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit">Shorten</button>
      </form>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Short code</th>
              <th>Target URL</th>
              <th className="clicks-col">Clicks</th>
            </tr>
          </thead>
          <tbody>
            {links.length === 0 ? (
              <tr>
                <td colSpan={3} className="empty">No links yet — shorten one above.</td>
              </tr>
            ) : (
              links.map((link) => (
                <tr key={link.id}>
                  <td>
                    <a
                      className="code"
                      href={`/${link.code}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      /{link.code}
                    </a>
                  </td>
                  <td className="target">
                    <a href={link.target_url} target="_blank" rel="noreferrer">
                      {link.target_url}
                    </a>
                  </td>
                  <td className="clicks-col">{link.clicks}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <footer className="footer">
        A DevOps portfolio project — the infrastructure is the point.
      </footer>
    </main>
  )
}

export default App
