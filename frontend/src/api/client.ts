import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail ?? err.message
    return Promise.reject(new Error(formatApiError(detail)))
  }
)

export function wsUrl(path: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/api${path}`
}

function formatApiError(detail: unknown): string {
  if (typeof detail === 'string') {
    return detail
  }

  if (typeof detail === 'number' || typeof detail === 'boolean') {
    return String(detail)
  }

  if (Array.isArray(detail)) {
    const parts = detail.map(formatApiError).filter(Boolean)
    return parts.join('; ') || 'Request failed'
  }

  if (detail && typeof detail === 'object') {
    const record = detail as Record<string, unknown>

    if (typeof record.msg === 'string') {
      const location = Array.isArray(record.loc) ? record.loc.join('.') : null
      return location ? `${location}: ${record.msg}` : record.msg
    }

    if ('detail' in record) {
      return formatApiError(record.detail)
    }

    try {
      return JSON.stringify(record)
    } catch {
      return 'Request failed'
    }
  }

  return 'Request failed'
}
