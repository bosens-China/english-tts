/**
 * 根据字符串生成一致的十六进制颜色
 * 使用简单的哈希算法确保同一人物始终获得相同颜色
 */
export function stringToColor(str: string): string {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // 转换为32位整数
  }

  // 生成HSL颜色，确保饱和度适中、亮度适中（保证可读性）
  const hue = Math.abs(hash % 360)
  const saturation = 65 + (Math.abs(hash) % 20) // 65-85%
  const lightness = 45 + (Math.abs(hash) % 10) // 45-55%

  return hslToHex(hue, saturation, lightness)
}

/**
 * HSL转十六进制
 */
function hslToHex(h: number, s: number, l: number): string {
  l /= 100
  const a = s * Math.min(l, 1 - l) / 100
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * color).toString(16).padStart(2, '0')
  }
  return `#${f(0)}${f(8)}${f(4)}`
}

/**
 * 根据背景色判断文字应该是白色还是黑色
 */
export function getTextColor(bgColor: string): string {
  const hex = bgColor.replace('#', '')
  const r = Number.parseInt(hex.substring(0, 2), 16)
  const g = Number.parseInt(hex.substring(2, 4), 16)
  const b = Number.parseInt(hex.substring(4, 6), 16)

  // 计算亮度
  const brightness = (r * 299 + g * 587 + b * 114) / 1000

  return brightness > 128 ? '#1f2937' : '#ffffff'
}

/**
 * 获取与背景色对比的文字颜色（确保可读性）
 * 使用更严格的阈值，确保彩色背景上的文字清晰可见
 */
export function getContrastColor(bgColor: string): string {
  const hex = bgColor.replace('#', '')
  const r = Number.parseInt(hex.substring(0, 2), 16)
  const g = Number.parseInt(hex.substring(2, 4), 16)
  const b = Number.parseInt(hex.substring(4, 6), 16)

  // 计算相对亮度
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

  // 对于中等亮度的颜色，使用深色文字以确保可读性
  return luminance > 0.5 ? '#374151' : '#1f2937'
}

/**
 * 生成带透明度的背景色
 */
export function getBgColorWithOpacity(hexColor: string, opacity: number = 0.15): string {
  const hex = hexColor.replace('#', '')
  const r = Number.parseInt(hex.substring(0, 2), 16)
  const g = Number.parseInt(hex.substring(2, 4), 16)
  const b = Number.parseInt(hex.substring(4, 6), 16)

  return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

// 缓存已生成的颜色
const colorCache = new Map<string, { bg: string, text: string }>()

/**
 * 获取人物的颜色配置（带缓存）
 */
export function getSpeakerColorConfig(speaker: string): { bg: string, text: string, border: string } {
  if (!colorCache.has(speaker)) {
    const bg = stringToColor(speaker)
    const text = getTextColor(bg)
    colorCache.set(speaker, { bg, text })
  }

  const cached = colorCache.get(speaker)!
  return {
    bg: cached.bg,
    text: cached.text,
    border: cached.bg,
  }
}
