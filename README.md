# AI Development Pipeline — راهنمای سریع

> بستهٔ اسکیل‌های Cursor برای **رهگیری توسعه با چند Agent**؛ هدف حفظ **Context، منطق کسب‌وکار، وابستگی‌ها، قراردادها و تاریخچه** در طول عمر محصول است — نه جایگزینی کدبیس با پرامپت‌های پراکنده.

**این ریپو:** اسکیل‌های قابل کپی به `.agents/skills/` یا Cursor skills. راهنمای عمیق انسان‌محور: [`dev-pipeline/README.md`](./dev-pipeline/README.md) (برای Agentها، `SKILL.md` مرجع است).

---

## اسکیل‌های این بسته

| پوشه | فعال‌سازی | نقش |
|------|-----------|-----|
| [`dev-pipeline/`](./dev-pipeline/) | `/dev-pipeline …` | برنامه‌ریزی و رهگیری محصول (فاز، backlog، brief، story، صف تسک) |
| [`promptize/`](./promptize/) | `/promptize …` | تبدیل درخواست کوتاه به مشخصات مهندسی (اختیاری `--execute`) |
| [`bug-report/`](./bug-report/) | `/bug-report …` | تبدیل توضیح طبیعی و یادداشت‌های خام به گزارش باگ ساختاریافته |
| [`commit/`](./commit/) | `/commit` | کامیت محدود به همان تسک |
| [`review-task/`](./review-task/) | `/review-task …` | PASS / FAIL / PARTIAL در برابر Task Prompt |
| [`clear-antipatterns/`](./clear-antipatterns/) | `/clear-antipatterns …` | اصلاح محافظه‌کارانه anti-patternهای TS |
| [`shared/`](./shared/) | — | قوانین مشترک (inspect، token-efficiency، SESSION-CACHE، Caveman انتخابی) |

### اصل اصلی

> **`/dev-pipeline` فقط برنامه‌ریزی و رهگیری می‌کند؛ Agent دیگر پیاده‌سازی می‌کند؛ `/commit` ثبت می‌کند؛ `/review-task` تعیین می‌کند تسک تمام شده یا نیاز به Rework دارد.**  
> **`/promptize` جایگزین `brief` / `story` / `backlog` / `adopt` نیست** — برای مشخصات عمیق مهندسی است.

---

## نمای کلی چرخه

```text
┌──────────────┐
│    PLAN      │  /dev-pipeline (init|adopt|brief|story|backlog|phase|next)
└──────┬───────┘
       ↓
┌──────────────┐
│ TASK PROMPT  │  agent-prompts/TASK-….md  (+ اختیاری /promptize)
└──────┬───────┘
       ↓
┌──────────────┐
│ IMPLEMENTER  │  Agent دیگر
└──────┬───────┘
       ↓
┌──────────────┐
│   /commit    │
└──────┬───────┘
       ↓
┌──────────────┐
│ /review-task │
└──────┬───────┘
       ↓
   PASS → DONE → /dev-pipeline next
   FAIL → Rework R1 → commit → review …
```

---

## شروع سریع

### پروژهٔ سبز (greenfield)

```text
/dev-pipeline init <product-name>
/dev-pipeline backlog
/dev-pipeline phase new <slug> --set-active
/dev-pipeline next
```

### پروژهٔ در حال توسعه (mid-flight)

```text
/dev-pipeline adopt
/dev-pipeline story extract          # اختیاری؛ استوری از کار تحویل‌شده
/dev-pipeline backlog                # در صورت نیاز، با تأیید کاربر
/dev-pipeline phase new … --set-active
/dev-pipeline next
```

### چرخهٔ روزانه (پس از راه‌اندازی)

```text
/dev-pipeline status
/dev-pipeline next
# → پیاده‌سازی با Agent روی agent-prompts/TASK-….md
/commit
/review-task TASK-…
# PASS → /dev-pipeline next   |   FAIL → Rework prompt → commit → review
```

---

## دستورهای مهم `/dev-pipeline`

| دستور | کاربرد |
|-------|--------|
| `init [name]` | بوت‌استرپ docs برای محصول جدید |
| `adopt` | اتصال پایپلاین به docs موجود (بدون پاک‌کردن SoT) |
| `brief [PH-…] …` | جذب توضیح فاز → قوانین/بک‌لاگ با dedup ادعاها |
| `story …` / `stories` | یوزر استوری محصول‌محور (`US-*`) + فلوها |
| `story extract` | استخراج استوری از فیچرهای پیاده‌شده |
| `backlog` / `plan` | اپیک / فیچر / وابستگی |
| `phase new` / `switch` / `status` | فازهای قابل پارک بدون شکستن ID |
| `shared` / `shared refresh` | شاخص قراردادهای مشترک |
| `surface new <slug>` | ثبت سرویس/سطح جدید روی همان SHARED |
| `next` / `task <FEATURE-ID>` | پرامپت تسک بعدی / مشخص |
| `status` | نمای فشرده فاز، صف، بلاکر |

