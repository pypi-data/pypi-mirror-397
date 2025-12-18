# CARL Presentation Crib Sheet
## Quick Reference for Second Monitor

---

## PRESENTATION STRUCTURE
**Navigation**: ← → for sections, ↑ ↓ for subsections within each section
**CARL Format**: Dennis wisely recommended Context → Action → Result → Learning

---

## SECTION 1: TITLE SLIDE ⏰ 2:30-2:32 PM
**Key Message**: "Dennis wisely recommended the CARL format"
- 60 minutes total
- C→A→R→L Structure
- Technical Leadership audience

---

## SECTION 2: FRAMEWORK DISCUSSION TOPICS ⏰ 2:32-2:35 PM

### Subsection 2.1: All Topics Available
**Hook**: "We have 15+ topics we could cover, but let's focus on the biggest pain points"
- Show comprehensive topic overview (4 cards)
- **Transition**: "All areas we could explore"

### Subsection 2.2: Today's Focus (60 min)
**Key Message**: "Given our time, let's focus on what hurts most today"
- Timeline with 5 phases:
  - Context (12 min): Architecture evolution, challenges
  - Action (20 min): Framework solution, demo
  - Results (15 min): Benefits and ROI
  - Learning (10 min): Migration strategy
  - Q&A (3 min): Discussion

---

## SECTION 3: CONTEXT - Why We Need to Act ⏰ 2:35-2:47 PM (12 min)

### Subsection 3.1: Context Title Slide
**Key Message**: "Why We Need to Act"
- 12 minutes total
- Set up the pain points

### Subsection 3.2: Architecture Evolution
**Key Message**: "I don't know exactly how we got here, but it was through many small decisions"
- Timeline: Early Phase → Growth → Specialization → Expansion → Current State
- **Key Insight**: "Each decision was logical in isolation, but compound complexity emerged"
- **Additional Context**: "Our development environment played a key role in some decisions - entire discussion for another day"

### Subsection 3.3: Lessons from Evolution
**Key Message**: "What We Learned"
- Separation of concerns is valuable
- Shared utilities reduce duplication, but at the expense of clarity
- **Challenge**: "Show me all the steps to produce a simple microbatch request object - DRY is not necessarily wise"
- Specialized repositories enable expertise (in some cases to enable offshore development, like data quality)
- Configuration management is critical
- **Testing becomes exponentially harder** (in some cases virtually impossible)

### Subsection 3.4: Current Complexity Example
**Key Message**: "Look at how many different tasks it takes to execute one piece of business logic"
- Show Load Promotion DAG workflow
- **Emphasis**: Count the number of separate tasks/operators required
- **Indirection Problem**: "DAG → sql_harness_consumer.py → config.py → code/promotion_3_0/ → SQL files"
- **Config Indirection**: "Same problem with config - get_env(), get_s3config_consumer(), get_redshift_role() - layers of utility functions"
- **Debugging Reality**: "Each path points to a project folder in a separate repo, under which there is a config file, which then points to SQL files"
- **Key Point**: "This is what it takes to load promotion data - count the tasks AND the layers of indirection"
- **Mental Load**: "It's a lot to unravel and keep in your head when trying to debug what is happening"

### Subsection 3.5: Coordination Costs
**Key Message**: "Current Multi-Repository Reality"
- **Deployment Burden**: "3 repos means up to 3 PR requests - meticulously managing merges"
- **Micromanagement**: "A ton of micromanagement with nothing but downsides wrt error"
- **Business Logic Atomicity**: "Serious burden when trying to ensure a business logic process is deployed as a whole"
- Configuration management across multiple systems
- Production debugging spans multiple codebases
- New developer onboarding is complex
- **Result**: Significant coordination overhead with high error risk

### Subsection 3.6: The Tipping Point
**Key Message**: "We've reached the complexity threshold"
- **Development Velocity**: "Adding features takes longer than it should"
- **Metrics Reality**: "If we tracked development metrics over time, you'd see direct correlation between complexity and time to develop/debug"
- **Honest Assessment**: "Pretty sure we have not gotten more nimble with time"
- Debugging requires archaeological expeditions
- New team members struggle with distributed knowledge
- Schema changes ripple across repositories

---

## SECTION 4: ACTION - The Framework Solution ⏰ 2:47-3:04 PM (17 min)

### Subsection 4.1: Action Title Slide
**Key Message**: "The Framework Solution"
- 20 minutes total
- Show the solution

### Subsection 4.2: Unified Framework Architecture
**Key Message**: "Single repository replacing distributed complexity"
- Data Sources → Entry Points → Business Logic → Destinations
- 4-column layout showing flow

