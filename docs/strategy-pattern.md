# Strategy Pattern (策略模式)

> Source: [初探設計模式 - 策略模式 (Strategy Pattern)](https://ithelp.ithome.com.tw/articles/10202506)  
> Author: Daniel Wu — 2019 iT 邦幫忙鐵人賽 Day 3

---

## Definition

The Strategy Pattern defines **a family of algorithms**, encapsulates each one behind a **common interface**, and makes them interchangeable at runtime.

> By swapping different strategies into an object, the object gains different behaviors without changing its own code. Composing strategies produces objects with varied behavior.

---

## Trade-offs

**Pros**
- Algorithms (behaviors) can be swapped flexibly at runtime
- Easy to extend — add a new strategy without touching existing code
- Eliminates chains of `if/else` or `switch` dispatching

**Cons**
- The caller must know which strategy to choose
- May proliferate many small strategy classes

> Tip: Combine with the Factory Pattern to remove the caller's burden of choosing a strategy — the factory encapsulates strategy selection.

---

## UML Structure

```
        ┌───────────────┐
        │   «interface» │
        │   IStrategy   │
        │───────────────│
        │ + execute()   │
        └───────┬───────┘
                │ implements
      ┌─────────┼─────────┐
      ▼         ▼         ▼
 StrategyA  StrategyB  StrategyC

        ┌───────────────┐
        │    Context    │◄── holds IStrategy
        │───────────────│
        │ setStrategy() │
        │ execute()     │
        └───────────────┘
```

---

## Example 1 — Calculator (Java)

A simple calculator where arithmetic operations are interchangeable strategies.

```java
// Strategy interface
public interface IStrategy {
    public int caculate(int a, int b);
}

// Concrete strategies
public class add implements IStrategy {
    @Override public int caculate(int a, int b) { return a + b; }
}
public class minus implements IStrategy {
    @Override public int caculate(int a, int b) { return a - b; }
}
public class multyply implements IStrategy {
    @Override public int caculate(int a, int b) { return a * b; }
}
public class divide implements IStrategy {
    @Override public int caculate(int a, int b) { return a / b; }
}

// Context — combines Strategy + Simple Factory
public class Calculator {
    private IStrategy strategy;

    public int execute(int a, int b) {
        return strategy.caculate(a, b);
    }

    public void setStrategy(DoType doType) {
        switch (doType) {
            case ADD:      this.strategy = new add();      break;
            case MINUS:    this.strategy = new minus();    break;
            case DIVIDE:   this.strategy = new divide();   break;
            case MULTYPLY: this.strategy = new multyply(); break;
        }
    }

    enum DoType { ADD, MINUS, DIVIDE, MULTYPLY }
}
```

Adding a new operation (e.g., exponentiation) only requires a new `IStrategy` implementation — no changes to `Calculator`.

---

## Example 2 — Transit Fare Calculator (Java)

A fare calculator where the pricing algorithm changes based on transport mode.

```java
public interface IStrategy {
    public int calculate(int km);
}

// Bus: flat-rate segments (≤10 km = 1 segment × $15, >10 km = 2 segments × $15)
public class BusStrategy implements IStrategy {
    @Override
    public int calculate(int km) {
        int count = (km <= 10) ? 1 : 2;
        return count * 15;
    }
}

// MRT: base $20 for ≤10 km, +$5 per additional 5 km (ceiling)
public class MRTStrategy implements IStrategy {
    @Override
    public int calculate(int km) {
        if (km <= 0) return 0;
        if (km <= 10) return 20;
        int count = (int) Math.ceil(((double)(km - 10)) / 5);
        return 20 + 5 * count;
    }
}

// Context
public class PriceCalculator {
    private IStrategy strategy;

    public PriceCalculator(IStrategy strategy) { this.strategy = strategy; }

    public void setStrategy(IStrategy strategy) { this.strategy = strategy; }

    public int calculate(int km) { return strategy.calculate(km); }
}
```

**Usage:**
```java
PriceCalculator calc = new PriceCalculator(new MRTStrategy());
System.out.println(calc.calculate(15)); // 25

calc.setStrategy(new BusStrategy());
System.out.println(calc.calculate(15)); // 30
```

---

## Relevance to This Codebase (secs4net / C#)

The Strategy Pattern appears implicitly in SECS-II message dispatch:

| Strategy Analogy | SECS-II Context |
|---|---|
| `IStrategy` interface | Per-message handler interface (e.g., `IMessageHandler<S1F1>`) |
| Concrete strategies | Individual `SxFy` handler implementations |
| Context (`Calculator`) | `ISecsGem` / `BackgroundService` dispatcher |
| Factory selection | DI container resolving the right handler by message type |

Instead of a giant `switch` on `(stream, function)`, each message type is an interchangeable handler registered via DI — matching the Strategy Pattern's intent exactly. See `docs/cslib/source/DeviceWorker.cs` for how the hosted service dispatches incoming primary messages.
