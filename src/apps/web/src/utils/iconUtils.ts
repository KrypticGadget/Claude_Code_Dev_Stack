/**
 * Utility functions for getting appropriate icons for files and languages
 */

// Language-specific icons
const LANGUAGE_ICONS: Record<string, string> = {
  // Web Technologies
  javascript: '📙',
  typescript: '📘',
  jsx: '⚛️',
  tsx: '⚛️',
  html: '🌐',
  css: '🎨',
  scss: '🎨',
  sass: '🎨',
  less: '🎨',
  stylus: '🎨',
  vue: '💚',
  svelte: '🧡',
  angular: '🔴',
  react: '⚛️',

  // Programming Languages
  python: '🐍',
  java: '☕',
  go: '🔷',
  rust: '🦀',
  cpp: '⚙️',
  'c++': '⚙️',
  c: '⚙️',
  csharp: '🔷',
  'c#': '🔷',
  php: '🐘',
  ruby: '💎',
  perl: '🐪',
  kotlin: '🟠',
  swift: '🍎',
  objectivec: '🍎',
  'objective-c': '🍎',
  dart: '🎯',
  scala: '🔴',
  clojure: '🔵',
  haskell: '🔮',
  elixir: '💧',
  erlang: '📞',
  lua: '🌙',
  r: '📊',
  matlab: '📐',

  // Shell and Scripting
  bash: '🐚',
  sh: '🐚',
  zsh: '🐚',
  fish: '🐠',
  powershell: '💙',
  bat: '🦇',
  cmd: '⚫',

  // Data and Config
  json: '📊',
  yaml: '📄',
  yml: '📄',
  xml: '📰',
  toml: '⚙️',
  ini: '⚙️',
  conf: '⚙️',
  config: '⚙️',
  env: '🔐',

  // Database
  sql: '🗄️',
  mysql: '🐬',
  postgresql: '🐘',
  sqlite: '💎',
  mongodb: '🍃',

  // Documentation
  markdown: '📝',
  md: '📝',
  rst: '📝',
  txt: '📄',
  readme: '📖',

  // Version Control
  gitignore: '🚫',
  gitattributes: '📋',
  dockerfile: '🐳',
  docker: '🐳',

  // Package Managers
  packagejson: '📦',
  'package.json': '📦',
  'package-lock.json': '🔒',
  'yarn.lock': '🧶',
  'pom.xml': '📦',
  'requirements.txt': '📦',
  'pipfile': '📦',
  'cargo.toml': '📦',
  'gemfile': '💎',
  'composer.json': '🎼',

  // Build Tools
  webpack: '📦',
  vite: '⚡',
  rollup: '📦',
  gulp: '🥤',
  grunt: '🏗️',
  makefile: '🔨',
  cmake: '🔨',

  // Testing
  test: '🧪',
  spec: '🧪',
  jest: '🃏',
  cypress: '🌲',
  mocha: '☕',

  // Linting and Formatting
  eslint: '📏',
  prettier: '💅',
  lint: '📏',

  // Images
  png: '🖼️',
  jpg: '🖼️',
  jpeg: '🖼️',
  gif: '🎞️',
  svg: '🖼️',
  webp: '🖼️',
  ico: '🖼️',
  bmp: '🖼️',

  // Fonts
  ttf: '🔤',
  otf: '🔤',
  woff: '🔤',
  woff2: '🔤',
  eot: '🔤',

  // Archives
  zip: '📦',
  tar: '📦',
  gz: '📦',
  rar: '📦',
  '7z': '📦',

  // Media
  mp4: '🎬',
  avi: '🎬',
  mov: '🎬',
  wmv: '🎬',
  mp3: '🎵',
  wav: '🎵',
  flac: '🎵',
  ogg: '🎵',

  // Binary
  exe: '⚙️',
  dll: '⚙️',
  so: '⚙️',
  dylib: '⚙️',
  lib: '📚',
  o: '⚙️',
  obj: '⚙️',

  // Default
  plaintext: '📄',
  text: '📄'
}

