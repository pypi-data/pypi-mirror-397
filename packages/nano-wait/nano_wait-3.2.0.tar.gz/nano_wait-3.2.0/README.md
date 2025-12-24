# 🧠 Adaptive Execution Engine — How Nano-Wait Thinks

Nano-Wait replaces blind delays with adaptive execution, combining system awareness and computer vision to automate safely in non-deterministic environments.

## 🚀 Quick Start (Read This First)

If you only read one section, read this.

### Adaptive Waiting (Drop-in Replacement for time.sleep)
```
from nano_wait import wait
wait(2.0)                 # safe default
wait(2.0, speed="fast")   # more aggressive
```
### Adaptive Waiting with Wi-Fi Awareness
```
wait(3.0, wifi_ssid="MyNetwork", speed="normal")
```
### Vision Mode (Screen Awareness)
```
from nano_wait.vision import VisionMode

vision = VisionMode(mode="observe")
vision.scan()
```
### Learn Mode (Visual Memory — No ML)
```
vision = VisionMode(mode="learn")
vision.mark_region("login_button")
```

That’s it.
Everything below explains why this works and how Nano-Wait thinks.

## 🗺️ Mental Model: How Nano-Wait Thinks

Nano-Wait is not a single mechanism.
It is a dual-system execution engine.

At runtime, it continuously executes:
```
observe → reason → wait → observe
```
Two Engines, One Decision

###  🔍 Vision Engine — What is happening?

- Reads the screen (OCR)

- Recognizes visual states

- Stores deterministic visual memory

- ⏱ Adaptive Waiting Engine — When is it safe to proceed?

- Observes CPU, memory, and network

- Estimates execution risk

- Adjusts wait duration dynamically

Vision answers what.
Adaptive Waiting answers when.

Only when both agree does execution advance.

## 1️⃣ The Core Problem: Time in Non-Deterministic Systems

Graphical automation runs in environments where:

CPU load fluctuates

Memory pressure changes

Network latency varies

Visual states appear asynchronously

The traditional approach:
```
time.sleep(t)
```

assumes:

“The system will be ready after exactly t seconds.”

This assumption fails in real systems.

Nano-Wait treats time as a variable, not a constant.

## 2️⃣ Design Philosophy: Observe First, Act Second

Nano-Wait follows one strict rule:

Never advance blindly. Advance only when conditions are favorable.

This is enforced by two cooperating engines:

### 🔹 Adaptive Waiting Engine

- Models system readiness

- Adjusts time dynamically

- Enforces safety bounds

### 🔹 Vision Engine

- Observes visual state

- Recognizes known patterns

- Enables early termination

- They do not compete — they cooperate.

## 3️⃣ Execution Risk (Intuition Before Math)

Nano-Wait reduces complexity to a single idea:

- Low risk → shorter waits

- High risk → longer waits

- Risk is measured, not guessed.

## 4️⃣ Hardware Performance Modeling (PC Score)

Nano-Wait samples:

- CPU utilization

- Memory utilization

- And normalizes them:
```
cpu_score = clamp(10 - CPU_usage / 10)
mem_score = clamp(10 - Memory_usage / 10)

pc_score = (cpu_score + mem_score) / 2
```

This produces:

- Smooth behavior

- No hard thresholds

- Stable timing decisions

## 5️⃣ Network Awareness (Wi-Fi Score)

If a Wi-Fi SSID is provided, Nano-Wait includes network stability.

| OS      | Source  |
| ------- | ------- |
| Windows | pywifi  |
| macOS   | airport |
| Linux   | nmcli   |


If unavailable, the system gracefully degrades.

## 6️⃣ With vs Without Wi-Fi
Local Mode
```
execution_risk = pc_score
```
Connected Mode
```
execution_risk = (pc_score + wifi_score) / 2
```
## 7️⃣ Speed: Controlled Aggressiveness
| Speed  | Meaning            |
| ------ | ------------------ |
| slow   | Conservative       |
| normal | Balanced           |
| fast   | Aggressive         |
| ultra  | High-risk, bounded |


Speed limits how fast Nano-Wait may move — not how long it waits.

## 8️⃣ Final Wait Calculation
```
wait_time = max(0.05, min(t / factor, t))
```

Guaranteed:

- Never under 50 ms

- Never over t

- Stable and monotonic

## 9️⃣ Vision + Learn Mode (No ML)

Learn Mode stores:

- Screen regions

- UI states

- Semantic markers

- Without machine learning.

This enables:

- Instant recognition

- Reproducible behavior

- Explainable automation

🔁 Closed Feedback Loop
```
observe → reason → wait → observe
```

Predictability inside uncertainty.

## 🧪 Proven at Scale

5,500+ downloads

50+ countries

Extensive internal test suites

## 🧠 Why No Heavy ML?

Automation requires:

Determinism

Debuggability

Interpretability

Nano-Wait uses rules + memory, adding ML only when controlled and explainable.

## 📌 In One Sentence

Nano-Wait is an execution engine that balances perception and time, combining adaptive waiting with computer vision to automate safely in non-deterministic systems.