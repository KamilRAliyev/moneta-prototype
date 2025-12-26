
> **This document is authoritative.**
> Every new feature or change **MUST** comply with this checklist.
> AI (and humans) **MUST NOT** mark a feature as complete unless **all required items are satisfied**.

---

## **1. Documentation Policy**
### **New Documentation**

❌ Do **NOT** create new documentation by default.

### **Create new documentation** 

### **ONLY IF**:
- A new system, module, or service is introduced
- A new user workflow is added
- System responsibilities change
- Existing documentation cannot logically include the change
### **Otherwise:**
- ✅ Update existing documentation

**MUST explicitly state** whether documentation was **updated** or **new documentation was created**, and why.

---
## **2. Pre-Implementation Requirements**
- Feature goal defined (1–2 sentences)
- Acceptance criteria defined (clear pass/fail)
- Impacted components identified
- Existing documentation reviewed
- Architecture compatibility confirmed

---

## **3. Architecture Validation (MANDATORY)**

Before coding:
- Architecture diagrams reviewed
- Data flow verified
- Component responsibilities validated
- No hidden coupling introduced

If architecture changes:
- Architecture documentation updated
- Changes clearly documented

🚫 **No implementation without architecture validation.**

---
## **4. Implementation Checklist**

- Feature implemented in correct module/service/component
- Business logic not placed in UI
- Configuration not hard-coded
- Error handling implemented
- Logging added at decision/failure points
- Code follows project conventions
- No unrelated changes included

---
## **5. Testing Requirements (NON-NEGOTIABLE)**

Tests are **required for every feature**.
- Tests written specifically for this feature
- Happy path covered
- Edge cases covered
- Failure cases covered
- Tests fail before implementation
- Tests pass after implementation

Applicable test types:
- Unit
- Integration
- API / Contract
- End-to-End (if user-facing)

🚫 **A feature without tests is incomplete.**

---

## **6. Documentation Updates**

- Architecture documentation updated (if behavior or flow changed)
- API documentation updated (if endpoints/data changed)
- Configuration/environment documentation updated

---

## **7. Architecture Documentation Final Check**
After implementation:
- Architecture documentation matches actual code
- Diagrams reflect real data flow
- No undocumented behavior remains
- Documentation version/date updated

---
## **8. Completion Gate**
AI **MUST** verify:
- All tests written and passing
- Documentation updated correctly
- Architecture validated
- No checklist items skipped

🚫 **AI MUST refuse to mark the feature as complete if any item is unchecked.**
