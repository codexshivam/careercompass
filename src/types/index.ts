export type Tab = 'simulator' | 'salary' | 'matrix' | 'personas'

export interface CompetencyField {
  id: string
  name: string
  low: string
  mid: string
  high: string
  default: number
}

export interface RoleConfig {
  code: string
  label: string
}

export interface PremiumChartItem {
  role: string
  premium: number
}

export interface SalaryConfig {
  roles: RoleConfig[]
  premiumsChart: PremiumChartItem[]
}

export interface SalaryEstimate {
  total: number
  expAdd: number
  premium: number
  bump: number
}

export interface MatrixItem {
  tag: string
  impact: string
  title: string
  demand: string
  impactRating: string
  description: string
}

export interface PersonaItem {
  id: string
  badge: string
  title: string
  description: string
}
