"""Intelligent file analysis for inferring purpose - multi-language support."""

from pathlib import Path
from typing import Optional, List, Dict, Set

# ============================================================================
# PYTHON
# ============================================================================
PYTHON_IMPORTS = {
    'fastapi': 'FastAPI web application',
    'flask': 'Flask web application',
    'django': 'Django web application',
    'sqlalchemy': 'Database ORM layer',
    'pydantic': 'Data validation models',
    'chromadb': 'ChromaDB vector storage',
    'openai': 'OpenAI API integration',
    'anthropic': 'Anthropic API integration',
    'langchain': 'LangChain integration',
    'llamaindex': 'LlamaIndex integration',
    'pytest': 'Test suite',
    'unittest': 'Unit tests',
    'requests': 'HTTP client',
    'httpx': 'Async HTTP client',
    'aiohttp': 'Async HTTP operations',
    'celery': 'Background task queue',
    'redis': 'Redis integration',
    'pandas': 'Data processing',
    'numpy': 'Numerical computations',
    'torch': 'PyTorch model',
    'tensorflow': 'TensorFlow model',
    'streamlit': 'Streamlit app',
    'gradio': 'Gradio interface',
}

# ============================================================================
# JAVASCRIPT / TYPESCRIPT
# ============================================================================
JS_IMPORTS = {
    'express': 'Express server',
    'react': 'React component',
    'vue': 'Vue component',
    'angular': 'Angular component',
    'next': 'Next.js component',
    'axios': 'HTTP client',
    'mongoose': 'MongoDB ORM',
    'sequelize': 'SQL ORM',
    'jest': 'Jest tests',
    'mocha': 'Mocha tests',
    'chai': 'Chai assertions',
    'socket.io': 'WebSocket handler',
    'graphql': 'GraphQL schema',
    'prisma': 'Prisma ORM',
    'typeorm': 'TypeORM models',
    'nestjs': 'NestJS module',
    '@nestjs': 'NestJS module',
}

# ============================================================================
# GO
# ============================================================================
GO_IMPORTS = {
    'gin': 'Gin web server',
    'fiber': 'Fiber web server',
    'echo': 'Echo web server',
    'gorm': 'GORM database layer',
    'sqlx': 'SQL extensions',
    'grpc': 'gRPC service',
    'testify': 'Test suite',
    'cobra': 'CLI command',
    'viper': 'Configuration management',
    'zap': 'Logging',
    'logrus': 'Logging',
}

# ============================================================================
# RUST
# ============================================================================
RUST_CRATES = {
    'actix_web': 'Actix web server',
    'axum': 'Axum web framework',
    'rocket': 'Rocket web framework',
    'tokio': 'Async runtime',
    'serde': 'Serialization',
    'diesel': 'Diesel ORM',
    'sqlx': 'SQL toolkit',
    'reqwest': 'HTTP client',
    'clap': 'CLI argument parser',
    'tracing': 'Tracing/logging',
}

# ============================================================================
# JAVA
# ============================================================================
JAVA_IMPORTS = {
    'springframework': 'Spring framework',
    'spring.boot': 'Spring Boot application',
    'javax.persistence': 'JPA entity',
    'jakarta.persistence': 'JPA entity',
    'hibernate': 'Hibernate ORM',
    'junit': 'JUnit tests',
    'mockito': 'Mockito mocks',
    'jackson': 'JSON processing',
    'lombok': 'Lombok utilities',
    'servlet': 'Servlet handler',
}

# ============================================================================
# RUBY
# ============================================================================
RUBY_REQUIRES = {
    'rails': 'Rails application',
    'sinatra': 'Sinatra application',
    'active_record': 'ActiveRecord model',
    'rspec': 'RSpec tests',
    'minitest': 'Minitest suite',
    'sidekiq': 'Background jobs',
    'devise': 'Authentication',
}

# ============================================================================
# PHP
# ============================================================================
PHP_USES = {
    'Laravel': 'Laravel component',
    'Symfony': 'Symfony component',
    'Illuminate': 'Laravel component',
    'Doctrine': 'Doctrine ORM',
    'PHPUnit': 'PHPUnit tests',
    'Guzzle': 'HTTP client',
    'Eloquent': 'Eloquent model',
}

# ============================================================================
# C/C++
# ============================================================================
CPP_INCLUDES = {
    'iostream': 'I/O operations',
    'vector': 'Vector container',
    'string': 'String utilities',
    'thread': 'Threading',
    'boost': 'Boost library',
    'gtest': 'Google Test suite',
    'opencv': 'OpenCV vision',
    'eigen': 'Eigen linear algebra',
}

