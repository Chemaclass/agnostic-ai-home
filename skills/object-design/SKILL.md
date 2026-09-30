---
name: object-design
description: "Responsibility-driven OO design, with Object Calisthenics as detectors. Use when refactoring or reviewing domain code where services decide from getters, primitives carry rules, or collection logic repeats, or when asked for tell-don't-ask or an OO design review. Not for DTOs, adapters, ORM mappings, or hot paths."
---

# Object design

Goal: give each concept, decision, invariant, and collaboration the right home. Not many small classes. Not rule compliance.

Object Calisthenics rules are training weights: they expose where responsibility is misplaced. The discomfort of applying one is the signal. Read what it tells you, then decide with judgment.

## Symptom to look for

OO syntax, procedural design: data lives in objects, decisions live in a service that pulls the data out.

```java
if (order.getStatus().equals("PAID")
    && SUPPORTED.contains(order.getShippingAddress().getCountryCode()))
```

The caller knows the status representation, navigates the address structure, and owns the rule. Shape is a star: one service in the middle interrogating many passive objects.

Target shape is a neighborhood: each object answers questions about its own domain and delegates the rest.

```java
order.canBeShippedWith(policy)
```

## Rules as detectors

| Rule | What resisting it reveals |
|---|---|
| One level of indentation per method | Mixed abstraction levels; nested branch belongs in another object or method |
| No `else` | Premature nesting; guard clauses and early returns make valid paths visible |
| Wrap primitives and strings | Unprotected domain concept (`"PAID"` should be `OrderStatus`, `int grams` should be `Weight`) |
| First-class collections | Group behavior spread across callers (`List<Item>` should be `OrderLines`) |
| One dot per line | Caller navigating structure it should not know |
| No abbreviations | Name hides a distinction (`addr`: billing or shipping?) |
| Small entities | Responsibilities accumulating in one place |
| Max two instance variables | Missing value object or parameter object |
| No getters, setters, public properties | Decision made by the caller instead of the owner |

## Refactoring moves

Apply one at a time behind passing tests. Add characterization tests first if behavior is not covered.

1. **String/int with rules becomes a type.** Enum or value object that owns the rule: `OrderStatus.allowsShipping()`.
2. **Validate and normalize at construction.** `CountryCode` rejects `"ESP"` and lowercases once; `Weight` rejects negatives. Invalid values stop spreading.
3. **Replace type checks with polymorphism.** `OrderLine.canBeShipped()` implemented by `PhysicalOrderLine` and `DigitalOrderLine`. New variants become new classes, not new branches.
4. **Collection wrapper owns group behavior.** `OrderLines.canBeShipped()`: non-empty and all lines shippable.
5. **Configurable rules become a collaborator.** Hardcoded country set becomes `ShippingPolicy.accepts(destination)`.
6. **Move the decision to the owner.** `service.canShip(order)` becomes `order.canBeShippedWith(policy)`. Pass policies in; do not reach out for them.
7. **Keep construction separate.** Factories hide canonical setup; builders make variable setup readable. They are not part of the domain behavior.

## Tests as design feedback

Compare test shape before and after:

- `service.canShip(order("PAID", "ES", 100))`: test speaks in primitives, service interrogates.
- `order(PAID, "ES", new PhysicalOrderLine(new Weight(100))).canBeShippedWith(policy())`: test speaks the domain, object answers.

One reason to fail per test. Test factories and builders through the behavior of what they build, not by asserting constructor calls.

## Judgment

- Rules conflict with each other and with delivery. Treat them as probes, not a style guide.
- Check that a new class is a real domain concept. The two-field rule can invent groupings with no business meaning; if nobody in the domain would name it, reconsider.
- Keep use-case orchestration (transactions, I/O, notifications) out of entities. Entities decide domain questions; application services coordinate.
- Respect vertical slicing: introduce a type when the current change needs its rule or invariant, not speculatively for every primitive.
- Relax the rules for DTOs, read models, serialization, ORM mappings, framework adapters, performance-critical code, and deliberate fluent APIs.

## In a review

Report the misplaced responsibility, not the rule: "service decides shipping eligibility from order internals; move the decision into `Order`" beats "violates no-getters". Suggest the smallest move that relocates the decision.
