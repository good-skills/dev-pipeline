# Refactoring (Plan/Execute phases)

Behavior-preserving remediation techniques for **confirmed** findings. Load at **Plan/Execute**. On any conflict SKILL.md wins: behavior preservation, minimal touch set, change budget, no new dependencies, tests protection.

Refactoring = gradual evolution, not revolution. Changes **how** code is structured, never **what** it does. For improving existing code — not rewriting from scratch.

## Golden rules

1. **Behavior preserved** — external behavior identical; prove via narrowest repo validation.
2. **Small steps** — one change → validate → next; every step revertible against the pre-execution baseline (SKILL.md Git baseline).
3. **Tests first** — touched code untested → add focused characterization tests **before** refactoring. Without tests you are editing, not refactoring.
4. **One concern at a time** — never mix refactoring with feature work or unrelated fixes.
5. **Purpose required** — no confirmed finding / no clear engineering benefit → `accepted`, no edit.

## When NOT to refactor

- Code that works and won't change again
- Untested critical code (add tests first, then proceed)
- Tight deadline pressure
- "Just because" — skill policy: low-benefit confirmed → `accepted`

## Smell → fix catalog

| Smell | Signal | Primary fix | Maps to |
|-------|--------|-------------|---------|
| S1 Long method | one body does fetch+validate+compute+notify | extract method per step; orchestrator calls steps | Pattern 1 |
| S2 Duplicated code | same logic block in ≥2 places | extract shared function/constant | manual-only (Pattern 6 = whole files only) |
| S3 Large class/module | mixed responsibilities in one type | extract class per responsibility | Pattern 4 |
| S4 Long parameter list | 4+ loose params, boolean flags | introduce parameter object; defaults for optional | manual-only |
| S5 Feature envy | method reads another object's data more than its own | move method to the data owner | manual-only |
| S6 Primitive obsession | domain concepts as raw strings/numbers | value object validating at creation | manual-only |
| S7 Magic numbers/strings | unexplained literals | named constants / const object | Pattern 7 |
| S8 Nested conditionals | arrow code, deep else trees | guard clauses / early returns | manual-only |
| S9 Dead code | unused functions/imports, commented-out code | delete — git history keeps it | Pattern 3 |
| S10 Inappropriate intimacy | `a.b.c.d` chains, reaching into internals | ask-don't-tell: intention-revealing method on owner | manual-only |

**Manual-only (S2, S4–S6, S8, S10):** no auto-scan; surface only during contextual inspection or on user request — same policy as Patterns 2/5.

## Before / after (compact)

### S1 → extract steps

```ts
// Before: 200-line processOrder doing everything inline
async function processOrder(orderId: string) {
  const order = await fetchOrder(orderId);
  validateOrder(order);
  const pricing = calculatePricing(order);
  await updateInventory(order);
  const shipment = await createShipment(order);
  await sendNotifications(order, pricing, shipment);
  return { order, pricing, shipment };
}
```

Extract in dependency order; validate after each extraction.

### S2 → shared function

```ts
const MEMBERSHIP_RATES = { gold: 0.2, silver: 0.1 } as const;
const rateFor = (m: Membership): number => MEMBERSHIP_RATES[m] ?? 0;
// calculateUserDiscount and calculateOrderDiscount both call rateFor
```

### S4 → parameter object

```ts
interface UserData { email: string; password: string; name: string; age?: number; address?: Address; }
function createUser(data: UserData) { /* ... */ }
```

### S5 → move method to data owner

```ts
// Before: Order.calculateDiscount(user) reads user.membershipLevel / user.accountAge
class User {
  getDiscountRate(orderTotal: number): number {
    if (this.membershipLevel === 'gold') return 0.2;
    if (this.accountAge > 365) return 0.1;
    return 0;
  }
}
// After: Order.calculateDiscount(user) → this.total * user.getDiscountRate(this.total)
```

### S6 → value object

```ts
class Email {
  private constructor(public readonly value: string) {}
  static create(value: string): Email {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) throw new Error('Invalid email');
    return new Email(value);
  }
}
```

Only when the type carries invariants/behavior — never wrap for wrapping's sake.

### S7 → named constants

```ts
const USER_STATUS = { ACTIVE: 1, INACTIVE: 2, SUSPENDED: 3 } as const;
const ONE_DAY_MS = 24 * 60 * 60 * 1000;
if (user.status === USER_STATUS.INACTIVE) { /* ... */ }
```

