const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000'

import type {
  CompetencyField,
  SalaryConfig,
  SalaryEstimate,
  MatrixItem,
  PersonaItem,
} from './types'

export async function fetchCompetencies(): Promise<CompetencyField[]> {
  const res = await fetch(`${API_BASE}/api/meta/competencies`)
  if (!res.ok) throw new Error('Failed to fetch competencies')
  return res.json()
}

export async function fetchSalaryConfig(): Promise<SalaryConfig> {
  const res = await fetch(`${API_BASE}/api/salary/config`)
  if (!res.ok) throw new Error('Failed to fetch salary configuration')
  return res.json()
}

export async function calculateSalary(params: {
  role: string
  experience: number
  senior: boolean
  location: string
}): Promise<SalaryEstimate> {
  const res = await fetch(`${API_BASE}/api/salary/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error('Failed to calculate salary estimate')
  return res.json()
}

export async function fetchMatrix(): Promise<MatrixItem[]> {
  const res = await fetch(`${API_BASE}/api/matrix`)
  if (!res.ok) throw new Error('Failed to fetch skill matrix')
  return res.json()
}

export async function fetchPersonas(): Promise<PersonaItem[]> {
  const res = await fetch(`${API_BASE}/api/personas`)
  if (!res.ok) throw new Error('Failed to fetch leadership personas')
  return res.json()
}

export async function predictPromotion(scores: {
  dashboard: number
  maths: number
  ai_ml: number
  big_data: number
  coding: number
}, signal?: AbortSignal) {
  const res = await fetch(`${API_BASE}/predict/promotion`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scores),
    signal,
  })
  if (!res.ok) throw new Error('Promotion prediction failed')
  return res.json()
}