# ============================================================================
# UNIVERSAL FOLDER HINTS
# ============================================================================
FOLDER_HINTS = {
    # Backend/API
    'api': 'API endpoint',
    'apis': 'API endpoint',
    'routes': 'Route handler',
    'endpoints': 'API endpoint',
    'controllers': 'Controller',
    'handlers': 'Request handler',
    'middleware': 'Middleware',
    
    # Services & Logic
    'services': 'Service layer',
    'service': 'Service layer',
    'business': 'Business logic',
    'logic': 'Business logic',
    'core': 'Core functionality',
    'domain': 'Domain logic',
    
    # Data Layer
    'models': 'Data model',
    'model': 'Data model',
    'entities': 'Entity definition',
    'schemas': 'Schema definition',
    'schema': 'Schema definition',
    'repositories': 'Repository pattern',
    'dao': 'Data access object',
    'db': 'Database layer',
    'database': 'Database layer',
    'migrations': 'Database migration',
    
    # AI/ML
    'agents': 'Agent module',
    'agent': 'Agent module',
    'vector_store': 'Memory module',
    'vectorstore': 'Memory module',
    'memory': 'Memory module',
    'embeddings': 'Embedding layer',
    'llm': 'LLM integration',
    'ml': 'Machine learning',
    'models': 'ML model',
    
    # Frontend
    'components': 'UI component',
    'views': 'View layer',
    'pages': 'Page component',
    'layouts': 'Layout component',
    'hooks': 'React hooks',
    'store': 'State management',
    'redux': 'Redux store',
    'actions': 'Redux actions',
    'reducers': 'Redux reducers',
    
    # Utilities
    'utils': 'Utility functions',
    'helpers': 'Helper functions',
    'lib': 'Library code',
    'common': 'Common utilities',
    'shared': 'Shared code',
    'tools': 'Tool implementation',
    
    # Configuration
    'config': 'Configuration',
    'configs': 'Configuration',
    'settings': 'Settings',
    'env': 'Environment config',
    
    # Testing
    'tests': 'Test module',
    'test': 'Test module',
    '__tests__': 'Test module',
    'spec': 'Test spec',
    'specs': 'Test specs',
    
    # Tasks & Jobs
    'tasks': 'Task handler',
    'jobs': 'Job handler',
    'workers': 'Worker process',
    'queues': 'Queue handler',
    
    # Scripts & Tools
    'scripts': 'Script',
    'bin': 'Executable script',
    'cmd': 'Command',
    'cli': 'CLI interface',
    
    # Documentation
    'docs': 'Documentation',
    'examples': 'Example code',
    
    # Build & Deploy
    'build': 'Build artifacts',
    'dist': 'Distribution',
    'deploy': 'Deployment scripts',
    'ci': 'CI/CD pipeline',
}

# ============================================================================
# SPECIAL FILENAMES (Language-agnostic)
# ============================================================================
SPECIAL_FILES = {
    # Python
    'main.py': 'Application entry point',
    'app.py': 'Application entry point',
    '__init__.py': 'Package initializer',
    '__main__.py': 'Module entry point',
    'setup.py': 'Package setup script',
    'config.py': 'Configuration settings',
    'settings.py': 'Application settings',
    'constants.py': 'Constants definition',
    'exceptions.py': 'Custom exceptions',
    'errors.py': 'Error handlers',
    'middleware.py': 'Middleware layer',
    'decorators.py': 'Decorator utilities',
    'dependencies.py': 'Dependency injection',
    'base.py': 'Base classes',
    'types.py': 'Type definitions',
    
    # JavaScript/TypeScript
    'index.js': 'Entry point',
    'index.ts': 'Entry point',
    'index.tsx': 'React entry point',
    'main.js': 'Main entry point',
    'main.ts': 'Main entry point',
    'app.js': 'Application root',
    'app.ts': 'Application root',
    'server.js': 'Server entry point',
    'server.ts': 'Server entry point',
    'config.js': 'Configuration',
    'config.ts': 'Configuration',
    'routes.js': 'Route definitions',
    'routes.ts': 'Route definitions',
    
    # Go
    'main.go': 'Main entry point',
    'server.go': 'Server implementation',
    'handler.go': 'HTTP handler',
    'router.go': 'Router setup',
    'config.go': 'Configuration',
    'types.go': 'Type definitions',
    
    # Rust
    'main.rs': 'Main entry point',
    'lib.rs': 'Library root',
    'mod.rs': 'Module definition',
    
    # Java
    'Main.java': 'Main entry point',
    'Application.java': 'Application root',
    'Controller.java': 'Controller',
    'Service.java': 'Service layer',
    'Repository.java': 'Repository',
    'Entity.java': 'JPA entity',
    'Config.java': 'Configuration',
    
    # C/C++
    'main.c': 'Main entry point',
    'main.cpp': 'Main entry point',
    'main.cc': 'Main entry point',
    
    # Ruby
    'application.rb': 'Application root',
    'config.rb': 'Configuration',
    
    # PHP
    'index.php': 'Entry point',
    'bootstrap.php': 'Bootstrap file',
    
    # Config files
    'Dockerfile': 'Docker container definition',
    'docker-compose.yml': 'Docker Compose configuration',
    'Makefile': 'Build automation',
    'CMakeLists.txt': 'CMake build configuration',
    'package.json': 'NPM package manifest',
    'Cargo.toml': 'Rust package manifest',
    'go.mod': 'Go module definition',
    'pom.xml': 'Maven project configuration',
    'build.gradle': 'Gradle build script',
    'requirements.txt': 'Python dependencies',
    'Pipfile': 'Python dependencies',
    'pyproject.toml': 'Python project configuration',
    'composer.json': 'PHP dependencies',
    'Gemfile': 'Ruby dependencies',
    '.env': 'Environment variables',
    '.env.example': 'Environment template',
    'README.md': 'Project documentation',
    'LICENSE': 'License file',
    '.gitignore': 'Git ignore rules',
}


