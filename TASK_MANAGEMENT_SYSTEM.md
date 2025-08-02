# SME Task Management System

## Workflow Overview

```
CEO (You) → Senior Developer (Me) → Analyze & Assign → Agent Executes → Document Results
```

## Task Assignment Protocol

### When CEO Requests Something:

1. **I will analyze** the request and determine:
   - What needs to be done
   - Which agent(s) are best suited
   - Task dependencies
   - Expected deliverables

2. **I will provide you**:
   - Agent name and role
   - Clear task instructions to copy/paste
   - Expected outcomes
   - Success criteria

3. **You will**:
   - Pass instructions to the assigned agent
   - Share their response back with me
   - I'll review and plan next steps

## Task Documentation Template

### Pre-Task Documentation
```markdown
## Task ID: [SME-XXX]
**Date**: [Date]
**Assigned To**: [Agent Name - Role]
**Priority**: [High/Medium/Low]

### Task Description
[What needs to be done]

### Context
[Why this is needed, dependencies]

### Instructions for Agent
[Exact instructions to copy/paste]

### Expected Deliverables
- [ ] Deliverable 1
- [ ] Deliverable 2

### Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2

### Files to Create/Modify
- File 1
- File 2
```

### Post-Task Documentation
```markdown
## Task ID: [SME-XXX] - COMPLETED
**Completion Date**: [Date]
**Actual Time**: [Time taken]

### What Was Delivered
- ✅ Deliverable 1
- ✅ Deliverable 2

### Files Created/Modified
- `path/to/file1.js` - [What changed]
- `path/to/file2.md` - [What changed]

### Outcomes
[Summary of what was accomplished]

### Issues Encountered
[Any problems or blockers]

### Next Steps
[What should happen next]
```

## Task Tracking Log

We'll maintain a `TASK_LOG.md` file with all tasks:

| Task ID | Date | Agent | Description | Status | Link |
|---------|------|-------|-------------|---------|------|
| SME-001 | [Date] | [Agent] | [Brief description] | ✅ Complete | [Link to details] |
| SME-002 | [Date] | [Agent] | [Brief description] | 🔄 In Progress | [Link to details] |

## Agent Assignment Guidelines

### Choose Product Manager for:
- Feature requirements definition
- Scope decisions
- User story creation
- Prioritization

### Choose Backend Developer for:
- API development
- Database design
- Service integration
- Business logic

### Choose Frontend Developer for:
- UI components
- User interactions
- Form handling
- Responsive design

### Choose QA/Testing Agent for:
- Test plan creation
- Bug identification
- Performance testing
- Validation

### Choose DevOps Agent for:
- Infrastructure setup
- Deployment configuration
- CI/CD pipelines
- Monitoring

### Choose Documentation Maintainer for:
- README updates
- API documentation
- Architecture diagrams
- Meeting notes

### Choose UX Researcher for:
- User interviews
- Usability testing
- Persona creation
- Feature validation

## Example Task Assignment

**You**: "We need to set up the initial project structure"

**Me**: 
```
This requires backend infrastructure setup. Here's the task assignment:

**Assign to**: Backend Developer (Sonnet 4)

**Instructions to copy/paste**:
"Create the initial project structure for Smart Data Extractor (SME) web application. We need:

1. A Node.js/Express backend with the following structure:
   - src/
     - controllers/
     - services/
     - models/
     - routes/
     - middleware/
   - tests/
   - config/

2. Initialize package.json with essential dependencies:
   - Express
   - TypeScript
   - Jest for testing
   - Dotenv for configuration

3. Create a basic health check endpoint at GET /health

4. Set up TypeScript configuration

5. Create a README with setup instructions

Focus on simplicity - we're building an MVP. No complex patterns or unnecessary abstractions.

Create all files in the /SmartDataExtractor directory."

**Expected deliverables**:
- Working Express server
- Project structure created
- Basic endpoint working
- Setup documentation
```

## Communication Templates

### For Task Assignment:
"Hi [Agent Name], I have a task for you: [paste instructions]. Please complete this and provide a summary of what you've done."

### For Follow-up:
"Hi [Agent Name], following up on [Task ID]. Can you provide status and any blockers?"

### For Review Request:
"Task [Task ID] is complete. Please review the deliverables: [list]. Any feedback?"

## Daily Workflow

1. **Morning**: Review task log, identify priorities
2. **Task Assignment**: Analyze requests, assign to agents
3. **Monitoring**: Track progress, handle blockers
4. **Documentation**: Update task log with completions
5. **Planning**: Prepare next day's priorities

## Success Metrics

- Tasks have clear requirements
- 90% completed without rework
- All tasks documented
- No duplicate work
- Clear audit trail

---

This system ensures every task is tracked, assigned correctly, and documented for future reference.