// File extension to icon mapping
const EXTENSION_ICONS: Record<string, string> = {
  // Extract from language icons for file extensions
  js: LANGUAGE_ICONS.javascript,
  ts: LANGUAGE_ICONS.typescript,
  jsx: LANGUAGE_ICONS.jsx,
  tsx: LANGUAGE_ICONS.tsx,
  py: LANGUAGE_ICONS.python,
  java: LANGUAGE_ICONS.java,
  go: LANGUAGE_ICONS.go,
  rs: LANGUAGE_ICONS.rust,
  php: LANGUAGE_ICONS.php,
  rb: LANGUAGE_ICONS.ruby,
  kt: LANGUAGE_ICONS.kotlin,
  swift: LANGUAGE_ICONS.swift,
  dart: LANGUAGE_ICONS.dart,
  scala: LANGUAGE_ICONS.scala,
  clj: LANGUAGE_ICONS.clojure,
  hs: LANGUAGE_ICONS.haskell,
  ex: LANGUAGE_ICONS.elixir,
  erl: LANGUAGE_ICONS.erlang,
  lua: LANGUAGE_ICONS.lua,
  r: LANGUAGE_ICONS.r,
  m: LANGUAGE_ICONS.matlab,
  sh: LANGUAGE_ICONS.bash,
  bash: LANGUAGE_ICONS.bash,
  zsh: LANGUAGE_ICONS.zsh,
  fish: LANGUAGE_ICONS.fish,
  ps1: LANGUAGE_ICONS.powershell,
  bat: LANGUAGE_ICONS.bat,
  cmd: LANGUAGE_ICONS.cmd,
  json: LANGUAGE_ICONS.json,
  yaml: LANGUAGE_ICONS.yaml,
  yml: LANGUAGE_ICONS.yml,
  xml: LANGUAGE_ICONS.xml,
  toml: LANGUAGE_ICONS.toml,
  ini: LANGUAGE_ICONS.ini,
  conf: LANGUAGE_ICONS.conf,
  config: LANGUAGE_ICONS.config,
  env: LANGUAGE_ICONS.env,
  sql: LANGUAGE_ICONS.sql,
  md: LANGUAGE_ICONS.markdown,
  rst: LANGUAGE_ICONS.rst,
  txt: LANGUAGE_ICONS.txt,
  html: LANGUAGE_ICONS.html,
  css: LANGUAGE_ICONS.css,
  scss: LANGUAGE_ICONS.scss,
  sass: LANGUAGE_ICONS.sass,
  less: LANGUAGE_ICONS.less,
  vue: LANGUAGE_ICONS.vue,
  png: LANGUAGE_ICONS.png,
  jpg: LANGUAGE_ICONS.jpg,
  jpeg: LANGUAGE_ICONS.jpeg,
  gif: LANGUAGE_ICONS.gif,
  svg: LANGUAGE_ICONS.svg,
  webp: LANGUAGE_ICONS.webp,
  ico: LANGUAGE_ICONS.ico,
  bmp: LANGUAGE_ICONS.bmp,
  zip: LANGUAGE_ICONS.zip,
  tar: LANGUAGE_ICONS.tar,
  gz: LANGUAGE_ICONS.gz,
  rar: LANGUAGE_ICONS.rar,
  '7z': LANGUAGE_ICONS['7z'],
  mp4: LANGUAGE_ICONS.mp4,
  avi: LANGUAGE_ICONS.avi,
  mov: LANGUAGE_ICONS.mov,
  mp3: LANGUAGE_ICONS.mp3,
  wav: LANGUAGE_ICONS.wav,
  exe: LANGUAGE_ICONS.exe,
  dll: LANGUAGE_ICONS.dll
}

// Special file name patterns
const SPECIAL_FILES: Record<string, string> = {
  'package.json': LANGUAGE_ICONS['package.json'],
  'package-lock.json': LANGUAGE_ICONS['package-lock.json'],
  'yarn.lock': LANGUAGE_ICONS['yarn.lock'],
  'requirements.txt': LANGUAGE_ICONS['requirements.txt'],
  'dockerfile': LANGUAGE_ICONS.dockerfile,
  'docker-compose.yml': LANGUAGE_ICONS.docker,
  'docker-compose.yaml': LANGUAGE_ICONS.docker,
  '.gitignore': LANGUAGE_ICONS.gitignore,
  '.gitattributes': LANGUAGE_ICONS.gitattributes,
  'makefile': LANGUAGE_ICONS.makefile,
  'cmake': LANGUAGE_ICONS.cmake,
  'readme.md': LANGUAGE_ICONS.readme,
  'readme.txt': LANGUAGE_ICONS.readme,
  'readme': LANGUAGE_ICONS.readme,
  '.eslintrc': LANGUAGE_ICONS.eslint,
  '.eslintrc.js': LANGUAGE_ICONS.eslint,
  '.eslintrc.json': LANGUAGE_ICONS.eslint,
  '.prettierrc': LANGUAGE_ICONS.prettier,
  '.prettierrc.js': LANGUAGE_ICONS.prettier,
  '.prettierrc.json': LANGUAGE_ICONS.prettier,
  'jest.config.js': LANGUAGE_ICONS.jest,
  'cypress.json': LANGUAGE_ICONS.cypress,
  'webpack.config.js': LANGUAGE_ICONS.webpack,
  'vite.config.js': LANGUAGE_ICONS.vite,
  'vite.config.ts': LANGUAGE_ICONS.vite,
  'rollup.config.js': LANGUAGE_ICONS.rollup,
  'gulpfile.js': LANGUAGE_ICONS.gulp,
  'gruntfile.js': LANGUAGE_ICONS.grunt
}

