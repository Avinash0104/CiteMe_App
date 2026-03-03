/**
 * Unified grading system for the application
 * Centralizes all grade-to-color and grade-to-letter mappings
 */

export interface GradeThreshold {
  min: number
  max: number
  letter: string
  color: string
  textColor: string
  bgColor: string
  label: string
}

export const GRADE_THRESHOLDS: GradeThreshold[] = [
  {
    min: 90,
    max: 100,
    letter: 'A',
    color: 'green',
    textColor: 'text-green-600',
    bgColor: 'bg-green-600',
    label: '90-100%'
  },
  {
    min: 80,
    max: 89,
    letter: 'B',
    color: 'blue',
    textColor: 'text-blue-500',
    bgColor: 'bg-blue-500',
    label: '80-89%'
  },
  {
    min: 70,
    max: 79,
    letter: 'C',
    color: 'yellow',
    textColor: 'text-yellow-500',
    bgColor: 'bg-yellow-500',
    label: '70-79%'
  },
  {
    min: 60,
    max: 69,
    letter: 'D',
    color: 'orange',
    textColor: 'text-orange-400',
    bgColor: 'bg-orange-400',
    label: '60-69%'
  },
  {
    min: 0,
    max: 59,
    letter: 'F',
    color: 'red',
    textColor: 'text-red-600',
    bgColor: 'bg-red-600',
    label: '0-59%'
  }
]

/**
 * Get the grade threshold object for a given score
 */
export function getGradeThreshold(score: number): GradeThreshold {
  const threshold = GRADE_THRESHOLDS.find(
    t => score >= t.min && score <= t.max
  )
  return threshold || GRADE_THRESHOLDS[GRADE_THRESHOLDS.length - 1]
}

/**
 * Get the letter grade for a score
 */
export function getScoreGrade(score: number): string {
  return getGradeThreshold(score).letter
}

/**
 * Get the color name for a score
 */
export function getScoreColor(score: number): string {
  return getGradeThreshold(score).color
}

/**
 * Get the text color class for a score
 */
export function getScoreTextColor(score: number): string {
  return getGradeThreshold(score).textColor
}

/**
 * Get the background color class for a score
 */
export function getScoreBgColor(score: number): string {
  return getGradeThreshold(score).bgColor
}

/**
 * Color class mapping for use in components
 */
export const COLOR_CLASS_MAP: Record<string, string> = {
  green: 'text-green-500',
  blue: 'text-blue-500',
  yellow: 'text-yellow-500',
  orange: 'text-orange-400',
  red: 'text-red-600',
  black: 'text-black'
}

/**
 * Calculate distribution of scores across grade ranges
 */
export interface ScoreDistribution {
  gradeRange: string
  letter: string
  count: number
  percentage: number
  color: string
  textColor: string
  bgColor: string
}

export function calculateScoreDistribution(scores: number[]): ScoreDistribution[] {
  if (scores.length === 0) {
    return GRADE_THRESHOLDS.map(threshold => ({
      gradeRange: threshold.label,
      letter: threshold.letter,
      count: 0,
      percentage: 0,
      color: threshold.color,
      textColor: threshold.textColor,
      bgColor: threshold.bgColor
    }))
  }

  const distribution = GRADE_THRESHOLDS.map(threshold => {
    const count = scores.filter(
      score => score >= threshold.min && score <= threshold.max
    ).length
    
    return {
      gradeRange: threshold.label,
      letter: threshold.letter,
      count,
      percentage: (count / scores.length) * 100,
      color: threshold.color,
      textColor: threshold.textColor,
      bgColor: threshold.bgColor
    }
  })

  return distribution
}