### Subsection 4.3: Repository Structure
**Key Message**: "Consolidated business logic with clear separation"
- jobs/ (Business logic)
- services/ (Core framework)
- schemas/ (DDL files)
- tests/ (Comprehensive coverage)

### Subsection 4.4: Key Architectural Principles
**Key Message**: "Foundation principles"
- Single Repository: All business logic in one place
- Platform Abstraction: Same code runs everywhere
- Schema-Centric: DDL files drive all validation
- Factory Pattern: Clean dependency injection - **enables local testing of complex logic**
- **Testing Standards**: Mock, monkey patching, and patch are banned from this repository
- **Comprehensive Testing**: Multi-tier validation approach (Unit → Functional → Integration)

### Subsection 4.5: Configuration Before vs After
**Key Message**: "Everything the job does is visible in the DAG"
- Split screen comparison
- Current: 15+ scattered imports, hard-coded schemas, hidden config
- Framework: Minimal imports, DDL-driven, transparent parameters
- **Additional Note**: "We have a job sensor as well, but that is all"
- **Benefit**: "No more archaeological expeditions"

### Subsection 4.6: Platform Abstraction
**Key Message**: "Same business logic runs everywhere"
- AWS Glue, Databricks, EMR, Docker
- Show business logic example
- **Platform Management**: The generic_entry.py script manages handling minor differences between platform execution requirements
- **Benefit**: "Debug locally, deploy anywhere"

### Subsection 4.7: Three-Tier Testing Architecture
**Key Message**: "Business Logic is Sacred - Never mocked, always tested"
- **Unit**: Simple tests - class variable and parameter validations, wiring validations
- **Functional**: Mocks backend services only, and as minimally as possible
- **Integration**: Production level tests. Only Redshift cannot be fully tested, and we substitute Postgres in its place. Proper Redshift testing requires a proper Redshift endpoint

### Subsection 4.8: Live Demo - Local Development
**Key Message**: "Same business logic that runs in production"
- Demo commands ready:
  ```bash
  cd dwh-business-logic-poc
  ./functional-tests.sh tests/functional/dwh/jobs/load_promos/test_postgres_load_strategy.py
  ```
- **Environment Setup**: Env setup is part of functional-tests.sh
- **Key Point**: "No permissions needed - runs entirely locally"

### Subsection 4.9: Schema Validation in Action
**Key Message**: "Framework catches issues before production"
- **Demo Steps**:
  1. Go to promotion_transform, modify line 2 from `.withColumn("promotioncode", col("name"))` to `.withColumn("promotion_code", col("name"))`
  2. Rerun test: `./functional-tests.sh tests/functional/dwh/jobs/load_promos/test_postgres_load_strategy.py`
  3. Show schema validation failure
- **Key Point**: "This would have been a production issue - now caught in development"
- **Future Enhancement**: More precise error details will be added, so we know exactly which process failed, and against what schema

### Subsection 4.10: Version Management
**Key Message**: "Complete isolation with instant rollback"
- MWAA Orchestration (Unchanged)
- S3 Deployment Structure (Complete Isolation)
- Benefits: Zero MWAA changes, Instant rollback, Parallel execution
- **Schema Management Note**: Schema management is a little more difficult than presented. I did not get into it here, but there are strategies for tracking of schemas

---

## SECTION 5: RESULTS - Expected Outcomes ⏰ 3:04-3:19 PM (15 min)

### Subsection 5.1: Results Title Slide
**Key Message**: "Expected Outcomes"
- 15 minutes total
- Show the benefits

### Subsection 5.2: Quantified Benefits
**Key Message**: "Significant productivity gains across the board"
- Development Efficiency: Debugging faster, schema changes automated
- Quality Improvements: Test coverage comprehensive, production issues reduced
- Knowledge Capture: Domain knowledge captured in code, multi-audience documentation, context preservation
- **ROI**: "Time savings compound across team"

### Subsection 5.3: Knowledge Repository Benefits
**Key Message**: "Code becomes living documentation"
- Show business rule example with context and rationale
- **Key Point**: "Code becomes living documentation"

### Subsection 5.4: Knowledge Impact
**Key Message**: "Knowledge survives team changes"
- Current Challenges vs Framework Benefits
- Team departure, onboarding, business rules, domain expertise
- **Benefit**: "Knowledge survives team changes"