### S8 → guard clauses

```ts
function process(order: Order | null) {
  if (!order) return { error: 'No order' };
  if (!order.user) return { error: 'No user' };
  if (!order.user.isActive) return { error: 'User inactive' };
  if (order.total <= 0) return { error: 'Invalid total' };
  return processOrder(order);
}
```

Many independent validations → collect errors via a validator list (below), not deeper nesting.

### S10 → ask, don't tell

```ts
// Before: order.user.profile.address.street
// After:  order.getShippingAddress()
```

## Type safety (supports Pattern 9)

Narrowing ladder stays in [detection.md](detection.md) (`any` remediation). Typing pass example:

```ts
type Membership = 'bronze' | 'silver' | 'gold';

interface DiscountResult { original: number; discount: number; final: number; rate: number; }

function calculateDiscount(user: User, total: number, date: Date = new Date()): DiscountResult {
  if (total < 0) throw new Error('Total cannot be negative');
  let rate = 0.1;
  if (user.membership === 'gold' && date.getDay() === 5) rate = 0.25;
  else if (user.membership === 'gold') rate = 0.2;
  else if (user.membership === 'silver') rate = 0.15;
  const discount = total * rate;
  return { original: total, discount, final: total - discount, rate };
}
```

Never mechanical — `any→unknown` only after downstream usage review. Public-API type changes trigger Re-scan expansion (exports, call sites).

## Structural patterns (sparingly)

Introduce only when a confirmed finding shows the branch/chain set actually varies; indirection must pay for itself. Otherwise prefer the catalog fixes above.

**Strategy** — replace a growing conditional on type/kind:

```ts
interface ShippingStrategy { calculate(order: Order): number; }
class StandardShipping implements ShippingStrategy { calculate(o: Order) { return o.total > 50 ? 0 : 5.99; } }
class ExpressShipping implements ShippingStrategy { calculate(o: Order) { return o.total > 100 ? 9.99 : 14.99; } }
// call site: strategy.calculate(order)
```

**Validator list** — replace inline error accumulation:

```ts
type Validator = (u: User) => string | null;
const validators: Validator[] = [requireEmail, validEmailFormat, requireName, adultAge, allowedCountry];
const errors = validators.map(v => v(user)).filter((e): e is string => e !== null);
```

Full Chain-of-Responsibility class hierarchy only when validators must short-circuit or be composed dynamically at runtime.

Risk: pattern introductions restructure call sites → **medium+**; require evidence + validation per SKILL.md Risk table.

## Safe process (maps to SKILL.md Workflow 5–9)

```
1 PREPARE   tests exist (add focused ones if missing) · record pre-execution baseline
2 IDENTIFY  confirmed finding → smallest fix from catalog
3 REFACTOR  one small change → validate → next (scope grows → stop: change budget)
4 VERIFY    narrowest repo command · behavior-sensitive → semantic review of call sites
5 CLEAN UP  update touched comments/docs · re-scan affected pattern(s)
```

## Checklist (per remediation)

- **Code:** functions small & single-purpose · no duplicated blocks · descriptive names · no magic literals · dead code removed
- **Structure:** related code together · clear module boundaries · dependencies flow one direction · no circular deps
- **Types:** public APIs typed · no unjustified `any` · nullability explicit
- **Tests:** refactored code covered · edge cases included · all pass · no weakened assertions

## Operations quick reference

| Operation | Use when |
|-----------|----------|
| Extract Method | fragment becomes a named step |
| Extract Class/Module | responsibilities split |
| Extract Interface | depend on abstraction, not implementation |
| Inline Method / Inline Class | indirection no longer earns its cost |
| Pull Up / Push Down Method | inheritance reshell (rare in TS) |
| Rename Method/Variable | clarity only — zero behavior change |
| Introduce Parameter Object | S4 |
| Replace Conditional with Polymorphism | branch set varies by type (Strategy) |
| Replace Magic Number with Constant | S7 |
| Decompose / Consolidate Conditional | complex or duplicated conditions |
| Replace Nested Conditional with Guard Clauses | S8 |
| Introduce Null Object | repeated null checks on one collaborator |
| Replace Type Code with Class/Enum | S6/S7 |
| Replace Inheritance with Delegation | composition over inheritance |