def read_file_head(file_path: Path, max_lines: int = 20) -> List[str]:
    """Read first N lines of a file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
            return lines
    except (UnicodeDecodeError, PermissionError, OSError):
        return []


def extract_python_docstring(lines: List[str]) -> Optional[str]:
    """Extract the first line of a Python docstring."""
    in_docstring = False
    docstring_lines = []
    quote_type = None
    
    for line in lines:
        stripped = line.strip()
        
        if not in_docstring and (not stripped or stripped.startswith('#')):
            continue
        
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote_type = stripped[:3]
                in_docstring = True
                content = stripped[3:]
                if quote_type in content:
                    docstring_lines.append(content.split(quote_type)[0].strip())
                    break
                docstring_lines.append(content.strip())
            else:
                break
        else:
            if quote_type in stripped:
                docstring_lines.append(stripped.split(quote_type)[0].strip())
                break
            docstring_lines.append(stripped)
    
    if docstring_lines:
        for line in docstring_lines:
            if line:
                return line
    return None


def extract_js_comment(lines: List[str]) -> Optional[str]:
    """Extract JSDoc or leading comment from JS/TS file."""
    for line in lines:
        stripped = line.strip()
        # JSDoc comment
        if stripped.startswith('/**'):
            content = stripped[3:].strip()
            if content and not content.startswith('*'):
                return content.rstrip('*/')
        # Single-line comment
        elif stripped.startswith('//'):
            content = stripped[2:].strip()
            if content and len(content) > 10:
                return content
    return None


def extract_go_comment(lines: List[str]) -> Optional[str]:
    """Extract package comment from Go file."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('//'):
            content = stripped[2:].strip()
            if content and len(content) > 10:
                return content
        elif stripped.startswith('package '):
            break
    return None