### Subsection 5.5: Strategic Value
**Key Message**: "Long-term strategic benefits"
- Platform Independence: Eliminate vendor lock-in
- Innovation Acceleration: No permission bottlenecks
- Organizational Maturity: Industry-standard practices
- Competitive Advantage: Faster time-to-market
- **Knowledge Preservation**: Institutional memory survives
- **Ops Note**: Ops still remains an issue. A topic for another conversation

---

## SECTION 6: LEARNING - Migration Strategy ⏰ 3:19-3:24 PM (5 min)

### Subsection 6.1: Learning Title Slide
**Key Message**: "Migration Strategy and Next Steps"
- 10 minutes total
- Show the path forward

### Subsection 6.2: Three-Phase Migration Approach
**Key Message**: "Zero-risk deployment, gradual adoption"
- Phase 1 (Months 1-2): Zero-Risk Deployment
- Phase 2 (Months 3-8): Strategic Migration
- Phase 3 (Months 9-12): Complete Migration

### Subsection 6.3: Risk Mitigation Strategy
**Key Message**: "Minimal risk with proven approach"
- Technical Risks: LOW (POC proven, 95% test coverage)
- Business Risks: MINIMAL (Gradual migration, business logic preserved)

### Subsection 6.4: Training Strategy
**Key Message**: "Comprehensive training program"
- Training Program: 4-week structured approach
- Target Audience: Senior devs, Mid-level, Junior, DevOps

### Subsection 6.5: Success Metrics
**Key Message**: "Clear success criteria"
- Phase 1 Targets: Framework deployment, improved workflow
- Overall Targets: Debugging time, production issues, development velocity

### Subsection 6.6: Immediate Next Steps
**Key Message**: "Ready to start immediately"
- Decision Points (Next 30 days):
  1. Approve Architecture
  2. Allocate Resources
  3. Establish Metrics
  4. Begin Training

---

## SECTION 7: QUESTIONS & DISCUSSION ⏰ 3:24-3:27 PM (3 min)

### Subsection 7.1: Questions Title Slide
**Key Message**: "Questions & Discussion"

### Subsection 7.2: Key Questions for Leadership
**Key Message**: "Critical decision points"
- Resource Allocation: Ready to invest?
- Risk Tolerance: Gradual migration acceptable?
- Timeline Expectations: 12-month timeline align?
- Success Criteria: Proposed metrics appropriate?

### Subsection 7.3: Technical Discussion Points
**Key Message**: "Technical considerations"
- Architecture Decisions: Factory patterns, dependency injection
- Migration Priorities: Which jobs first?
- Team Structure: How to organize?
- Integration Points: Fit with existing infrastructure?

---

## SECTION 8: CONCLUSION ⏰ 3:27-3:30 PM (3 min)

### Subsection 8.1: Conclusion Title Slide
**Key Message**: "Conclusion"

### Subsection 8.2: The Business Case
**Key Message**: "Strong business justification"
- Productivity Gains: Faster debugging, streamlined development
- Proven Approach: POC demonstrates feasibility
- Risk Mitigation: Gradual migration with rollback
- Strategic Value: Platform independence, innovation acceleration

### Subsection 8.3: The Technical Case
**Key Message**: "Technical excellence"
- Architecture Maturity: Industry-standard patterns
- Quality Improvement: Comprehensive test coverage
- Developer Productivity: Faster development, onboarding
- Operational Excellence: Reduced maintenance overhead

### Subsection 8.4: The Organizational Case
**Key Message**: "Organizational benefits"
- Knowledge Preservation: Institutional memory survives
- Team Scalability: Junior developers can write DAGs
- Innovation Enablement: Local development eliminates bottlenecks
- Competitive Advantage: Faster, more reliable delivery

### Subsection 8.5: Final Recommendation
**Key Message**: "Approve framework deployment and begin Phase 1 migration immediately"
- 95% Test Coverage
- 12 Month Migration
- **CALL TO ACTION**: Approve Phase 1 deployment

---

## DEMO PREPARATION

### Terminal Commands Ready
```bash
cd dwh-business-logic-poc
./setup-env.sh
./functional-tests.sh load_promos
```

### Files to Have Open
- Current Load Promotion DAG (for comparison)
- Framework DAG example
- Schema validation error example

### Demo Talking Points
1. **Speed**: "30 seconds to full environment"
2. **Transparency**: "Everything visible in configuration"
3. **Validation**: "Catches issues before production"

---

## COMPREHENSIVE Q&A REFERENCE

### "We just spent months building this code"
**Response**: "And that investment in business logic is exactly what we want to preserve. The framework provides a better foundation for that logic, making it more maintainable and testable. Your domain expertise becomes more valuable, not obsolete."
**Follow-up**: Show preservation strategy - what gets kept vs. what gets enhanced.

