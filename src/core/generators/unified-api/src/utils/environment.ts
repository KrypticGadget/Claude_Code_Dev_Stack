/**
 * Environment detection and setup utilities
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { platform } from 'os';
import { existsSync } from 'fs';
import { join } from 'path';
import { EnvironmentInfo, GeneratorType } from '../types.js';

const execAsync = promisify(exec);

/**
 * Detects the current environment and recommends optimal generator
 */
export async function detectEnvironment(): Promise<EnvironmentInfo> {
  const info: EnvironmentInfo = {
    platform: platform(),
    packageManagers: [],
    recommendedGenerator: 'auto'
  };

  // Detect Node.js
  try {
    const { stdout } = await execAsync('node --version');
    info.nodeVersion = stdout.trim().replace('v', '');
  } catch {
    // Node.js not available
  }

  // Detect Python
  try {
    const { stdout } = await execAsync('python --version');
    info.pythonVersion = stdout.trim().replace('Python ', '');
  } catch {
    try {
      const { stdout } = await execAsync('python3 --version');
      info.pythonVersion = stdout.trim().replace('Python ', '');
    } catch {
      // Python not available
    }
  }

  // Detect package managers
  const packageManagers = [
    { name: 'npm', command: 'npm --version' },
    { name: 'yarn', command: 'yarn --version' },
    { name: 'pnpm', command: 'pnpm --version' },
    { name: 'pip', command: 'pip --version' },
    { name: 'poetry', command: 'poetry --version' },
    { name: 'pipenv', command: 'pipenv --version' }
  ];

  for (const pm of packageManagers) {
    try {
      const { stdout } = await execAsync(pm.command);
      info.packageManagers.push({
        name: pm.name,
        version: stdout.trim().split(' ').pop() || 'unknown',
        available: true
      });
    } catch {
      info.packageManagers.push({
        name: pm.name,
        available: false
      });
    }
  }

  // Detect Git
  try {
    const { stdout: versionOutput } = await execAsync('git --version');
    const version = versionOutput.trim().split(' ').pop();
    
    info.git = {
      available: true,
      version
    };

    // Check if we're in a git repository
    try {
      const { stdout: repoOutput } = await execAsync('git remote get-url origin');
      info.git.repository = repoOutput.trim();
      
      const { stdout: branchOutput } = await execAsync('git branch --show-current');
      info.git.branch = branchOutput.trim();
    } catch {
      // Not in a git repository or no remote
    }
  } catch {
    info.git = { available: false };
  }

  // Recommend generator based on environment
  info.recommendedGenerator = recommendGenerator(info);

  return info;
}

/**
 * Recommends the best generator based on environment
 */
function recommendGenerator(info: EnvironmentInfo): GeneratorType {
  const hasNode = !!info.nodeVersion;
  const hasPython = !!info.pythonVersion;
  const hasNpm = info.packageManagers.some(pm => pm.name === 'npm' && pm.available);
  const hasPip = info.packageManagers.some(pm => pm.name === 'pip' && pm.available);

  // If both are available, prefer based on versions and ecosystem
  if (hasNode && hasPython) {
    // Check versions
    const nodeVersionNum = parseVersion(info.nodeVersion || '0.0.0');
    const pythonVersionNum = parseVersion(info.pythonVersion || '0.0.0');

    // Prefer Node.js if it's recent and npm is available
    if (nodeVersionNum.major >= 18 && hasNpm) {
      return 'nodejs';
    }

    // Prefer Python if it's 3.11+ and has package manager
    if (pythonVersionNum.major >= 3 && pythonVersionNum.minor >= 11 && hasPip) {
      return 'python';
    }

    // Default to Node.js if both are decent
    return 'nodejs';
  }

  // If only one is available, use that
  if (hasNode && hasNpm) return 'nodejs';
  if (hasPython && hasPip) return 'python';

  // Fallback
  return 'auto';
}

/**
 * Parses a semantic version string
 */
function parseVersion(version: string): { major: number; minor: number; patch: number } {
  const parts = version.split('.').map(p => parseInt(p.replace(/[^\d]/g, ''), 10) || 0);
  return {
    major: parts[0] || 0,
    minor: parts[1] || 0,
    patch: parts[2] || 0
  };
}

/**
 * Checks if required tools are available for a generator
 */