/**
 * Get icon for a programming language
 */
export function getLanguageIcon(language: string): string | null {
  if (!language) return null
  
  const normalizedLang = language.toLowerCase().trim()
  return LANGUAGE_ICONS[normalizedLang] || null
}

/**
 * Get icon for a file based on its path
 */
export function getFileIcon(filePath: string): string | null {
  if (!filePath) return null

  const fileName = filePath.split('/').pop()?.toLowerCase() || ''
  const extension = fileName.split('.').pop() || ''

  // Check special files first
  if (SPECIAL_FILES[fileName]) {
    return SPECIAL_FILES[fileName]
  }

  // Check by extension
  if (EXTENSION_ICONS[extension]) {
    return EXTENSION_ICONS[extension]
  }

  // Check for test files
  if (fileName.includes('test') || fileName.includes('spec')) {
    return LANGUAGE_ICONS.test
  }

  // Check for config files
  if (fileName.includes('config') || fileName.includes('conf')) {
    return LANGUAGE_ICONS.config
  }

  return null
}

/**
 * Get icon with fallback logic
 */
export function getIcon(language?: string, filePath?: string): string {
  // Try language first
  if (language) {
    const langIcon = getLanguageIcon(language)
    if (langIcon) return langIcon
  }

  // Try file path
  if (filePath) {
    const fileIcon = getFileIcon(filePath)
    if (fileIcon) return fileIcon
  }

  // Default fallback
  return '📄'
}

/**
 * Get icon for tab based on file type and content
 */
export function getTabIcon(tab: { language: string; filePath: string; title: string; content?: string }): string {
  // Try different approaches in order of priority
  const icon = getIcon(tab.language, tab.filePath) || 
               getIcon(undefined, tab.title) ||
               getLanguageIcon(tab.language) ||
               '📄'

  return icon
}

/**
 * Check if a file is likely an image
 */
export function isImageFile(filePath: string): boolean {
  const extension = filePath.split('.').pop()?.toLowerCase() || ''
  return ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico', 'bmp'].includes(extension)
}

/**
 * Check if a file is likely a media file
 */
export function isMediaFile(filePath: string): boolean {
  const extension = filePath.split('.').pop()?.toLowerCase() || ''
  return ['mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav', 'flac', 'ogg'].includes(extension)
}

/**
 * Check if a file is likely a binary file
 */
export function isBinaryFile(filePath: string): boolean {
  const extension = filePath.split('.').pop()?.toLowerCase() || ''
  return ['exe', 'dll', 'so', 'dylib', 'lib', 'o', 'obj', 'zip', 'tar', 'gz', 'rar', '7z'].includes(extension)
}

/**
 * Get file category for grouping
 */
export function getFileCategory(language: string, filePath: string): string {
  if (isImageFile(filePath)) return 'Images'
  if (isMediaFile(filePath)) return 'Media'
  if (isBinaryFile(filePath)) return 'Binary'

  const webLangs = ['javascript', 'typescript', 'html', 'css', 'scss', 'vue', 'react', 'angular']
  if (webLangs.includes(language.toLowerCase())) return 'Web'

  const systemLangs = ['c', 'cpp', 'c++', 'rust', 'go', 'assembly']
  if (systemLangs.includes(language.toLowerCase())) return 'System'

  const scriptLangs = ['python', 'ruby', 'perl', 'lua', 'bash', 'sh', 'powershell']
  if (scriptLangs.includes(language.toLowerCase())) return 'Scripting'

  const dataLangs = ['json', 'yaml', 'xml', 'sql', 'csv']
  if (dataLangs.includes(language.toLowerCase())) return 'Data'

  const docLangs = ['markdown', 'txt', 'rst']
  if (docLangs.includes(language.toLowerCase())) return 'Documentation'

  return 'Other'
}

export default {
  getLanguageIcon,
  getFileIcon,
  getIcon,
  getTabIcon,
  isImageFile,
  isMediaFile,
  isBinaryFile,
  getFileCategory
}