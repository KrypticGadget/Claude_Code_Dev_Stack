#!/usr/bin/env python3
"""
Automated Code Quality Hooks - Real-time Code Assessment
Provides automated code quality assessment through LSP integration,
real-time analysis triggers, and intelligent quality improvement suggestions.
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import ast
import re
import subprocess
import logging
import statistics
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Code quality metrics"""
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    MAINTAINABILITY = "maintainability"
    TESTABILITY = "testability"
    READABILITY = "readability"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    DOCUMENTATION = "documentation"


class SeverityLevel(Enum):
    """Issue severity levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


class QualityCategory(Enum):
    """Quality issue categories"""
    BUG = "bug"
    VULNERABILITY = "vulnerability"
    CODE_SMELL = "code_smell"
    DUPLICATION = "duplication"
    COMPLEXITY = "complexity"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"


@dataclass
class QualityIssue:
    """Represents a code quality issue"""
    id: str
    category: QualityCategory
    severity: SeverityLevel
    metric: QualityMetric
    title: str
    description: str
    file_path: str
    line_number: int
    column_number: int = 0
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    rule_id: str = ""
    suggestions: List[str] = field(default_factory=list)
    auto_fixable: bool = False
    fix_command: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    file_path: str
    language: str
    issues: List[QualityIssue]
    metrics: Dict[QualityMetric, float]
    overall_score: float
    timestamp: datetime
    analysis_duration: float
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    test_coverage: Optional[float] = None
    technical_debt_minutes: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class QualityAnalyzer(ABC):
    """Abstract base class for quality analyzers"""
    
    @abstractmethod
    def analyze(self, file_path: str, content: str) -> List[QualityIssue]:
        pass
    
    @abstractmethod
    def get_metrics(self, file_path: str, content: str) -> Dict[QualityMetric, float]:
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        pass


class PythonQualityAnalyzer(QualityAnalyzer):
    """Python-specific quality analyzer"""
    
    def __init__(self):
        self.max_complexity = 10
        self.max_line_length = 88
        self.max_function_length = 50
        self.max_class_length = 200
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python"]
    
    def analyze(self, file_path: str, content: str) -> List[QualityIssue]:
        """Analyze Python code for quality issues"""
        issues = []
        
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Check complexity
            issues.extend(self._check_complexity(tree, file_path))
            
            # Check function/class lengths
            issues.extend(self._check_lengths(tree, file_path, content))
            
            # Check naming conventions
            issues.extend(self._check_naming_conventions(tree, file_path))
            
            # Check documentation
            issues.extend(self._check_documentation(tree, file_path))
            
            # Check for code smells
            issues.extend(self._check_code_smells(tree, file_path, content))
            
        except SyntaxError as e:
            issues.append(QualityIssue(
                id=f"syntax_error_{int(time.time())}",
                category=QualityCategory.BUG,
                severity=SeverityLevel.CRITICAL,
                metric=QualityMetric.STYLE,
                title="Syntax Error",
                description=f"Syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno or 1,
                column_number=e.offset or 0,
                auto_fixable=False
            ))
        
        return issues
    
    def get_metrics(self, file_path: str, content: str) -> Dict[QualityMetric, float]:
        """Calculate quality metrics for Python code"""
        metrics = {}
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Calculate complexity
            complexity = self._calculate_complexity(tree)
            metrics[QualityMetric.COMPLEXITY] = min(complexity / self.max_complexity, 1.0)
            
            # Calculate maintainability (inverse of complexity + other factors)
            maintainability = max(0, 1.0 - (complexity / 20))
            metrics[QualityMetric.MAINTAINABILITY] = maintainability
            
            # Calculate readability based on line length, comments, etc.
            readability = self._calculate_readability(content, lines)
            metrics[QualityMetric.READABILITY] = readability
            
            # Calculate documentation score
            doc_score = self._calculate_documentation_score(tree)
            metrics[QualityMetric.DOCUMENTATION] = doc_score
            
            # Basic testability score (presence of testable functions)
            testability = self._calculate_testability(tree)
            metrics[QualityMetric.TESTABILITY] = testability
            
        except SyntaxError:
            # If code doesn't parse, give it low scores
            for metric in QualityMetric:
                metrics[metric] = 0.1
        
        return metrics
    
    def _check_complexity(self, tree: ast.AST, file_path: str) -> List[QualityIssue]:
        """Check cyclomatic complexity"""
        issues = []
        
        class ComplexityVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                complexity = self._calculate_node_complexity(node)
                if complexity > self.parent.max_complexity:
                    issues.append(QualityIssue(
                        id=f"complexity_{node.name}_{node.lineno}",
                        category=QualityCategory.COMPLEXITY,
                        severity=SeverityLevel.HIGH if complexity > 15 else SeverityLevel.MEDIUM,
                        metric=QualityMetric.COMPLEXITY,
                        title="High Cyclomatic Complexity",
                        description=f"Function '{node.name}' has complexity {complexity} (max: {self.parent.max_complexity})",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=[
                            "Consider breaking this function into smaller functions",
                            "Use early returns to reduce nesting",
                            "Extract complex conditions into separate functions"
                        ],
                        metadata={"complexity": complexity}
                    ))
                self.generic_visit(node)
            
            def _calculate_node_complexity(self, node):
                complexity = 1  # Base complexity
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                return complexity
        
        visitor = ComplexityVisitor()
        visitor.parent = self
        visitor.visit(tree)
        return issues
    
    def _check_lengths(self, tree: ast.AST, file_path: str, content: str) -> List[QualityIssue]:
        """Check function and class lengths"""
        issues = []
        lines = content.split('\n')
        
        class LengthVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                length = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
                if length > self.parent.max_function_length:
                    issues.append(QualityIssue(
                        id=f"function_length_{node.name}_{node.lineno}",
                        category=QualityCategory.CODE_SMELL,
                        severity=SeverityLevel.MEDIUM,
                        metric=QualityMetric.MAINTAINABILITY,
                        title="Long Function",
                        description=f"Function '{node.name}' is {length} lines long (max: {self.parent.max_function_length})",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=[
                            "Consider breaking this function into smaller functions",
                            "Extract logical blocks into separate methods"
                        ],
                        metadata={"length": length}
                    ))
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                length = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
                if length > self.parent.max_class_length:
                    issues.append(QualityIssue(
                        id=f"class_length_{node.name}_{node.lineno}",
                        category=QualityCategory.CODE_SMELL,
                        severity=SeverityLevel.MEDIUM,
                        metric=QualityMetric.MAINTAINABILITY,
                        title="Long Class",
                        description=f"Class '{node.name}' is {length} lines long (max: {self.parent.max_class_length})",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=[
                            "Consider splitting this class into multiple classes",
                            "Extract related methods into separate classes",
                            "Use composition instead of inheritance"
                        ],
                        metadata={"length": length}
                    ))
                self.generic_visit(node)
        
        visitor = LengthVisitor()
        visitor.parent = self
        visitor.visit(tree)
        return issues
    
    def _check_naming_conventions(self, tree: ast.AST, file_path: str) -> List[QualityIssue]:
        """Check Python naming conventions"""
        issues = []
        
        class NamingVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check snake_case for functions
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append(QualityIssue(
                        id=f"naming_function_{node.name}_{node.lineno}",
                        category=QualityCategory.STYLE,
                        severity=SeverityLevel.LOW,
                        metric=QualityMetric.STYLE,
                        title="Naming Convention Violation",
                        description=f"Function '{node.name}' should use snake_case",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=["Use snake_case for function names"],
                        auto_fixable=True
                    ))
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check PascalCase for classes
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(QualityIssue(
                        id=f"naming_class_{node.name}_{node.lineno}",
                        category=QualityCategory.STYLE,
                        severity=SeverityLevel.LOW,
                        metric=QualityMetric.STYLE,
                        title="Naming Convention Violation",
                        description=f"Class '{node.name}' should use PascalCase",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=["Use PascalCase for class names"],
                        auto_fixable=True
                    ))
                self.generic_visit(node)
        
        visitor = NamingVisitor()
        visitor.visit(tree)
        return issues
    
    def _check_documentation(self, tree: ast.AST, file_path: str) -> List[QualityIssue]:
        """Check for missing documentation"""
        issues = []
        
        class DocVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Skip private methods and test methods
                if not node.name.startswith('_') and not node.name.startswith('test_'):
                    has_docstring = (ast.get_docstring(node) is not None)
                    if not has_docstring:
                        issues.append(QualityIssue(
                            id=f"missing_docstring_{node.name}_{node.lineno}",
                            category=QualityCategory.DOCUMENTATION,
                            severity=SeverityLevel.LOW,
                            metric=QualityMetric.DOCUMENTATION,
                            title="Missing Docstring",
                            description=f"Function '{node.name}' is missing a docstring",
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestions=[
                                "Add a docstring describing the function's purpose",
                                "Include parameter descriptions",
                                "Document return values"
                            ],
                            auto_fixable=True
                        ))
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                has_docstring = (ast.get_docstring(node) is not None)
                if not has_docstring:
                    issues.append(QualityIssue(
                        id=f"missing_class_docstring_{node.name}_{node.lineno}",
                        category=QualityCategory.DOCUMENTATION,
                        severity=SeverityLevel.LOW,
                        metric=QualityMetric.DOCUMENTATION,
                        title="Missing Class Docstring",
                        description=f"Class '{node.name}' is missing a docstring",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=[
                            "Add a class docstring describing its purpose",
                            "Document key attributes and methods",
                            "Include usage examples"
                        ],
                        auto_fixable=True
                    ))
                self.generic_visit(node)
        
        visitor = DocVisitor()
        visitor.visit(tree)
        return issues
    
    def _check_code_smells(self, tree: ast.AST, file_path: str, content: str) -> List[QualityIssue]:
        """Check for common code smells"""
        issues = []
        
        # Check for long parameter lists
        class ParameterVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                param_count = len(node.args.args)
                if param_count > 5:
                    issues.append(QualityIssue(
                        id=f"long_parameter_list_{node.name}_{node.lineno}",
                        category=QualityCategory.CODE_SMELL,
                        severity=SeverityLevel.MEDIUM,
                        metric=QualityMetric.MAINTAINABILITY,
                        title="Long Parameter List",
                        description=f"Function '{node.name}' has {param_count} parameters (max recommended: 5)",
                        file_path=file_path,
                        line_number=node.lineno,
                        suggestions=[
                            "Consider using a configuration object",
                            "Group related parameters into data classes",
                            "Use keyword-only arguments"
                        ]
                    ))
                self.generic_visit(node)
        
        visitor = ParameterVisitor()
        visitor.visit(tree)
        
        # Check for duplicated code (simple string matching)
        lines = content.split('\n')
        line_groups = defaultdict(list)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('#'):
                line_groups[stripped].append(i + 1)
        
        for line_content, line_numbers in line_groups.items():
            if len(line_numbers) > 1:
                issues.append(QualityIssue(
                    id=f"duplicate_line_{hash(line_content)}",
                    category=QualityCategory.DUPLICATION,
                    severity=SeverityLevel.LOW,
                    metric=QualityMetric.DUPLICATION,
                    title="Duplicate Code",
                    description=f"Identical line found at multiple locations: {line_numbers}",
                    file_path=file_path,
                    line_number=line_numbers[0],
                    suggestions=[
                        "Extract common code into a function",
                        "Use constants for repeated values",
                        "Consider using a loop or function call"
                    ],
                    metadata={"duplicate_lines": line_numbers}
                ))
        
        return issues
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate overall cyclomatic complexity"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def _calculate_readability(self, content: str, lines: List[str]) -> float:
        """Calculate readability score"""
        if not lines:
            return 0.0
        
        # Factors: line length, comment ratio, blank line ratio
        long_lines = sum(1 for line in lines if len(line) > self.max_line_length)
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        blank_lines = sum(1 for line in lines if not line.strip())
        
        line_length_score = max(0, 1.0 - (long_lines / len(lines)))
        comment_ratio = comment_lines / len(lines) if lines else 0
        comment_score = min(comment_ratio * 2, 1.0)  # Cap at 1.0
        blank_ratio = blank_lines / len(lines) if lines else 0
        structure_score = min(blank_ratio * 3, 1.0)  # Some blank lines are good
        
        return (line_length_score + comment_score + structure_score) / 3
    
    def _calculate_documentation_score(self, tree: ast.AST) -> float:
        """Calculate documentation score"""
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1
            elif isinstance(node, ast.ClassDef):
                total_classes += 1
                if ast.get_docstring(node):
                    documented_classes += 1
        
        if total_functions == 0 and total_classes == 0:
            return 1.0
        
        function_score = documented_functions / total_functions if total_functions > 0 else 1.0
        class_score = documented_classes / total_classes if total_classes > 0 else 1.0
        
        return (function_score + class_score) / 2
    
    def _calculate_testability(self, tree: ast.AST) -> float:
        """Calculate testability score"""
        # Simple heuristic: functions with fewer dependencies are more testable
        total_functions = 0
        testable_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                total_functions += 1
                # Consider function testable if it has parameters and/or return statements
                has_params = len(node.args.args) > 0
                has_returns = any(isinstance(child, ast.Return) for child in ast.walk(node))
                if has_params or has_returns:
                    testable_functions += 1
        
        return testable_functions / total_functions if total_functions > 0 else 1.0


class TypeScriptQualityAnalyzer(QualityAnalyzer):
    """TypeScript/JavaScript quality analyzer"""
    
    @property
    def supported_languages(self) -> List[str]:
        return ["typescript", "javascript"]
    
    def analyze(self, file_path: str, content: str) -> List[QualityIssue]:
        """Analyze TypeScript/JavaScript code"""
        issues = []
        
        # Basic checks for TypeScript/JavaScript
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for console.log statements
            if 'console.log' in line and not line.strip().startswith('//'):
                issues.append(QualityIssue(
                    id=f"console_log_{i}",
                    category=QualityCategory.CODE_SMELL,
                    severity=SeverityLevel.LOW,
                    metric=QualityMetric.STYLE,
                    title="Console Statement",
                    description="console.log statement found (should be removed in production)",
                    file_path=file_path,
                    line_number=i,
                    suggestions=["Remove console.log statements", "Use proper logging framework"],
                    auto_fixable=True,
                    fix_command=f"Remove line {i}"
                ))
            
            # Check for var usage (prefer let/const)
            if re.search(r'\bvar\b', line) and not line.strip().startswith('//'):
                issues.append(QualityIssue(
                    id=f"var_usage_{i}",
                    category=QualityCategory.CODE_SMELL,
                    severity=SeverityLevel.LOW,
                    metric=QualityMetric.STYLE,
                    title="Use of 'var'",
                    description="Use 'let' or 'const' instead of 'var'",
                    file_path=file_path,
                    line_number=i,
                    suggestions=["Replace 'var' with 'let' or 'const'"],
                    auto_fixable=True
                ))
        
        return issues
    
    def get_metrics(self, file_path: str, content: str) -> Dict[QualityMetric, float]:
        """Calculate TypeScript/JavaScript metrics"""
        lines = content.split('\n')
        
        # Basic metrics
        console_statements = sum(1 for line in lines if 'console.log' in line)
        var_statements = sum(1 for line in lines if re.search(r'\bvar\b', line))
        
        # Calculate scores (inverse of issues)
        total_lines = len(lines)
        style_score = max(0, 1.0 - ((console_statements + var_statements) / max(total_lines, 1)))
        
        return {
            QualityMetric.STYLE: style_score,
            QualityMetric.MAINTAINABILITY: style_score,
            QualityMetric.READABILITY: style_score,
            QualityMetric.COMPLEXITY: 0.8,  # Default assumption
            QualityMetric.DOCUMENTATION: 0.5,  # Default assumption
            QualityMetric.TESTABILITY: 0.7,  # Default assumption
        }


class AutomatedQualityAssessor:
    """Main quality assessment system"""
    
    def __init__(self):
        self.analyzers: Dict[str, QualityAnalyzer] = {
            "python": PythonQualityAnalyzer(),
            "typescript": TypeScriptQualityAnalyzer(),
            "javascript": TypeScriptQualityAnalyzer(),
        }
        
        # Quality thresholds
        self.thresholds = {
            QualityMetric.COMPLEXITY: 0.7,
            QualityMetric.MAINTAINABILITY: 0.6,
            QualityMetric.READABILITY: 0.7,
            QualityMetric.DOCUMENTATION: 0.5,
            QualityMetric.TESTABILITY: 0.6
        }
        
        # History tracking
        self.assessment_history: deque = deque(maxlen=1000)
        self.file_history: Dict[str, List[QualityReport]] = defaultdict(list)
        
        # Real-time monitoring
        self.monitoring_enabled = True
        self.quality_trends: Dict[str, List[float]] = defaultdict(list)
    
    def assess_file(self, file_path: str, content: Optional[str] = None) -> QualityReport:
        """Perform comprehensive quality assessment"""
        start_time = time.time()
        
        if content is None:
            try:
                content = Path(file_path).read_text(encoding='utf-8')
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                return self._create_error_report(file_path, str(e))
        
        # Determine language
        language = self._detect_language(file_path)
        
        # Get appropriate analyzer
        analyzer = self.analyzers.get(language)
        if not analyzer:
            return self._create_unsupported_report(file_path, language)
        
        # Perform analysis
        issues = analyzer.analyze(file_path, content)
        metrics = analyzer.get_metrics(file_path, content)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics, issues)
        
        # Calculate additional metrics
        lines_of_code = len([line for line in content.split('\n') if line.strip()])
        cyclomatic_complexity = metrics.get(QualityMetric.COMPLEXITY, 0) * 20  # Rough estimate
        maintainability_index = metrics.get(QualityMetric.MAINTAINABILITY, 0) * 100
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics)
        
        # Calculate technical debt
        technical_debt = self._calculate_technical_debt(issues)
        
        # Create report
        report = QualityReport(
            file_path=file_path,
            language=language,
            issues=issues,
            metrics=metrics,
            overall_score=overall_score,
            timestamp=datetime.now(),
            analysis_duration=time.time() - start_time,
            lines_of_code=lines_of_code,
            cyclomatic_complexity=int(cyclomatic_complexity),
            maintainability_index=maintainability_index,
            technical_debt_minutes=technical_debt,
            recommendations=recommendations
        )
        
        # Store in history
        self.assessment_history.append(report)
        self.file_history[file_path].append(report)
        
        # Update trends
        if self.monitoring_enabled:
            self.quality_trends[file_path].append(overall_score)
            if len(self.quality_trends[file_path]) > 50:  # Keep last 50 assessments
                self.quality_trends[file_path].pop(0)
        
        return report
    
    def assess_directory(self, directory_path: str, 
                        file_patterns: List[str] = None) -> Dict[str, QualityReport]:
        """Assess all files in a directory"""
        if file_patterns is None:
            file_patterns = ["*.py", "*.ts", "*.js"]
        
        reports = {}
        directory = Path(directory_path)
        
        for pattern in file_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    try:
                        report = self.assess_file(str(file_path))
                        reports[str(file_path)] = report
                    except Exception as e:
                        logger.error(f"Failed to assess {file_path}: {e}")
        
        return reports
    
    def get_quality_trend(self, file_path: str) -> Dict[str, Any]:
        """Get quality trend for a file"""
        if file_path not in self.quality_trends:
            return {"trend": "no_data", "scores": []}
        
        scores = self.quality_trends[file_path]
        if len(scores) < 2:
            return {"trend": "insufficient_data", "scores": scores}
        
        # Calculate trend
        if len(scores) >= 5:
            recent_avg = statistics.mean(scores[-5:])
            older_avg = statistics.mean(scores[:-5]) if len(scores) > 5 else scores[0]
            
            if recent_avg > older_avg + 0.1:
                trend = "improving"
            elif recent_avg < older_avg - 0.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            if scores[-1] > scores[0]:
                trend = "improving"
            elif scores[-1] < scores[0]:
                trend = "degrading"
            else:
                trend = "stable"
        
        return {
            "trend": trend,
            "scores": scores,
            "current_score": scores[-1],
            "average_score": statistics.mean(scores),
            "score_range": (min(scores), max(scores))
        }
    
    def get_project_overview(self, project_path: str) -> Dict[str, Any]:
        """Get project-wide quality overview"""
        reports = self.assess_directory(project_path)
        
        if not reports:
            return {"error": "No files analyzed"}
        
        # Aggregate statistics
        total_issues = sum(len(report.issues) for report in reports.values())
        total_lines = sum(report.lines_of_code for report in reports.values())
        average_score = statistics.mean(report.overall_score for report in reports.values())
        
        # Issue breakdown
        issue_breakdown = defaultdict(int)
        severity_breakdown = defaultdict(int)
        
        for report in reports.values():
            for issue in report.issues:
                issue_breakdown[issue.category.value] += 1
                severity_breakdown[issue.severity.value] += 1
        
        # Technical debt
        total_debt = sum(report.technical_debt_minutes for report in reports.values())
        
        # Quality distribution
        score_ranges = {
            "excellent": sum(1 for r in reports.values() if r.overall_score >= 0.9),
            "good": sum(1 for r in reports.values() if 0.7 <= r.overall_score < 0.9),
            "fair": sum(1 for r in reports.values() if 0.5 <= r.overall_score < 0.7),
            "poor": sum(1 for r in reports.values() if r.overall_score < 0.5)
        }
        
        return {
            "project_path": project_path,
            "files_analyzed": len(reports),
            "total_lines_of_code": total_lines,
            "average_quality_score": average_score,
            "total_issues": total_issues,
            "total_technical_debt_hours": total_debt / 60,
            "issue_breakdown": dict(issue_breakdown),
            "severity_breakdown": dict(severity_breakdown),
            "quality_distribution": score_ranges,
            "recommendations": self._generate_project_recommendations(reports)
        }
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _calculate_overall_score(self, metrics: Dict[QualityMetric, float], 
                                issues: List[QualityIssue]) -> float:
        """Calculate overall quality score"""
        # Start with metric-based score
        metric_weights = {
            QualityMetric.COMPLEXITY: 0.2,
            QualityMetric.MAINTAINABILITY: 0.25,
            QualityMetric.READABILITY: 0.2,
            QualityMetric.DOCUMENTATION: 0.15,
            QualityMetric.TESTABILITY: 0.2
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric, weight in metric_weights.items():
            if metric in metrics:
                weighted_score += metrics[metric] * weight
                total_weight += weight
        
        base_score = weighted_score / total_weight if total_weight > 0 else 0.5
        
        # Apply penalties for issues
        critical_issues = sum(1 for issue in issues if issue.severity == SeverityLevel.CRITICAL)
        high_issues = sum(1 for issue in issues if issue.severity == SeverityLevel.HIGH)
        medium_issues = sum(1 for issue in issues if issue.severity == SeverityLevel.MEDIUM)
        
        penalty = (critical_issues * 0.1) + (high_issues * 0.05) + (medium_issues * 0.02)
        
        return max(0.0, min(1.0, base_score - penalty))
    
    def _generate_recommendations(self, issues: List[QualityIssue], 
                                 metrics: Dict[QualityMetric, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Metric-based recommendations
        for metric, score in metrics.items():
            threshold = self.thresholds.get(metric, 0.6)
            if score < threshold:
                if metric == QualityMetric.COMPLEXITY:
                    recommendations.append("Consider refactoring complex functions into smaller, simpler ones")
                elif metric == QualityMetric.MAINTAINABILITY:
                    recommendations.append("Improve code maintainability by reducing complexity and improving structure")
                elif metric == QualityMetric.READABILITY:
                    recommendations.append("Improve code readability with better formatting and comments")
                elif metric == QualityMetric.DOCUMENTATION:
                    recommendations.append("Add docstrings and comments to improve code documentation")
                elif metric == QualityMetric.TESTABILITY:
                    recommendations.append("Improve testability by reducing dependencies and adding return values")
        
        # Issue-based recommendations
        issue_counts = defaultdict(int)
        for issue in issues:
            issue_counts[issue.category] += 1
        
        if issue_counts[QualityCategory.COMPLEXITY] > 2:
            recommendations.append("Address high complexity issues to improve maintainability")
        
        if issue_counts[QualityCategory.DUPLICATION] > 3:
            recommendations.append("Eliminate code duplication by extracting common functionality")
        
        if issue_counts[QualityCategory.STYLE] > 5:
            recommendations.append("Run a code formatter to fix style issues automatically")
        
        return recommendations
    
    def _generate_project_recommendations(self, reports: Dict[str, QualityReport]) -> List[str]:
        """Generate project-wide recommendations"""
        recommendations = []
        
        total_files = len(reports)
        poor_quality_files = sum(1 for r in reports.values() if r.overall_score < 0.5)
        
        if poor_quality_files > total_files * 0.2:
            recommendations.append("Consider a comprehensive code quality review - over 20% of files have poor quality scores")
        
        total_debt = sum(r.technical_debt_minutes for r in reports.values())
        if total_debt > 480:  # 8 hours
            recommendations.append(f"High technical debt detected ({total_debt/60:.1f} hours) - prioritize refactoring")
        
        # Check for patterns across files
        common_issues = defaultdict(int)
        for report in reports.values():
            for issue in report.issues:
                common_issues[issue.rule_id or issue.title] += 1
        
        most_common = max(common_issues.items(), key=lambda x: x[1]) if common_issues else None
        if most_common and most_common[1] > total_files * 0.3:
            recommendations.append(f"Address common issue across project: {most_common[0]}")
        
        return recommendations
    
    def _calculate_technical_debt(self, issues: List[QualityIssue]) -> float:
        """Calculate technical debt in minutes"""
        debt_weights = {
            SeverityLevel.CRITICAL: 60,  # 1 hour per critical issue
            SeverityLevel.HIGH: 30,      # 30 minutes per high issue
            SeverityLevel.MEDIUM: 15,    # 15 minutes per medium issue
            SeverityLevel.LOW: 5,        # 5 minutes per low issue
            SeverityLevel.INFO: 2        # 2 minutes per info issue
        }
        
        total_debt = 0.0
        for issue in issues:
            total_debt += debt_weights.get(issue.severity, 5)
        
        return total_debt
    
    def _create_error_report(self, file_path: str, error: str) -> QualityReport:
        """Create report for files that couldn't be analyzed"""
        return QualityReport(
            file_path=file_path,
            language="unknown",
            issues=[QualityIssue(
                id="analysis_error",
                category=QualityCategory.BUG,
                severity=SeverityLevel.CRITICAL,
                metric=QualityMetric.STYLE,
                title="Analysis Error",
                description=f"Failed to analyze file: {error}",
                file_path=file_path,
                line_number=1
            )],
            metrics={},
            overall_score=0.0,
            timestamp=datetime.now(),
            analysis_duration=0.0,
            lines_of_code=0,
            cyclomatic_complexity=0,
            maintainability_index=0.0,
            technical_debt_minutes=60.0
        )
    
    def _create_unsupported_report(self, file_path: str, language: str) -> QualityReport:
        """Create report for unsupported languages"""
        return QualityReport(
            file_path=file_path,
            language=language,
            issues=[],
            metrics={},
            overall_score=0.5,  # Neutral score for unsupported
            timestamp=datetime.now(),
            analysis_duration=0.0,
            lines_of_code=0,
            cyclomatic_complexity=0,
            maintainability_index=50.0,
            technical_debt_minutes=0.0,
            recommendations=[f"Add support for {language} language analysis"]
        )


# Export main classes
__all__ = [
    'AutomatedQualityAssessor',
    'QualityReport',
    'QualityIssue',
    'QualityMetric',
    'SeverityLevel',
    'QualityCategory',
    'PythonQualityAnalyzer',
    'TypeScriptQualityAnalyzer'
]