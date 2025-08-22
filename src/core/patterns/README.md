# AI Bailout Detection Patterns

This directory contains AI bailout detection patterns extracted from the AicodeGuard repository. These patterns detect when AI is avoiding implementation, deflecting tasks, or providing low-quality responses.

## Structure

```
core/patterns/
├── PatternDetector.ts          # Core pattern detection logic
├── config/
│   ├── patterns.json           # Main pattern definitions
│   └── conversation-patterns.json  # Conversation-specific patterns
├── analyzers/
│   ├── ConversationAnalyzer.ts # Analyzes conversation patterns
│   ├── InterventionEngine.ts   # Handles automatic interventions
│   └── QualityAnalyzer.ts      # Quality analysis and reporting
├── managers/
│   ├── ConfigManager.ts        # Configuration management
│   └── NotificationManager.ts  # Notification handling
├── types/
│   └── common.ts              # Type definitions
├── index.ts                   # Main exports
└── README.md                  # This file
```

## Pattern Categories

### Terminal Patterns (AI Response Detection)

1. **DIRECT_REFUSAL** (Weight: 20)
   - "I cannot generate code for you"
   - "would be completing your work"
   - "learn programming instead"

2. **EDUCATIONAL_POSITIONING** (Weight: 15)
   - "this will help you learn"
   - "good learning exercise"
   - "I encourage you to"

3. **COMPLEXITY_AVOIDANCE** (Weight: 12)
   - "this is quite complex"
   - "would require significant"
   - "beyond the scope"

4. **ARCHITECTURAL_DEFLECTION** (Weight: 8)
   - "let's start with the basics"
   - "we should think about architecture"
   - "need to plan this carefully"

### Code Patterns (Quality Issues)

1. **SECURITY_ISSUES** (Weight: 25)
   - `eval()` usage
   - `innerHTML` assignments
   - `document.write()` calls

2. **TYPESCRIPT_BAILOUTS** (Weight: 15)
   - `: any` type annotations
   - `as any` casts
   - `@ts-ignore` comments

3. **PRODUCTION_ISSUES** (Weight: 10)
   - `console.log()` statements
   - `debugger` statements
   - TODO/FIXME comments

4. **CODE_QUALITY_ISSUES** (Weight: 12)
   - Placeholder implementations
   - Unimplemented error throws
   - TODO-marked returns

### Conversation Patterns (Implementation Avoidance)

1. **HIGH** severity (Weight: 15)
   - "analyze existing"
   - "create mock"
   - "for now"
   - "placeholder implementation"

2. **MEDIUM** severity (Weight: 10)
   - "add proper error handling"
   - "enhance for production"
   - "write comprehensive tests"

3. **LOW** severity (Weight: 5)
   - "basic implementation"
   - "simple approach"
   - "initial version"

## Usage

```typescript
import { 
  PatternDetector, 
  ConversationAnalyzer, 
  QualityAnalyzer,
  ConfigManager 
} from './core/patterns';

// Detect patterns in text/code
const detector = new PatternDetector();
const result = detector.analyzeText(aiResponse);

// Analyze conversation for bailout patterns
const conversationAnalyzer = new ConversationAnalyzer();
const analysis = conversationAnalyzer.analyzeTodoBailoutPatterns(todoContent);

// Generate quality reports
const qualityAnalyzer = new QualityAnalyzer();
const report = qualityAnalyzer.generateQualityReport(fileAnalysis);
```

## Quality Levels

Based on severity score:
- **EXCELLENT**: 0-4 points
- **GOOD**: 5-14 points  
- **ACCEPTABLE**: 15-29 points
- **POOR**: 30-49 points
- **CRITICAL**: 50+ points

## Aggressiveness Levels

1. **Zero-Tolerance**: Maximum protection, catches all issues
2. **Sophisticated**: Balanced protection with intelligent intervention
3. **Light**: Minimal monitoring, only blatant security issues

## Intervention Behaviors

- **Auto-Intervention**: Automatic terminal corrections
- **Block Saves**: Prevent saving files with critical issues
- **Notifications**: Show quality issue alerts
- **Detailed Reports**: Generate comprehensive analysis reports

## Integration

These patterns can be integrated into:
- VSCode extensions for real-time monitoring
- CI/CD pipelines for quality gates
- Code review processes
- AI interaction monitoring systems
- Quality assurance workflows

The patterns help ensure AI assistants provide complete, production-ready implementations rather than educational deflections or incomplete code.