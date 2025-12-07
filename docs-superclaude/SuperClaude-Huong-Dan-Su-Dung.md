# Hướng Dẫn Sử Dụng SuperClaude Framework

## Mục Lục
- [Giới Thiệu](#giới-thiệu)
- [Cài Đặt](#cài-đặt)
- [Kiến Trúc Framework](#kiến-trúc-framework)
- [Các Thành Phần Chính](#các-thành-phần-chính)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Ví Dụ Thực Tế](#ví-dụ-thực-tế)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Giới Thiệu

### SuperClaude là gì?

SuperClaude là một **meta-programming configuration framework** được thiết kế để nâng cao khả năng của Claude Code, biến nó thành một nền tảng phát triển phần mềm có cấu trúc và mạnh mẽ thông qua:
- **Behavioral Instruction Injection**: Chèn các hướng dẫn hành vi cụ thể
- **Component Orchestration**: Điều phối các thành phần một cách thông minh

### Tại sao nên sử dụng SuperClaude?

✅ **Tăng năng suất**: Tự động hóa các tác vụ phức tạp với 25 slash commands
✅ **Chuyên môn hóa**: 16 AI agents chuyên biệt cho từng lĩnh vực
✅ **Linh hoạt**: 7 chế độ hành vi thích ứng theo ngữ cảnh
✅ **Mở rộng**: Tích hợp 8 MCP servers mạnh mẽ
✅ **Thông minh**: Nghiên cứu web tự động, phân tích đa chiều

---

## Cài Đặt

### Yêu Cầu Hệ Thống

- **Python**: 3.9 trở lên
- **pip/pipx**: Đã cài đặt và được thêm vào PATH
- **Claude Code**: CLI đã được cài đặt

### Phương Pháp Cài Đặt (Khuyên Dùng: pipx)

#### 1. Cài Đặt pipx (nếu chưa có)

```bash
# macOS/Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Khởi động lại terminal hoặc source shell config
source ~/.bashrc  # hoặc ~/.zshrc
```

#### 2. Cài Đặt SuperClaude

```bash
# Cài đặt SuperClaude qua pipx
pipx install SuperClaude

# Nâng cấp lên phiên bản mới nhất
pipx upgrade SuperClaude
```

#### 3. Chạy Trình Cài Đặt Framework

**Cài đặt tương tác** (khuyên dùng):
```bash
SuperClaude install
```

**Cài đặt tự động** (tất cả components):
```bash
SuperClaude install --yes --components core modes agents commands mcp mcp_docs
```

**Cài đặt tùy chỉnh**:
```bash
# Chỉ cài các components cơ bản
SuperClaude install --components core commands

# Xem danh sách components có thể cài
SuperClaude install --list-components
```

#### 4. Xác Nhận Cài Đặt

```bash
# Kiểm tra thư mục cài đặt
ls ~/.claude/

# Các files/folders quan trọng:
# - agents/          : 16 AI agents chuyên biệt
# - commands/sc/     : 25 slash commands
# - MODE_*.md        : 7 behavioral modes
# - CLAUDE.md        : Entry point của framework
# - PRINCIPLES.md    : Nguyên tắc kỹ thuật
# - RESEARCH_CONFIG.md : Cấu hình nghiên cứu
```

### Cấu Trúc Thư Mục Sau Cài Đặt

```
~/.claude/
├── CLAUDE.md                    # Framework entry point
├── agents/                      # 16 specialized agents
│   ├── deep-research-agent.md
│   ├── frontend-architect.md
│   ├── backend-architect.md
│   ├── security-engineer.md
│   └── ...
├── commands/sc/                 # 25 slash commands
│   ├── analyze.md
│   ├── implement.md
│   ├── research.md
│   └── ...
├── MODE_*.md                    # 7 behavioral modes
│   ├── MODE_DeepResearch.md
│   ├── MODE_Brainstorming.md
│   └── ...
├── PRINCIPLES.md                # Engineering principles
├── RESEARCH_CONFIG.md           # Research configuration
├── RULES.md                     # Framework rules
└── backups/                     # Automatic backups
```

---

## Kiến Trúc Framework

### Tổng Quan Kiến Trúc

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERCLAUDE FRAMEWORK                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   25 Slash   │  │  16 AI       │  │  7 Behavioral│     │
│  │   Commands   │  │  Agents      │  │  Modes       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│  ┌────────────────────────┴──────────────────────────┐     │
│  │         Orchestration Engine                       │     │
│  │   - Intelligent routing                            │     │
│  │   - Context awareness                              │     │
│  │   - Parallel execution                             │     │
│  └────────────────────────┬──────────────────────────┘     │
│                           │                                 │
│  ┌────────────────────────┴──────────────────────────┐     │
│  │         8 MCP Servers Integration                  │     │
│  │   Tavily | Sequential | Magic | Playwright         │     │
│  │   Morphllm | Serena | Context7 | Chrome DevTools   │     │
│  └────────────────────────┬──────────────────────────┘     │
│                           │                                 │
│  ┌────────────────────────┴──────────────────────────┐     │
│  │              Claude Code Core                      │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Luồng Xử Lý

```
User Request
    ↓
Slash Command (/sc:*)
    ↓
Mode Detection & Activation
    ↓
Agent Selection (if needed)
    ↓
MCP Server Orchestration
    ↓
Parallel Tool Execution
    ↓
Result Synthesis
    ↓
Quality Validation
    ↓
Output Delivery
```

---

## Các Thành Phần Chính

### 1. Slash Commands (25 Commands)

Tất cả commands đều có prefix `/sc:` để tránh xung đột với các commands khác.

#### 📊 Analysis & Understanding

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:analyze` | Phân tích code toàn diện (quality, security, performance, architecture) | `/sc:analyze src/` |
| `/sc:explain` | Giải thích code, concepts, hành vi hệ thống một cách rõ ràng | `/sc:explain AuthService` |
| `/sc:troubleshoot` | Chẩn đoán và giải quyết vấn đề trong code, builds, deployments | `/sc:troubleshoot "login fails"` |

#### 💡 Planning & Design

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:brainstorm` | Khám phá yêu cầu qua đối thoại Socratic có hệ thống | `/sc:brainstorm "e-commerce app"` |
| `/sc:design` | Thiết kế kiến trúc hệ thống, APIs, component interfaces | `/sc:design "payment gateway"` |
| `/sc:estimate` | Ước tính thời gian phát triển cho tasks/features/projects | `/sc:estimate "user dashboard"` |
| `/sc:spec-panel` | Review và cải thiện specifications với panel chuyên gia | `/sc:spec-panel` |

#### 🔨 Implementation

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:implement` | Triển khai features với persona activation và MCP integration | `/sc:implement "OAuth login"` |
| `/sc:improve` | Cải thiện chất lượng code, performance, maintainability | `/sc:improve "slow queries"` |
| `/sc:build` | Build, compile, package projects với error handling thông minh | `/sc:build --optimize` |
| `/sc:cleanup` | Dọn dẹp code, xóa dead code, tối ưu cấu trúc project | `/sc:cleanup src/` |

#### 🧪 Testing & Quality

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:test` | Chạy tests với coverage analysis và quality reporting | `/sc:test --coverage` |

#### 📚 Documentation & Research

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:document` | Tạo documentation cho components, functions, APIs | `/sc:document API` |
| `/sc:research` | Nghiên cứu web sâu với adaptive planning và intelligent search | `/sc:research "React 19 features"` |
| `/sc:index` | Tạo comprehensive project documentation và knowledge base | `/sc:index` |

#### 🔄 Workflow & Task Management

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:task` | Thực thi complex tasks với intelligent workflow management | `/sc:task "refactor auth"` |
| `/sc:workflow` | Tạo structured implementation workflows từ PRDs | `/sc:workflow prd.md` |
| `/sc:spawn` | Meta-system task orchestration với intelligent breakdown | `/sc:spawn "microservices"` |

#### 🔧 DevOps & Git

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:git` | Git operations với intelligent commit messages | `/sc:git commit "Add auth"` |

#### 🎨 Business & Specialized

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:business-panel` | Multi-expert business analysis với adaptive interaction | `/sc:business-panel` |

#### 💾 Session Management

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:load` | Load project context với Serena MCP integration | `/sc:load project-name` |
| `/sc:save` | Save session context với Serena MCP | `/sc:save session-name` |
| `/sc:reflect` | Task reflection và validation với Serena analysis | `/sc:reflect` |

#### 🛠️ Utility

| Command | Mô Tả | Sử Dụng |
|---------|-------|---------|
| `/sc:help` | Liệt kê tất cả commands và functionality | `/sc:help` |
| `/sc:select-tool` | Intelligent MCP tool selection based on complexity | `/sc:select-tool` |

---

### 2. AI Agents (16 Specialized Agents)

Các agents được tự động kích hoạt dựa trên ngữ cảnh task.

#### 🏗️ Architecture & Design

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **System Architect** | Thiết kế kiến trúc tổng thể, patterns, scalability | Thiết kế hệ thống lớn, microservices |
| **Frontend Architect** | React, Vue, Angular, UI/UX architecture | Frontend apps, SPA, component design |
| **Backend Architect** | APIs, databases, server architecture | RESTful APIs, GraphQL, backend services |
| **DevOps Architect** | CI/CD, containers, cloud infrastructure | Deployment pipelines, Kubernetes, Docker |

#### 🔍 Analysis & Research

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **Deep Research Agent** | Web research, multi-hop reasoning, evidence synthesis | Nghiên cứu công nghệ mới, competitive analysis |
| **Requirements Analyst** | Phân tích yêu cầu, use cases, user stories | Thu thập requirements, PRD analysis |
| **Root Cause Analyst** | Debugging sâu, 5 Whys, causal chain analysis | Tìm nguyên nhân gốc rễ của bugs/issues |

#### 🛡️ Quality & Security

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **Security Engineer** | OWASP, vulnerability assessment, secure coding | Security audits, penetration testing prep |
| **Quality Engineer** | Testing strategies, test automation, QA processes | Test planning, quality assurance |
| **Performance Engineer** | Performance optimization, profiling, benchmarking | Tối ưu performance, load testing |

#### ♻️ Refactoring & Improvement

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **Refactoring Expert** | Code refactoring, design patterns, SOLID | Legacy code modernization, code cleanup |

#### 📝 Documentation & Education

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **Technical Writer** | Documentation, API docs, user guides | Viết documentation, README, guides |
| **Learning Guide** | Educational content, tutorials, explanations | Học công nghệ mới, training materials |
| **Socratic Mentor** | Guided learning, critical thinking, Q&A | Coaching, mentoring, skill development |

#### 💼 Business & Strategy

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **Business Panel Experts** | Multi-expert business analysis (14 personas) | Business strategy, product planning |

#### 💻 Language Specialists

| Agent | Chuyên Môn | Khi Nào Dùng |
|-------|-----------|--------------|
| **Python Expert** | Python best practices, async, frameworks | Python projects, Django, FastAPI |

---

### 3. Behavioral Modes (7 Adaptive Modes)

Modes tự động kích hoạt hoặc có thể bật bằng flags.

#### 🌟 MODE: Brainstorming

**Kích hoạt**: Requests mơ hồ, exploration keywords
**Flag**: `--brainstorm`

**Hành vi**:
- Collaborative discovery mindset
- Đặt câu hỏi thăm dò (probing questions)
- Khám phá nhiều khả năng
- Không implement ngay lập tức

**Khi nào dùng**:
```bash
/sc:brainstorm "I want to build something with AI"
/sc:design --brainstorm "social network features"
```

#### 🔬 MODE: Deep Research

**Kích hoạt**: `/sc:research`, research keywords
**Flag**: `--research`

**Hành vi**:
- Systematic investigation methodology
- Evidence-based reasoning
- Multi-hop exploration (lên đến 5 levels)
- Source credibility checking
- Parallel search execution

**Tính năng chính**:
- **Adaptive Planning**: 3 strategies (Planning-Only, Intent-Planning, Unified)
- **Multi-Hop Reasoning**: Entity expansion, temporal progression, causal chains
- **Quality Scoring**: Confidence levels, source credibility matrix
- **Tool Orchestration**: Tavily + Playwright + Sequential + Context7

**Khi nào dùng**:
```bash
/sc:research "latest AI developments 2024"
/sc:research "best practices for microservices" --depth deep
```

#### 🧠 MODE: Introspection

**Kích hoạt**: Self-analysis requests, error recovery
**Flag**: `--introspect`

**Hành vi**:
- Expose thinking process với transparency markers
- Phân tích quyết định và trade-offs
- Identify biases và assumptions
- Self-reflection và improvement

**Khi nào dùng**:
```bash
/sc:analyze --introspect "why did the build fail?"
```

#### 🎯 MODE: Task Management

**Kích hoạt**: Multi-step operations (>3 steps)
**Flag**: `--task-manage`

**Hành vi**:
- Orchestrate through delegation
- Systematic organization với TodoWrite
- Progress tracking chi tiết
- Breakdown complex tasks thành subtasks

**Khi nào dùng**:
```bash
/sc:implement --task-manage "complete authentication system"
```

#### 🎼 MODE: Orchestration

**Kích hoạt**: Multi-tool operations, parallel execution
**Flag**: `--orchestrate`

**Hành vi**:
- Optimize tool selection matrix
- Enable parallel thinking
- Intelligent MCP server routing
- Concurrent operation execution

**Khi nào dùng**:
```bash
/sc:task --orchestrate "analyze and refactor entire codebase"
```

#### ⚡ MODE: Token Efficiency

**Kích hoạt**: Context usage >75%, large-scale operations
**Flag**: `--token-efficient` hoặc `--uc` (ultra-compressed)

**Hành vi**:
- Symbol-enhanced communication
- 30-50% token reduction
- Compressed output format
- Essential information only

**Khi nào dùng**:
```bash
/sc:analyze --uc large-codebase/
/sc:document --token-efficient extensive-api/
```

#### 💼 MODE: Business Panel

**Kích hoạt**: `/sc:business-panel`
**Flag**: `--business-panel`

**Hành vi**:
- Multi-expert collaboration (14 business personas)
- Strategic analysis
- Business-focused communication
- Decision framework application

**Khi nào dùng**:
```bash
/sc:business-panel "evaluate SaaS pricing strategy"
```

---

### 4. MCP Servers (8 Powerful Integrations)

MCP (Model Context Protocol) servers mở rộng khả năng của Claude Code.

#### 🔍 Tavily - Web Search & Real-time Information

**Khả năng**:
- Real-time web search
- Content extraction từ URLs
- Up-to-date information retrieval
- News và current events

**Khi nào dùng**:
- Nghiên cứu thông tin mới nhất
- Competitive analysis
- Market research
- Technology trends

**Cài đặt**:
```bash
# Cần TAVILY_API_KEY
export TAVILY_API_KEY="your_api_key"
```

#### 🧵 Sequential-Thinking - Multi-step Reasoning

**Khả năng**:
- Complex problem decomposition
- Multi-step reasoning chains
- Systematic analysis
- Structured thinking

**Khi nào dùng**:
- Debugging phức tạp
- System design decisions
- Complex algorithms
- Trade-off analysis

#### ✨ Magic - UI Component Generation

**Khả năng**:
- Modern UI component generation
- Design system integration
- React/Vue/Svelte components
- Responsive layouts

**Khi nào dùng**:
- Frontend development
- UI prototyping
- Component libraries
- Design system implementation

**Flag**: `--magic`

#### 🎭 Playwright - Browser Automation & Testing

**Khả năng**:
- Cross-browser E2E testing
- Web scraping với JavaScript rendering
- Screenshot capture
- Browser automation

**Khi nào dùng**:
- E2E testing
- Web scraping dynamic content
- UI testing
- Browser automation tasks

**Flag**: `--play` hoặc `--playwright`

#### 🔄 Morphllm-Fast-Apply - Bulk Code Transformations

**Khả năng**:
- Fast Apply for context-aware modifications
- Bulk code transformations
- Pattern-based refactoring
- Multi-file updates

**Khi nào dùng**:
- Large-scale refactoring
- Rename across codebase
- Pattern application
- Migration tasks

**Flag**: `--morph` hoặc `--morphllm`

#### 💾 Serena - Session Persistence & Semantic Analysis

**Khả năng**:
- Session context persistence
- Semantic code analysis
- Project memory
- Intelligent editing

**Khi nào dùng**:
- Session management
- Long-term project context
- Symbol operations
- Cross-session learning

**Flag**: `--serena`

#### 📚 Context7 - Technical Documentation

**Khả năng**:
- Official library documentation
- Code examples
- API references
- Framework guides

**Khi nào dùng**:
- Learning new frameworks
- API integration
- Best practices lookup
- Documentation reference

**Flag**: `--c7` hoặc `--context7`

#### 🔧 Chrome-DevTools - Performance Analysis

**Khả năng**:
- Chrome DevTools debugging
- Performance profiling
- Network analysis
- Memory inspection

**Khi nào dùng**:
- Performance optimization
- Memory leak detection
- Network debugging
- Frontend profiling

---

### 5. Flags System

SuperClaude sử dụng flags để customize behavior và enable specific features.

#### 🎯 Analysis Depth Flags

| Flag | Token Usage | MCP Servers | Khi Nào Dùng |
|------|------------|-------------|--------------|
| `--think` | ~4K tokens | Sequential | Standard analysis, multi-component |
| `--think-hard` | ~10K tokens | Sequential + Context7 | Architectural analysis, dependencies |
| `--ultrathink` | ~32K tokens | All MCP servers | Critical redesign, legacy modernization |

**Ví dụ**:
```bash
/sc:analyze --think src/components/
/sc:design --think-hard "distributed system architecture"
/sc:troubleshoot --ultrathink "production memory leak"
```

#### 🔧 Execution Control Flags

| Flag | Mô Tả | Giá Trị |
|------|-------|---------|
| `--delegate [mode]` | Sub-agent parallel processing | auto, files, folders |
| `--concurrency [n]` | Max concurrent operations | 1-15 |
| `--loop` | Enable iterative improvement | boolean |
| `--iterations [n]` | Improvement cycle count | 1-10 |
| `--validate` | Pre-execution validation | boolean |
| `--safe-mode` | Maximum validation mode | boolean |

**Ví dụ**:
```bash
/sc:implement --delegate auto --concurrency 5 "refactor services"
/sc:improve --loop --iterations 3 "optimize performance"
/sc:build --safe-mode --validate "production deployment"
```

#### 🎨 Output Optimization Flags

| Flag | Mô Tả | Giá Trị |
|------|-------|---------|
| `--uc` / `--ultracompressed` | Token reduction 30-50% | boolean |
| `--scope` | Operational scope | file, module, project, system |
| `--focus` | Domain-specific targeting | performance, security, quality, architecture, accessibility, testing |

**Ví dụ**:
```bash
/sc:analyze --uc --scope module src/auth/
/sc:test --focus security tests/
/sc:document --scope system --focus architecture
```

#### 🔌 MCP Server Flags

| Flag | MCP Server | Mục Đích |
|------|-----------|----------|
| `--c7` / `--context7` | Context7 | Technical docs |
| `--seq` / `--sequential` | Sequential | Multi-step reasoning |
| `--magic` | Magic | UI components |
| `--morph` / `--morphllm` | Morphllm | Bulk transformations |
| `--serena` | Serena | Session persistence |
| `--play` / `--playwright` | Playwright | Browser automation |
| `--all-mcp` | All servers | Maximum capability |
| `--no-mcp` | None | Native-only |

**Ví dụ**:
```bash
/sc:research --c7 "React hooks documentation"
/sc:implement --magic --seq "dashboard UI with complex logic"
/sc:refactor --morph "rename UserService across codebase"
```

#### 🎯 Mode Activation Flags

| Flag | Mode | Trigger |
|------|------|---------|
| `--brainstorm` | Brainstorming | Exploration |
| `--introspect` | Introspection | Self-analysis |
| `--task-manage` | Task Management | Multi-step ops |
| `--orchestrate` | Orchestration | Multi-tool ops |
| `--token-efficient` | Token Efficiency | Context pressure |
| `--research` | Deep Research | Investigation |
| `--business-panel` | Business Panel | Business analysis |

#### 📏 Flag Priority Rules

1. **Safety First**: `--safe-mode` > `--validate` > optimization flags
2. **Explicit Override**: User flags > auto-detection
3. **Depth Hierarchy**: `--ultrathink` > `--think-hard` > `--think`
4. **MCP Control**: `--no-mcp` overrides all individual MCP flags
5. **Scope Precedence**: system > project > module > file

---

## Hướng Dẫn Sử Dụng

### Workflow Cơ Bản

#### 1️⃣ Khởi Động Project Mới

```bash
# Brainstorm ý tưởng
/sc:brainstorm "e-commerce platform for handmade goods"

# Sau khi có requirements rõ ràng, thiết kế architecture
/sc:design "microservices architecture for e-commerce"

# Estimate effort
/sc:estimate "MVP with user auth, product catalog, shopping cart"

# Tạo implementation workflow
/sc:workflow requirements.md
```

#### 2️⃣ Development Workflow

```bash
# Implement một feature
/sc:implement "user authentication with JWT"

# Build và test
/sc:build --validate
/sc:test --coverage

# Analyze code quality
/sc:analyze --think src/auth/

# Document code
/sc:document src/auth/AuthService.ts
```

#### 3️⃣ Code Review & Improvement

```bash
# Analyze toàn bộ codebase
/sc:analyze --think-hard --focus quality src/

# Refactor code có vấn đề
/sc:improve --loop --iterations 2 src/legacy/

# Cleanup unused code
/sc:cleanup src/

# Verify improvements
/sc:test --coverage
```

#### 4️⃣ Troubleshooting & Debugging

```bash
# Chẩn đoán issue
/sc:troubleshoot "API returning 500 errors intermittently"

# Deep analysis nếu cần
/sc:troubleshoot --ultrathink --introspect "memory leak in production"

# Root cause analysis
# (Automatically activates Root Cause Analyst agent)
```

#### 5️⃣ Research & Learning

```bash
# Research công nghệ mới
/sc:research "Next.js 14 Server Components best practices"

# Deep research với multiple sources
/sc:research --depth deep "microservices vs monolith trade-offs 2024"

# Research với specific strategy
/sc:research --strategy unified "GraphQL federation implementation"
```

---

### Workflows Chuyên Biệt

#### 🔒 Security Audit Workflow

```bash
# 1. Security analysis
/sc:analyze --focus security --think-hard src/

# 2. Vulnerability assessment (activates Security Engineer agent)
/sc:implement --focus security "add rate limiting and input validation"

# 3. Security testing
/sc:test --focus security tests/security/

# 4. Document security measures
/sc:document --focus security "Security Implementation Guide"
```

#### ⚡ Performance Optimization Workflow

```bash
# 1. Analyze performance bottlenecks
/sc:analyze --focus performance --think-hard src/

# 2. Research optimization techniques
/sc:research "React performance optimization 2024"

# 3. Implement optimizations (activates Performance Engineer)
/sc:improve --focus performance --loop --iterations 3 src/components/

# 4. Benchmark và validate
/sc:test --focus performance "run load tests"

# 5. Document optimizations
/sc:document --focus performance "Performance Improvements"
```

#### 🎨 Frontend Development Workflow

```bash
# 1. Design UI components
/sc:design --magic "responsive dashboard layout"

# 2. Implement với Magic MCP
/sc:implement --magic "Dashboard component with charts"

# 3. Test UI
/sc:test --playwright "dashboard E2E tests"

# 4. Analyze accessibility
/sc:analyze --focus accessibility src/components/

# 5. Document components
/sc:document src/components/Dashboard.tsx
```

#### 📊 Business Analysis Workflow

```bash
# 1. Activate business panel
/sc:business-panel "analyze SaaS pricing strategies"

# 2. Market research
/sc:research --depth deep "SaaS pricing models 2024"

# 3. Competitive analysis
/sc:research "competitor pricing analysis for project management tools"

# 4. Strategy recommendations
/sc:business-panel "recommend pricing tiers and features"
```

---

### Advanced Patterns

#### 🔄 Parallel Multi-Task Execution

```bash
# Orchestration mode tự động parallelize independent tasks
/sc:task --orchestrate --delegate auto "refactor auth module, update tests, improve documentation"
```

**Điều gì xảy ra**:
1. Task decomposition thành 3 independent subtasks
2. Parallel execution với appropriate agents:
   - Refactoring Expert cho auth refactor
   - Quality Engineer cho test updates
   - Technical Writer cho documentation
3. Progress tracking với TodoWrite
4. Final synthesis và validation

#### 🧩 Complex System Design

```bash
# Ultra-deep analysis cho system design
/sc:design --ultrathink --all-mcp "design distributed event-driven architecture for real-time collaboration platform"
```

**MCP Servers activated**:
- **Sequential**: Multi-step design reasoning
- **Context7**: Best practices documentation
- **Tavily**: Current architecture patterns research
- **Serena**: Session context persistence

#### 🔍 Comprehensive Code Analysis

```bash
# Multi-focus analysis
/sc:analyze --think-hard --scope project --focus "quality,security,performance" .
```

**Analysis covers**:
- **Quality**: Code smells, SOLID violations, technical debt
- **Security**: OWASP Top 10, vulnerability patterns
- **Performance**: Bottlenecks, optimization opportunities

#### 🚀 Full-Stack Feature Implementation

```bash
# End-to-end feature với multiple specialists
/sc:spawn --delegate auto --all-mcp "implement real-time chat feature with message persistence, typing indicators, and read receipts"
```

**Agents choreography**:
1. **System Architect**: Overall design
2. **Backend Architect**: WebSocket server, message storage
3. **Frontend Architect**: React components, real-time UI
4. **Security Engineer**: Authentication, authorization
5. **Performance Engineer**: Optimization, scaling
6. **Quality Engineer**: Test strategy
7. **Technical Writer**: API documentation

---

### Tips & Best Practices

#### ✅ DO's

1. **Sử dụng đúng command cho đúng task**
   - Research → `/sc:research`
   - Implementation → `/sc:implement`
   - Analysis → `/sc:analyze`

2. **Leverage flags để customize behavior**
   ```bash
   # Thay vì generic
   /sc:implement "add feature"

   # Nên specific
   /sc:implement --magic --validate --focus accessibility "add dashboard"
   ```

3. **Dùng depth flags phù hợp với complexity**
   - Simple → no flag hoặc `--think`
   - Complex → `--think-hard`
   - Critical → `--ultrathink`

4. **Enable MCP servers khi cần**
   ```bash
   # UI work → --magic
   # Research → --c7 hoặc default (Tavily)
   # Complex reasoning → --seq
   # Bulk refactoring → --morph
   ```

5. **Combine modes và flags**
   ```bash
   /sc:task --orchestrate --delegate auto --think-hard --all-mcp "complex multi-component task"
   ```

6. **Sử dụng session management cho long-running projects**
   ```bash
   # Save context
   /sc:save "my-project-session"

   # Load context later
   /sc:load "my-project-session"
   ```

#### ❌ DON'Ts

1. **Không overuse flags không cần thiết**
   ```bash
   # Overkill cho simple task
   /sc:explain --ultrathink --all-mcp "what is a variable"
   ```

2. **Không skip validation cho production code**
   ```bash
   # Luôn dùng --validate hoặc --safe-mode cho production
   /sc:build --safe-mode --validate
   ```

3. **Không dùng `--no-mcp` trừ khi thực sự cần**
   - MCP servers provide significant value
   - Only disable khi có lý do cụ thể (e.g., offline work)

4. **Không combine conflicting flags**
   ```bash
   # Contradiction
   /sc:research --no-mcp --c7  # --c7 sẽ bị ignore
   ```

5. **Không bỏ qua research trước khi implement**
   ```bash
   # Nên research trước
   /sc:research "best practices for feature X"
   # Rồi mới implement
   /sc:implement "feature X following best practices"
   ```

---

## Ví Dụ Thực Tế

### Case Study 1: Building Authentication System

```bash
# Step 1: Research best practices
/sc:research --depth deep "OAuth 2.0 implementation best practices 2024"

# Step 2: Design architecture
/sc:design --think-hard --c7 "secure authentication system with JWT and refresh tokens"

# Step 3: Estimate effort
/sc:estimate "authentication system with user registration, login, password reset, 2FA"

# Step 4: Generate implementation workflow
/sc:workflow "auth-requirements.md"

# Step 5: Implement (activates Backend Architect + Security Engineer)
/sc:implement --validate --focus security "authentication system"

# Step 6: Security analysis
/sc:analyze --focus security --think-hard src/auth/

# Step 7: Write tests
/sc:test --focus security tests/auth/

# Step 8: Document
/sc:document src/auth/ "Authentication System Documentation"

# Step 9: Final review
/sc:analyze --think src/auth/
```

### Case Study 2: Performance Optimization

```bash
# Step 1: Identify bottlenecks
/sc:analyze --focus performance --think-hard src/

# Step 2: Research optimization techniques
/sc:research "Node.js performance optimization techniques 2024"

# Step 3: Implement optimizations (activates Performance Engineer)
/sc:improve --focus performance --loop --iterations 3 src/api/

# Step 4: Add performance tests
/sc:test --focus performance "benchmark API endpoints"

# Step 5: Validate improvements
/sc:analyze --focus performance src/api/

# Step 6: Document optimizations
/sc:document "Performance Optimization Report"
```

### Case Study 3: Legacy Code Refactoring

```bash
# Step 1: Deep analysis của legacy code
/sc:analyze --ultrathink --scope project legacy/

# Step 2: Research modern patterns
/sc:research --c7 "modern design patterns for legacy modernization"

# Step 3: Create refactoring plan
/sc:design --think-hard "refactoring strategy for legacy module"

# Step 4: Estimate effort và risks
/sc:estimate --validate "legacy code refactoring"

# Step 5: Incremental refactoring (activates Refactoring Expert)
/sc:improve --loop --iterations 5 --safe-mode legacy/module1/

# Step 6: Test extensively
/sc:test --coverage legacy/module1/

# Step 7: Repeat for other modules
# ...

# Step 8: Final quality check
/sc:analyze --think-hard --focus quality refactored/

# Step 9: Comprehensive documentation
/sc:index refactored/ "Refactoring Documentation"
```

### Case Study 4: Full-Stack Feature Development

**Task**: Implement real-time collaborative document editing

```bash
# Phase 1: Research & Planning
/sc:research --depth exhaustive "real-time collaborative editing implementations WebSocket vs WebRTC"

/sc:design --ultrathink --all-mcp "real-time collaborative document editing architecture"

/sc:estimate "collaborative editing with OT/CRDT, presence, cursors, comments"

# Phase 2: Architecture Review
/sc:spec-panel "review collaborative editing architecture"

# Phase 3: Implementation
## Backend (activates Backend Architect + System Architect)
/sc:implement --validate --focus "performance,scalability" "WebSocket server with operational transformation"

## Frontend (activates Frontend Architect)
/sc:implement --magic --validate "collaborative editor UI with live cursors and presence"

## Real-time sync (activates Performance Engineer)
/sc:implement --seq --validate "conflict resolution with CRDT"

# Phase 4: Testing
/sc:test --playwright "E2E collaborative editing scenarios"
/sc:test --focus performance "load testing with 100 concurrent editors"

# Phase 5: Security & Performance
/sc:analyze --focus security src/collaboration/
/sc:analyze --focus performance src/collaboration/

# Phase 6: Optimization
/sc:improve --loop --iterations 3 --focus performance src/collaboration/

# Phase 7: Documentation
/sc:document --scope system "Collaborative Editing System"
/sc:index . "Complete Project Documentation"

# Phase 8: Final Review
/sc:analyze --think-hard --scope project .
```

### Case Study 5: API Development với Documentation

```bash
# Step 1: Design API
/sc:design --c7 --think-hard "RESTful API for task management with HATEOAS"

# Step 2: Research API best practices
/sc:research --depth deep "REST API design best practices 2024"

# Step 3: Implement API (activates Backend Architect)
/sc:implement --validate "Task Management REST API"

# Step 4: Generate OpenAPI specification
/sc:document --focus architecture "OpenAPI 3.0 specification for Task API"

# Step 5: Add API tests
/sc:test "API endpoint tests with various scenarios"

# Step 6: Security analysis
/sc:analyze --focus security --think api/

# Step 7: Generate comprehensive API documentation
/sc:document api/ "API Documentation with examples"

# Step 8: Create developer guide
/sc:document "API Developer Guide"
```

---

## Best Practices

### 🎯 Command Selection

**Chọn đúng command cho đúng phase**:

| Phase | Command | Rationale |
|-------|---------|-----------|
| Exploration | `/sc:brainstorm` | Mở rộng ý tưởng, khám phá khả năng |
| Research | `/sc:research` | Thu thập thông tin, best practices |
| Planning | `/sc:design`, `/sc:estimate` | Architecture, effort estimation |
| Implementation | `/sc:implement`, `/sc:task` | Code generation, execution |
| Quality | `/sc:analyze`, `/sc:test` | Quality assurance, testing |
| Maintenance | `/sc:improve`, `/sc:cleanup` | Refactoring, optimization |
| Documentation | `/sc:document`, `/sc:index` | Knowledge capture |
| Debugging | `/sc:troubleshoot` | Issue resolution |

### 🚀 Performance Optimization

1. **Leverage Parallel Execution**
   ```bash
   # Orchestration mode automatically parallelizes
   /sc:task --orchestrate "analyze security, performance, and quality"
   ```

2. **Use Appropriate Depth**
   - Start with `--think` for standard analysis
   - Use `--think-hard` only when needed
   - Reserve `--ultrathink` for critical decisions

3. **Cache Research Results**
   - Research results are cached (Tavily: 1 hour, Playwright: 24 hours)
   - Reuse research for related queries

4. **Token Efficiency**
   ```bash
   # For large-scale operations
   /sc:analyze --uc --scope project .
   ```

### 🛡️ Security Best Practices

1. **Always validate security-critical code**
   ```bash
   /sc:implement --validate --focus security "payment processing"
   ```

2. **Run security analysis**
   ```bash
   /sc:analyze --focus security --think-hard src/
   ```

3. **Use safe mode for production**
   ```bash
   /sc:build --safe-mode --validate
   ```

4. **Security testing**
   ```bash
   /sc:test --focus security tests/security/
   ```

### 📚 Documentation Best Practices

1. **Document as you go**
   ```bash
   /sc:implement "feature X"
   /sc:document "feature X"  # Ngay sau khi implement
   ```

2. **Use index for comprehensive docs**
   ```bash
   /sc:index . "Project Documentation"
   ```

3. **Specific vs General documentation**
   ```bash
   # Specific component
   /sc:document src/auth/AuthService.ts

   # Entire module
   /sc:document src/auth/ "Authentication Module Guide"

   # System-wide
   /sc:document --scope system "System Architecture"
   ```

### 🔄 Workflow Integration

1. **Git workflow integration**
   ```bash
   /sc:implement "add feature"
   /sc:test --coverage
   /sc:git commit "Add feature X with tests"
   ```

2. **CI/CD integration**
   ```bash
   /sc:build --validate --safe-mode
   /sc:test --coverage
   # Deploy nếu pass
   ```

3. **Session continuity**
   ```bash
   # End of day
   /sc:save "project-state-2024-10-09"

   # Next day
   /sc:load "project-state-2024-10-09"
   /sc:reflect  # Review previous work
   ```

---

## Troubleshooting

### Common Issues

#### ❌ Issue: MCP Server Not Found

**Triệu chứng**:
```
Error: MCP server 'tavily' not found
```

**Giải pháp**:
1. Check MCP server installation:
   ```bash
   SuperClaude install --list-components
   ```

2. Reinstall MCP component:
   ```bash
   SuperClaude install --components mcp
   ```

3. Verify MCP configuration trong `~/.claude/settings.json`

4. Hoặc disable MCP nếu không cần:
   ```bash
   /sc:research --no-mcp "query"
   ```

#### ❌ Issue: Command Not Recognized

**Triệu chứng**:
```
Command '/sc:xyz' not found
```

**Giải pháp**:
1. Verify command tồn tại:
   ```bash
   /sc:help
   ```

2. Check installation:
   ```bash
   ls ~/.claude/commands/sc/
   ```

3. Reinstall commands:
   ```bash
   SuperClaude install --components commands
   ```

#### ❌ Issue: API Key Missing (Tavily)

**Triệu chứng**:
```
Error: TAVILY_API_KEY environment variable not set
```

**Giải pháp**:
1. Get API key từ https://tavily.com

2. Set environment variable:
   ```bash
   # Temporary (current session)
   export TAVILY_API_KEY="your_api_key"

   # Permanent (add to ~/.bashrc hoặc ~/.zshrc)
   echo 'export TAVILY_API_KEY="your_api_key"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. Hoặc dùng `--no-mcp` để skip Tavily:
   ```bash
   /sc:research --no-mcp "query"
   ```

#### ❌ Issue: Slow Performance

**Triệu chứng**: Commands thực thi chậm

**Giải pháp**:

1. **Reduce analysis depth**:
   ```bash
   # Thay vì
   /sc:analyze --ultrathink src/

   # Dùng
   /sc:analyze --think src/
   ```

2. **Disable unnecessary MCP servers**:
   ```bash
   /sc:analyze --no-mcp src/  # Nếu không cần MCP
   ```

3. **Use token efficiency mode**:
   ```bash
   /sc:analyze --uc src/
   ```

4. **Scope appropriately**:
   ```bash
   # Thay vì
   /sc:analyze --scope project .

   # Dùng
   /sc:analyze --scope module src/auth/
   ```

#### ❌ Issue: Context Length Exceeded

**Triệu chứng**:
```
Error: Context length exceeded
```

**Giải pháp**:

1. **Use ultra-compressed mode**:
   ```bash
   /sc:analyze --uc large-codebase/
   ```

2. **Narrow scope**:
   ```bash
   /sc:analyze --scope file src/large-file.ts
   ```

3. **Break down task**:
   ```bash
   # Instead of analyzing entire codebase at once
   /sc:analyze src/module1/
   /sc:analyze src/module2/
   # etc.
   ```

4. **Use delegation**:
   ```bash
   /sc:task --delegate auto "analyze entire codebase"
   ```

#### ❌ Issue: Framework Files Not Loading

**Triệu chứng**: SuperClaude commands không hoạt động như expected

**Giải pháp**:

1. **Check CLAUDE.md import**:
   ```bash
   cat ~/.claude/CLAUDE.md
   ```
   Should see imports like `@PRINCIPLES.md`, `@MODE_*.md`, etc.

2. **Verify file permissions**:
   ```bash
   ls -la ~/.claude/
   ```

3. **Reinstall framework**:
   ```bash
   SuperClaude install --force --components core modes agents commands
   ```

4. **Check for backup và restore nếu cần**:
   ```bash
   ls ~/.claude/backups/
   # Restore từ backup nếu có issue
   ```

---

### Diagnostic Commands

```bash
# Check SuperClaude version
SuperClaude --version

# List installed components
SuperClaude install --list-components

# Run diagnostics
SuperClaude install --diagnose

# Verify installation
ls -la ~/.claude/

# Check command availability
/sc:help

# Test basic functionality
/sc:explain "what is SuperClaude?"
```

---

## Advanced Topics

### Custom Agent Creation

Bạn có thể tạo custom agents cho domain-specific needs.

**Template** (`~/.claude/agents/my-custom-agent.md`):

```markdown
---
name: my-custom-agent
description: Custom agent for specific domain expertise
category: custom
---

# My Custom Agent

## Triggers
- Specific keywords or patterns
- Explicit command activation

## Behavioral Mindset
Describe the thinking style and approach

## Core Capabilities
- Capability 1
- Capability 2
- Capability 3

## Workflow
1. Step 1
2. Step 2
3. Step 3

## Quality Standards
- Standard 1
- Standard 2

## Boundaries
**Excel at**: What this agent does best
**Limitations**: What it shouldn't do
```

### Custom Commands

Tạo custom slash commands:

**Template** (`~/.claude/commands/sc/my-command.md`):

```markdown
---
name: my-command
description: "Description of what this command does"
category: custom
complexity: medium
mcp-servers: [list, of, required, servers]
personas: [list, of, required, agents]
---

# /sc:my-command - Custom Command

## Triggers
- When to use this command
- Specific patterns or keywords

## Context Trigger Pattern
\```
/sc:my-command "[arguments]" [--flags]
\```

## Behavioral Flow

### 1. Understand
- What to analyze
- What to identify

### 2. Plan
- How to approach
- What strategy to use

### 3. Execute
- Implementation steps
- Tools to use

### 4. Validate
- Quality checks
- Success criteria

## Examples
\```
/sc:my-command "example usage"
\```

## Boundaries
**Will**: What this command does
**Won't**: What it doesn't do
```

### Custom Modes

Tạo custom behavioral modes:

**Template** (`~/.claude/MODE_MyMode.md`):

```markdown
---
name: MODE_MyMode
description: Custom mode description
category: mode
---

# My Custom Mode

## Activation Triggers
- Keyword patterns
- Explicit flags
- Contextual indicators

## Behavioral Modifications

### Thinking Style
- How thinking changes in this mode

### Communication Changes
- How output format changes

### Priority Shifts
- What becomes more important

### Process Adaptations
- How workflow adapts

## Integration Points
- Which agents activate
- Which MCP servers enable
- Which tools emphasize

## Quality Focus
- Key quality metrics
- Success criteria

## Output Characteristics
- Expected output format
- Key deliverables
```

---

## Resources & Links

### Official Documentation
- **GitHub Repository**: https://github.com/SuperClaude-Org/SuperClaude_Framework
- **Installation Guide**: Xem phần [Cài Đặt](#cài-đặt)
- **Command Reference**: `/sc:help` hoặc xem [Slash Commands](#1-slash-commands-25-commands)

### MCP Server Documentation
- **Tavily**: https://tavily.com
- **Context7**: Documentation trong framework
- **Playwright**: https://playwright.dev
- **Sequential Thinking**: Trong framework installation

### Learning Resources
- **SuperClaude Principles**: `~/.claude/PRINCIPLES.md`
- **Research Configuration**: `~/.claude/RESEARCH_CONFIG.md`
- **Agent Documentation**: `~/.claude/agents/`
- **Mode Documentation**: `~/.claude/MODE_*.md`

### Community & Support
- **GitHub Issues**: https://github.com/SuperClaude-Org/SuperClaude_Framework/issues
- **Discussions**: GitHub Discussions
- **Updates**: Follow repository for latest changes

---

## Kết Luận

SuperClaude Framework transforms Claude Code thành một development platform mạnh mẽ với:

✅ **25 specialized commands** cho mọi development lifecycle phase
✅ **16 expert AI agents** với domain-specific knowledge
✅ **7 adaptive behavioral modes** tự động điều chỉnh theo context
✅ **8 powerful MCP servers** mở rộng capabilities
✅ **Intelligent orchestration** với parallel execution và smart routing

### Quick Start Checklist

- [ ] Cài đặt pipx
- [ ] Cài đặt SuperClaude: `pipx install SuperClaude`
- [ ] Run installer: `SuperClaude install --yes --components core modes agents commands`
- [ ] Verify: `/sc:help`
- [ ] Test basic command: `/sc:explain "what is SuperClaude"`
- [ ] Try research: `/sc:research "something interesting"`
- [ ] Explore workflows: Xem [Ví Dụ Thực Tế](#ví-dụ-thực-tế)

### Next Steps

1. **Làm quen với commands**: Thử các commands cơ bản
2. **Explore agents**: Xem các agents trong `~/.claude/agents/`
3. **Experiment với modes**: Thử các behavioral modes
4. **Configure MCP servers**: Setup các servers cần thiết (Tavily, etc.)
5. **Build workflows**: Tạo custom workflows cho projects
6. **Customize**: Tạo custom agents/commands/modes nếu cần

### Pro Tips

💡 **Start simple**: Bắt đầu với basic commands, sau đó tăng complexity
💡 **Read agent docs**: Hiểu agents để leverage tốt hơn
💡 **Use flags wisely**: Flags are powerful, nhưng đừng overuse
💡 **Research first**: Luôn research trước khi implement
💡 **Document everything**: Dùng `/sc:document` frequently
💡 **Save sessions**: Dùng `/sc:save` và `/sc:load` cho continuity

---

**Happy Coding with SuperClaude! 🚀**

*Version: 1.0.0*
*Last Updated: 2024-10-09*
*Framework Version: SuperClaude v4.1.5*