export async function checkGeneratorRequirements(
  generator: GeneratorType,
  info?: EnvironmentInfo
): Promise<{
  available: boolean;
  missing: string[];
  warnings: string[];
}> {
  const environment = info || await detectEnvironment();
  const missing: string[] = [];
  const warnings: string[] = [];

  switch (generator) {
    case 'python': {
      if (!environment.pythonVersion) {
        missing.push('Python (>=3.11 recommended)');
      } else {
        const pythonVersion = parseVersion(environment.pythonVersion);
        if (pythonVersion.major < 3 || (pythonVersion.major === 3 && pythonVersion.minor < 11)) {
          warnings.push(`Python ${environment.pythonVersion} detected. Python 3.11+ is recommended`);
        }
      }

      const hasPip = environment.packageManagers.some(pm => pm.name === 'pip' && pm.available);
      if (!hasPip) {
        missing.push('pip package manager');
      }

      break;
    }

    case 'nodejs': {
      if (!environment.nodeVersion) {
        missing.push('Node.js (>=18.0.0 recommended)');
      } else {
        const nodeVersion = parseVersion(environment.nodeVersion);
        if (nodeVersion.major < 18) {
          warnings.push(`Node.js ${environment.nodeVersion} detected. Node.js 18+ is recommended`);
        }
      }

      const hasNpm = environment.packageManagers.some(pm => pm.name === 'npm' && pm.available);
      if (!hasNpm) {
        missing.push('npm package manager');
      }

      break;
    }

    case 'auto': {
      // Check both and see if at least one is available
      const pythonOk = environment.pythonVersion && 
        environment.packageManagers.some(pm => pm.name === 'pip' && pm.available);
      const nodeOk = environment.nodeVersion && 
        environment.packageManagers.some(pm => pm.name === 'npm' && pm.available);

      if (!pythonOk && !nodeOk) {
        missing.push('Either Python (>=3.11) with pip or Node.js (>=18) with npm');
      }

      break;
    }
  }

  return {
    available: missing.length === 0,
    missing,
    warnings
  };
}

/**
 * Detects project type based on existing files
 */
export function detectProjectType(projectDir: string): {
  existingProject: boolean;
  projectType?: string;
  frameworks: string[];
} {
  const files = [
    'package.json',
    'pyproject.toml',
    'requirements.txt',
    'Pipfile',
    'poetry.lock',
    'yarn.lock',
    'pnpm-lock.yaml'
  ];

  const frameworks: string[] = [];
  let existingProject = false;
  let projectType: string | undefined;

  for (const file of files) {
    const filePath = join(projectDir, file);
    if (existsSync(filePath)) {
      existingProject = true;

      switch (file) {
        case 'package.json':
          frameworks.push('Node.js');
          if (!projectType) projectType = 'nodejs';
          break;
        case 'pyproject.toml':
        case 'requirements.txt':
        case 'Pipfile':
        case 'poetry.lock':
          frameworks.push('Python');
          if (!projectType) projectType = 'python';
          break;
      }
    }
  }

  // Check for framework-specific files
  const frameworkFiles = [
    { file: 'tsconfig.json', framework: 'TypeScript' },
    { file: '.eslintrc.js', framework: 'ESLint' },
    { file: '.eslintrc.json', framework: 'ESLint' },
    { file: 'jest.config.js', framework: 'Jest' },
    { file: 'pytest.ini', framework: 'pytest' },
    { file: 'tox.ini', framework: 'tox' },
    { file: 'setup.py', framework: 'setuptools' }
  ];

  for (const { file, framework } of frameworkFiles) {
    if (existsSync(join(projectDir, file))) {
      frameworks.push(framework);
    }
  }

  return {
    existingProject,
    projectType,
    frameworks: [...new Set(frameworks)] // Remove duplicates
  };
}

/**
 * Validates that the environment meets minimum requirements
 */
export async function validateEnvironmentRequirements(): Promise<{
  valid: boolean;
  errors: string[];
  warnings: string[];
}> {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check for basic tools
  try {
    await execAsync('git --version');
  } catch {
    warnings.push('Git is not available. Version control features will be limited.');
  }

  // Check disk space (simplified check)
  try {
    const { stdout } = await execAsync(platform() === 'win32' ? 'dir' : 'df -h .');
    // Basic check that command runs - actual space checking would be more complex
  } catch {
    warnings.push('Could not check available disk space.');
  }

  // Check write permissions
  try {
    const testFile = join(process.cwd(), '.unified-mcp-test');
    await import('fs/promises').then(fs => fs.writeFile(testFile, 'test'));
    await import('fs/promises').then(fs => fs.unlink(testFile));
  } catch {
    errors.push('No write permission in current directory.');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}