import http from 'k6/http';
import { check, sleep } from 'k6';

// Target the live app (override with -e BASE_URL=... if needed)
const BASE = __ENV.BASE_URL || 'http://4.166.180.215';

export const options = {
  stages: [
    { duration: '30s', target: 10 }, // ramp up to 10 virtual users
    { duration: '1m', target: 10 },  // hold at 10
    { duration: '30s', target: 0 },  // ramp back down
  ],
};

export default function () {
  const params = { headers: { 'Content-Type': 'application/json' } };

  // 1. Create a short link
  const res = http.post(
    `${BASE}/api/links`,
    JSON.stringify({ target_url: 'https://example.com' }),
    params,
  );
  check(res, { 'create returns 201': (r) => r.status === 201 });

  // 2. List all links
  const list = http.get(`${BASE}/api/links`);
  check(list, { 'list returns 200': (r) => r.status === 200 });

  // 3. Follow the new short code (don't auto-follow, so we see the 307)
  if (res.status === 201) {
    const code = res.json('code');
    const redir = http.get(`${BASE}/${code}`, { redirects: 0 });
    check(redir, { 'redirect returns 307': (r) => r.status === 307 });
  }

  sleep(1);
}