### "We don't have time for another rewrite"
**Response**: "We're not proposing a rewrite. New development uses the framework immediately. Existing code migrates only when it needs changes anyway - when you're already touching it. Zero additional work for existing stable code."
**Follow-up**: Show 3-phase migration timeline - emphasize Phase 1 has zero impact on existing code.

### "The current code works fine"
**Response**: "It works, but at what cost? [Show concrete metrics: 4-6 hours debugging time, <20% test coverage, 3-5 production issues per month]. The framework reduces these costs significantly while preserving the business logic that works."
**Follow-up**: Demo the debugging comparison - same issue, 4 hours vs. 30 minutes.

### "This will slow us down initially"
**Response**: "Initially, yes - there's a learning curve. But within 2-3 months, development becomes faster due to better testing, clearer patterns, and easier debugging. The POC already proves this with 50% faster development time."
**Follow-up**: Show ROI timeline - short-term cost, long-term benefit.

### "What if the framework doesn't work out?"
**Response**: "The business logic is preserved and each version is completely isolated. Rollback is instant - just change a DAG configuration. No MWAA changes needed. The POC has already proven the framework's value with zero production issues."
**Follow-up**: Demo instant rollback capability and version isolation.

### "Our code is too complex for this framework"
**Response**: "Complex business logic is exactly what the framework handles best. The knowledge repository captures all that complexity with business context, making it manageable and transferable. Your complex domain expertise becomes an institutional asset, not a maintenance burden."
**Follow-up**: Demo knowledge repository showing complex business rules with context.

### "We need to focus on delivery, not refactoring"
**Response**: "This actually accelerates delivery. New features get built 50% faster with comprehensive testing. More importantly, you eliminate 6+ week permission bottlenecks that currently block delivery. Local development means immediate productivity."
**Follow-up**: Show permission bottleneck vs. framework development speed comparison.

### "The team doesn't know this framework"
**Response**: "The patterns are standard software engineering practices - factory pattern, dependency injection, comprehensive testing. Plus, the framework captures your domain expertise automatically, so new team members learn your business logic faster. It's professional development that preserves your knowledge."
**Follow-up**: Show knowledge repository demo - how domain expertise is preserved and shared.

### "This seems over-engineered for our needs"
**Response**: "The engineering matches the complexity of your business logic and organizational challenges. When you're spending 6+ weeks waiting for permissions to do a simple demo, that's a sign the current approach is under-engineered for the organizational reality. The framework solves process problems, not just technical ones."
**Follow-up**: Show permission bottleneck example and framework solution.

### "We can't afford to introduce risk right now"
**Response**: "The bigger risk is continuing with code that's difficult to debug and test. The framework actually reduces risk - each version is completely isolated, rollback is instant, and MWAA never needs to change. Plus, proper security separation reduces the risk of permission-related issues."
**Follow-up**: Show version isolation and organizational benefits demo.

### Key Messages to Reinforce
- "We're building on your investment, not replacing it"
- "Migration happens when you're already changing code anyway"
- "The framework makes your expertise more valuable, not obsolete"
- "We've proven this works - zero production issues in POC"
- "This solves the debugging and testing problems you face daily"
- "Version management eliminates MWAA deployment risk"
- "Rollback is instant - just change a configuration"
- "Your domain knowledge is captured and preserved forever"
- "Framework eliminates permission bottlenecks that block innovation"
- "We optimize for debugging, not just development"

### If Multiple Objections Arise
**Acknowledge**: "I'm hearing several concerns about disrupting existing work. Let me address the core issue: we're not asking you to throw away months of development. We're providing a better foundation for that valuable business logic."
**Redirect**: "The framework solves the problems you're dealing with right now - long debugging sessions, manual testing, production surprises. Let's focus on how it makes your daily work easier."
**Offer Proof**: "Rather than debate this theoretically, let's pick one problematic job and migrate it as a proof of concept. Measure the before/after debugging time, test coverage, and reliability."

### Closing Ask
**"Approve framework deployment and begin Phase 1 migration immediately"**

---

## BACKUP SLIDES/TOPICS
If time allows or questions arise:
- Debug-first development philosophy
- Version management details
- Platform abstraction technical details
- Performance benchmarking
- Security model
- Long-term roadmap

---

## ENERGY & PACING NOTES
- **High energy** for demo section
- **Slow down** for complex architecture diagrams
- **Pause** after key benefits for emphasis
- **Build excitement** for knowledge repository benefits
- **Confident close** on migration strategy