پرچم‌های رایج: `--set-active`، `--phase`، `--promptize` (با `next`/`task`)، `--dry-run`، `--extract-stories`.

جزئیات: [`dev-pipeline/SKILL.md`](./dev-pipeline/SKILL.md).

---

## همراهان (companions)

| موقعیت | دستور |
|--------|--------|
| تسک صف نیاز به مشخصات عمیق دارد | `/promptize` بعد از `next`، یا `next --promptize` |
| کار ad-hoc خارج از صف | `/promptize` (اختیاری `--execute`) |
| پایان پیاده‌سازی | `/commit` |
| پس از کامیت | `/review-task` / `/review-task TASK-…` |

---

## قوانین پایدار (خلاصه)

1. **IDها دائمی‌اند** — rename / renumber / reuse ممنوع؛ `cancelled` / `superseded` بگیرید.
2. **فاز پارک‌شده را حذف نکنید** — `active ↔ parked`.
3. **قرارداد مشترک را بدون ثبت نشکنید** — SoT در `docs/dev-pipeline/SHARED.md` محصول هدف.
4. **Review تعیین‌کننده Done است** — `Implementation ≠ Done`.
5. **FAIL نباید به تسک بعدی بپرد** — Rework با `…-R1`، سپس review دوباره.
6. **مسئولیت Agentها جداست** — Pipeline ≠ Implementer ≠ Commit ≠ Review.

---

## شناسه‌ها (نمونه)

| نوع | الگو | مثال |
|-----|------|------|
| Phase | `PH-{NN}` | `PH-01` |
| Surface | `SUR-{NN}` | `SUR-01` |
| Epic | `EPIC-{SUFFIX}` | `EPIC-ASK` |
| Feature | `{SUFFIX}-{NN}` | `ASK-01` |
| Task | `TASK-{FEATURE}-{NN}` | `TASK-ASK-01-01` |
| Rework | `{TASK}-R{N}` | `TASK-ASK-01-01-R1` |
| User story | `US-{NNN}` / `US-…-F{NN}` | `US-001-F01` |

---

## ساختار docs در محصول هدف (طرح پیش‌فرض)

```text
docs/
├── PRODUCT.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── epics/
├── user-stories/          # SHARED — متعلق به یک سرویس نیست
├── business-rules/        # اختیاری
└── dev-pipeline/
    ├── PHASES.md
    ├── SHARED.md
    ├── ADOPTION.md        # پس از adopt
    └── phases/PH-…/
        ├── README.md
        ├── CONTEXT.md
        ├── TASK-QUEUE.md
        └── briefs/

agent-prompts/             # gitignored — پرامپت تحویل به Agent
```

اگر پروژه از قبل docs دارد، Pipeline باید **همان را گسترش دهد** و spine موازی نسازد. جزئیات: [`dev-pipeline/schema.md`](./dev-pipeline/schema.md).

---

## سه دستور که باید حفظ کنید

```text
/dev-pipeline next     → پرامپت تسک بعدی
/commit                → ثبت تغییرات همان تسک
/review-task TASK-…    → PASS یا Rework
```

### چرخه اصلی

> **Plan → Implement → Commit → Review → Rework or Advance**

این چرخه توسعه با چند Agent و چند Session را قابل رهگیری، قابل ادامه و قابل بررسی نگه می‌دارد.

---

## Single-file distribution

برای agentهایی که فقط یک Skill file می‌پذیرند:

| فایل | توضیح |
|------|-------|
| `promptize/SKILL.md` | **Canonical source** — multi-file architecture |
| `dist/single/promptize/SKILL.md` | **Generated** — single-file, self-contained |

### Build commands

```bash
npm run build:skill:promptize   # build single-file promptize
npm run build:skills            # alias for above
npm run build:check             # build + verify no drift
```

### Drift detection

`build:check` بعد از build، `git diff --exit-code dist/` اجرا می‌کند. اگر generated file قدیمی باشد، CI fail می‌شود.

### Token budget system

Promptize شامل token budget policies است:

- Context budgets (context, skill, retrieval, read, tool output, output, loop)
- Read budget (file size thresholds)
- Tool output budget (bounded results)
- Search budget (scoped excludes)
- Git budget (bounded inspection)
- Loop budget (max cycles before escalation)
- Retry policy (no blind retries)