def extract_rust_comment(lines: List[str]) -> Optional[str]:
    """Extract doc comment from Rust file."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('///'):
            content = stripped[3:].strip()
            if content:
                return content
        elif stripped.startswith('//!'):
            content = stripped[3:].strip()
            if content:
                return content
    return None


def detect_python_imports(lines: List[str]) -> List[str]:
    """Detect Python imports."""
    imports = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            if stripped.startswith('import '):
                pkg = stripped[7:].split()[0].split('.')[0]
            else:
                pkg = stripped.split()[1].split('.')[0]
            imports.append(pkg)
    return imports


def detect_js_imports(lines: List[str]) -> List[str]:
    """Detect JavaScript/TypeScript imports."""
    imports = []
    for line in lines:
        stripped = line.strip()
        # import X from 'pkg'
        if 'import' in stripped and 'from' in stripped:
            parts = stripped.split('from')
            if len(parts) >= 2:
                pkg = parts[-1].strip().strip("';\"")
                pkg = pkg.split('/')[0].replace('@', '')
                imports.append(pkg)
        # const X = require('pkg')
        elif 'require(' in stripped:
            start = stripped.find('require(') + 8
            end = stripped.find(')', start)
            if end > start:
                pkg = stripped[start:end].strip("';\"")
                pkg = pkg.split('/')[0].replace('@', '')
                imports.append(pkg)
    return imports


def detect_go_imports(lines: List[str]) -> List[str]:
    """Detect Go imports."""
    imports = []
    in_import_block = False
    
    for line in lines:
        stripped = line.strip().strip('"')
        
        if stripped.startswith('import ('):
            in_import_block = True
            continue
        elif in_import_block:
            if stripped == ')':
                break
            if stripped and not stripped.startswith('//'):
                pkg = stripped.split('/')[-1]
                imports.append(pkg)
        elif stripped.startswith('import "'):
            pkg = stripped[8:].strip('"').split('/')[-1]
            imports.append(pkg)
    
    return imports


def detect_rust_uses(lines: List[str]) -> List[str]:
    """Detect Rust use statements."""
    uses = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('use '):
            parts = stripped[4:].split('::')
            if parts:
                crate = parts[0].strip()
                uses.append(crate)
    return uses


def detect_java_imports(lines: List[str]) -> List[str]:
    """Detect Java imports."""
    imports = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import '):
            pkg = stripped[7:].strip(';').split('.')[0]
            imports.append(pkg)
    return imports


def get_folder_context(file_path: Path) -> Optional[str]:
    """Get contextual hint from parent folder names."""
    parts = file_path.parts
    for part in reversed(parts[:-1]):
        part_lower = part.lower()
        if part_lower in FOLDER_HINTS:
            return FOLDER_HINTS[part_lower]
    return None


def analyze_python_file(file_path: Path, lines: List[str]) -> str:
    """Analyze Python file."""
    # Try docstring first
    docstring = extract_python_docstring(lines)
    if docstring:
        if len(docstring) > 60:
            docstring = docstring[:57] + '...'
        return docstring
    
    # Check imports
    imports = detect_python_imports(lines)
    for imp in imports:
        if imp in PYTHON_IMPORTS:
            return PYTHON_IMPORTS[imp]
    
    # Folder context
    folder_hint = get_folder_context(file_path)
    if folder_hint:
        return folder_hint
    
    return 'Python module'


def analyze_js_file(file_path: Path, lines: List[str]) -> str:
    """Analyze JavaScript/TypeScript file."""
    # Try comment first
    comment = extract_js_comment(lines)
    if comment:
        if len(comment) > 60:
            comment = comment[:57] + '...'
        return comment
    
    # Check imports
    imports = detect_js_imports(lines)
    for imp in imports:
        if imp in JS_IMPORTS:
            return JS_IMPORTS[imp]
    
    # Folder context
    folder_hint = get_folder_context(file_path)
    if folder_hint:
        return folder_hint
    
    ext = file_path.suffix
    if ext in ['.tsx', '.jsx']:
        return 'React component'
    elif ext == '.ts':
        return 'TypeScript module'
    else:
        return 'JavaScript module'


def analyze_go_file(file_path: Path, lines: List[str]) -> str:
    """Analyze Go file."""
    # Try comment first
    comment = extract_go_comment(lines)
    if comment:
        if len(comment) > 60:
            comment = comment[:57] + '...'
        return comment
    
    # Check imports
    imports = detect_go_imports(lines)
    for imp in imports:
        if imp in GO_IMPORTS:
            return GO_IMPORTS[imp]
    
    # Folder context
    folder_hint = get_folder_context(file_path)
    if folder_hint:
        return folder_hint
    
    return 'Go module'


def analyze_rust_file(file_path: Path, lines: List[str]) -> str:
    """Analyze Rust file."""
    # Try comment first
    comment = extract_rust_comment(lines)
    if comment:
        if len(comment) > 60:
            comment = comment[:57] + '...'
        return comment
    
    # Check uses
    uses = detect_rust_uses(lines)
    for use in uses:
        if use in RUST_CRATES:
            return RUST_CRATES[use]
    
    # Folder context
    folder_hint = get_folder_context(file_path)
    if folder_hint:
        return folder_hint
    
    return 'Rust module'


def analyze_java_file(file_path: Path, lines: List[str]) -> str:
    """Analyze Java file."""
    # Check imports
    imports = detect_java_imports(lines)
    for imp in imports:
        if imp in JAVA_IMPORTS:
            return JAVA_IMPORTS[imp]
    
    # Folder context
    folder_hint = get_folder_context(file_path)
    if folder_hint:
        return folder_hint
    
    # Check class type from filename
    name = file_path.stem
    if name.endswith('Controller'):
        return 'Controller'
    elif name.endswith('Service'):
        return 'Service layer'
    elif name.endswith('Repository'):
        return 'Repository'
    elif name.endswith('Entity'):
        return 'JPA entity'
    elif name.endswith('Test'):
        return 'Test suite'
    
    return 'Java class'


def analyze_generic_file(file_path: Path) -> str:
    """Analyze non-code files."""
    ext = file_path.suffix.lower()
    
    generic_desc = {
        # Documentation
        '.txt': 'Text document',
        '.md': 'Markdown documentation',
        '.rst': 'reStructuredText documentation',
        '.adoc': 'AsciiDoc documentation',
        
        # Config
        '.json': 'JSON configuration',
        '.yaml': 'YAML configuration',
        '.yml': 'YAML configuration',
        '.toml': 'TOML configuration',
        '.ini': 'INI configuration',
        '.xml': 'XML configuration',
        '.properties': 'Properties file',
        '.conf': 'Configuration file',
        
        # Environment
        '.env': 'Environment variables',
        
        # Scripts
        '.sh': 'Shell script',
        '.bash': 'Bash script',
        '.zsh': 'Zsh script',
        '.fish': 'Fish script',
        '.ps1': 'PowerShell script',
        '.bat': 'Batch script',
        '.cmd': 'Command script',
        
        # Data
        '.sql': 'SQL script',
        '.csv': 'CSV data file',
        '.tsv': 'TSV data file',
        '.parquet': 'Parquet data file',
        
        # Web
        '.html': 'HTML template',
        '.htm': 'HTML template',
        '.css': 'Stylesheet',
        '.scss': 'Sass stylesheet',
        '.sass': 'Sass stylesheet',
        '.less': 'LESS stylesheet',
        
        # Images
        '.svg': 'SVG image',
        '.png': 'PNG image',
        '.jpg': 'JPEG image',
        '.jpeg': 'JPEG image',
        '.gif': 'GIF image',
        '.webp': 'WebP image',
        
        # Other code files
        '.c': 'C source file',
        '.h': 'C header file',
        '.cpp': 'C++ source file',
        '.cc': 'C++ source file',
        '.cxx': 'C++ source file',
        '.hpp': 'C++ header file',
        '.cs': 'C# source file',
        '.rb': 'Ruby script',
        '.php': 'PHP script',
        '.swift': 'Swift source file',
        '.kt': 'Kotlin source file',
        '.scala': 'Scala source file',
        '.r': 'R script',
        '.lua': 'Lua script',
        '.vim': 'Vim script',
        '.el': 'Emacs Lisp',
        '.clj': 'Clojure source',
        '.hs': 'Haskell source',
        '.erl': 'Erlang source',
        '.ex': 'Elixir source',
        '.dart': 'Dart source file',
        
        # Build files
        '.lock': 'Lock file',
        '.sum': 'Checksum file',
    }
    
    return generic_desc.get(ext, 'Data file')


def analyze_file(file_path: Path) -> str:
    """
    Analyze any file and return a one-line description.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        Single-line description of the file's purpose
    """
    filename = file_path.name
    
    # Check for special filenames first
    if filename in SPECIAL_FILES:
        return SPECIAL_FILES[filename]
    
    # Get file extension
    ext = file_path.suffix.lower()
    
    # Route to appropriate analyzer based on extension
    if ext == '.py':
        lines = read_file_head(file_path)
        if lines:
            return analyze_python_file(file_path, lines)
        return 'Python module'
    
    elif ext in ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs']:
        lines = read_file_head(file_path)
        if lines:
            return analyze_js_file(file_path, lines)
        return 'JavaScript module'
    
    elif ext == '.go':
        lines = read_file_head(file_path)
        if lines:
            return analyze_go_file(file_path, lines)
        return 'Go module'
    
    elif ext == '.rs':
        lines = read_file_head(file_path)
        if lines:
            return analyze_rust_file(file_path, lines)
        return 'Rust module'
    
    elif ext == '.java':
        lines = read_file_head(file_path)
        if lines:
            return analyze_java_file(file_path, lines)
        return 'Java class'
    
    elif ext == '.rb':
        folder_hint = get_folder_context(file_path)
        if folder_hint:
            return folder_hint
        return 'Ruby script'
    
    elif ext == '.php':
        folder_hint = get_folder_context(file_path)
        if folder_hint:
            return folder_hint
        return 'PHP script'
    
    elif ext in ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp']:
        folder_hint = get_folder_context(file_path)
        if folder_hint:
            return folder_hint
        if ext in ['.h', '.hpp']:
            return 'Header file'
        return 'C/C++ source file'
    
    else:
        # Generic file analysis
        return analyze_generic_file(file_path)