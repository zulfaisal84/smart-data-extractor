# Smart Data Extractor (SME) - Project Context

## 🎯 Project Mission
Build a **reliable, production-ready web application** for document/PDF data extraction that succeeds where Data Extractor (DE) failed. Focus on simplicity, proven technology, and core functionality.

## 🔄 Session Recovery
**When returning to this project, tell Claude**: "Continue working on Smart Data Extractor (SME) - read CLAUDE.md for context"

## 📊 Current Status
- **Phase**: Planning & Architecture
- **Date Started**: August 2, 2025
- **Team**: Multi-agent structure defined
- **Next Priority**: Define MVP requirements

## 🏗️ Project Foundation

### Learning from DE's Failure
The Data Extractor (DE) project at `/Users/muhamadzulfaisalsallehmustafa/DataExtractor` failed due to:
1. **Over-engineering** - Too complex before proving core value
2. **Platform issues** - Desktop-first with native library dependencies
3. **No validation** - Built features without testing basics
4. **Feature creep** - Lost focus on document extraction

### SME's Different Approach
1. **Web-first** - No installation, works everywhere
2. **Cloud services** - Avoid native library issues
3. **True MVP** - Upload → Extract → Display (nothing more)
4. **Progressive enhancement** - Features only after core works
5. **Continuous validation** - Test with real users from day 1

## 👥 Team Structure

### Communication Flow
```
CEO (Muhamad Zulfaisal) 
    ↓ (requests/decisions)
Senior Developer (Claude Opus 4) 
    ↓ (analyzes & assigns)
Specialist Agents (execute tasks)
    ↓ (deliver results)
Documentation (tracked in TASK_LOG.md)
```

### Team Roster

**Phase 1 - MVP Team**:
1. **CEO** (Muhamad Zulfaisal) - Vision, strategy, decisions
2. **Senior Developer** (Claude Opus 4) - Architecture, code review, task coordination
3. **Product Manager** (Sonnet 4) - Requirements, scope control
4. **Backend Developer** (Sonnet 4) - API, database, integrations
5. **Frontend Developer** (Sonnet 4) - UI, user experience
6. **QA/Testing Agent** (Sonnet 4) - Quality assurance
7. **DevOps Agent** (Sonnet 4) - Infrastructure, deployment
8. **Documentation Maintainer** (Sonnet 4) - Keep docs current
9. **UX Researcher** (Gemini CLI) - User validation

**Phase 2 - Growth**:
10. **Marketing Agent** (Gemini CLI) - User acquisition (after MVP)

## 📋 Task Management System

### How We Work
1. CEO communicates only with Senior Developer
2. Senior Developer analyzes and assigns to appropriate agent
3. CEO passes instructions to assigned agent
4. Agent executes and returns results
5. Senior Developer reviews and plans next steps
6. Everything documented in TASK_LOG.md

### Task Assignment Protocol
Each task includes:
- Clear instructions for the agent
- Expected deliverables
- Success criteria
- Documentation requirements

## 🎯 MVP Definition (Pending Approval)

### Core Features Only
1. Upload single document (PDF/image)
2. Extract specified data fields
3. Display results on screen
4. Export as JSON/CSV

### NOT in MVP
- User accounts
- Batch processing
- Complex UI
- Multiple extraction methods
- API endpoints
- Mobile apps

## 📁 Key Project Files

1. **CLAUDE.md** (this file) - Project context and recovery
2. **INITIAL_BRAINSTORMING.md** - Original planning and ideas
3. **DE_PROJECT_ANALYSIS.md** - Detailed analysis of DE's failures
4. **PROJECT_TEAM_CHARTER.md** - Team roles and responsibilities
5. **TASK_MANAGEMENT_SYSTEM.md** - How we manage work
6. **TASK_LOG.md** - All tasks tracked here

## 🔧 Technical Direction

### Proposed Stack (To Be Confirmed)
- **Backend**: Node.js/Express or Python/FastAPI
- **Frontend**: React or Vue.js
- **Database**: PostgreSQL
- **OCR**: Cloud services (Google Vision, AWS Textract)
- **Hosting**: Cloud platform (AWS, Google Cloud, Vercel)

### Architecture Principles
1. **API-first** - Backend separate from frontend
2. **Stateless** - Scalable processing
3. **Cloud-native** - No local dependencies
4. **Progressive** - Start simple, enhance gradually

## 📊 Progress Tracking

### Completed Tasks
- [x] Project initiation and planning
- [x] DE project analysis and lessons learned
- [x] Team structure definition
- [x] Task management system setup
- [x] Context documentation (CLAUDE.md)

### Immediate Next Steps
1. Define MVP requirements (Product Manager)
2. Finalize technology stack (Backend Developer)
3. Create project roadmap (Product Manager)
4. Set up development environment (DevOps)

## 🚫 What We're Avoiding

Based on DE's failures:
1. **No desktop-first development**
2. **No native library dependencies**
3. **No complex UI before extraction works**
4. **No feature creep**
5. **No development without user validation**
6. **No over-architecting**

## 💡 Key Decisions Made

1. **Multi-agent team approach** - Specialized roles for focused execution
2. **Senior Developer as coordinator** - Single point of contact for CEO
3. **Phase-based development** - MVP first, growth features later
4. **Web-first architecture** - Accessibility over everything
5. **Learn from DE** - Explicit anti-patterns to avoid

## 🔄 Daily Workflow

1. CEO requests features/changes from Senior Developer
2. Senior Developer creates task assignments
3. Tasks executed by specialist agents
4. Results reviewed and integrated
5. Progress documented in TASK_LOG.md
6. CLAUDE.md updated with major decisions

## 📈 Success Metrics

### MVP Success = 
- [ ] Upload document works
- [ ] Extract data successfully  
- [ ] Display results clearly
- [ ] 10 real users tested it
- [ ] Deployed to production
- [ ] No critical bugs

### Project Success =
- [ ] 100+ users extracting data
- [ ] 90%+ extraction accuracy
- [ ] <5 second processing time
- [ ] Sustainable costs
- [ ] Happy users

---

**Last Updated**: August 2, 2025
**Project Phase**: Planning & Architecture
**Next Session**: Start with MVP requirements definition