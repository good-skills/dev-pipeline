# AI Development Pipeline — راهنمای سریع

> یک سیستم سبک و قابل رهگیری برای مدیریت توسعه نرم‌افزار با AI Agentها؛ با هدف حفظ **Context، منطق کسب‌وکار، وابستگی‌ها، قراردادها و تاریخچه توسعه** در طول چرخه عمر محصول.

---

## نمای کلی

اسکیل `dev-pipeline` فرآیند توسعه را به مراحل مشخصی تقسیم می‌کند:

```text
┌──────────────┐
│    PLAN      │
│ /dev-pipeline│
└──────┬───────┘
       ↓
┌──────────────┐
│     TASK     │
│    PROMPT    │
└──────┬───────┘
       ↓
┌──────────────┐
│ IMPLEMENTER  │
│     AGENT    │
└──────┬───────┘
       ↓
┌──────────────┐
│    COMMIT    │
│   /commit    │
└──────┬───────┘
       ↓
┌──────────────┐
│    REVIEW    │
│ /review-task │
└──────┬───────┘
       ↓
    ┌──┴────┐
    ↓       ↓
  PASS     FAIL
    ↓       ↓
  DONE    REWORK
    ↓       ↓
  NEXT    R1 → R2 → ...
```

### اصل اصلی

> ** اسکیل `dev-pipeline` وظیفه برنامه‌ریزی و رهگیری توسعه را بر عهده دارد؛ یک Agent دیگر کد را پیاده‌سازی می‌کند؛ `/commit` تغییرات را ثبت می‌کند؛ و `/review-task` نتیجه را بررسی می‌کند و مشخص می‌کند Task کامل شده یا نیاز به اصلاح دارد.**

این تفکیک باعث می‌شود بتوان از **چند Agent، چند Session یا حتی چند ابزار مختلف** در یک فرآیند توسعه واحد استفاده کرد.

---

# 1. شروع یک پروژه جدید

برای ایجاد Pipeline در یک پروژه جدید:

```text
/dev-pipeline init <product-name>
```

مثال:

```text
/dev-pipeline init coffee-platform
```

این دستور ساختار اولیه مستندات و فایل‌های موردنیاز Pipeline را ایجاد می‌کند.

---

# 2. ایجاد Product Backlog

برای تحلیل محصول و تبدیل نیازمندی‌ها به ساختار قابل رهگیری:

```text
/dev-pipeline backlog
```

یا:

```text
/dev-pipeline plan
```

وظیفه Pipeline این است که باید محصول را به ساختاری مشابه زیر تبدیل کند:

```text
Product
   ↓
Epic
   ↓
Feature
   ↓
Dependencies
   ↓
Acceptance Criteria
```

این مرحله **فقط برای برنامه‌ریزی و مستندسازی است** و نباید کد محصول را پیاده‌سازی کند.

---

# 3. ایجاد یک Phase

هر Phase یک **بازه مسئولیتی مستقل در فرآیند توسعه** است.

برای ایجاد Phase:

```text
/dev-pipeline phase new <phase-name>
```

مثال:

```text
/dev-pipeline phase new frontend-mvp
```

برای ایجاد و فعال‌سازی هم‌زمان:

```text
/dev-pipeline phase new frontend-mvp --set-active
```

ساختار هر Phase:

```text
PH-01-frontend-mvp/
├── README.md
├── CONTEXT.md
└── TASK-QUEUE.md
```

یک Phase الزاماً معادل یک Git Branch نیست.

مثلاً می‌توان Phaseهای زیر را داشت:

```text
PH-01 → Frontend MVP
PH-02 → Backend API
PH-03 → Authentication
PH-04 → Integrations
```

---

# 4. جابه‌جایی بین Phaseها

برای مشاهده وضعیت Phaseها:

```text
/dev-pipeline phase status
```

برای فعال کردن Phase دیگر:

```text
/dev-pipeline phase switch PH-02
```

Phase قبلی حذف نمی‌شود؛ بلکه به حالت `parked` می‌رود:

```text
PH-01 active
      ↓
PH-01 parked
      +
PH-02 active
```

بعداً می‌توان آن را دوباره فعال کرد:

```text
/dev-pipeline phase switch PH-01
```

### نکته مهم

هنگام جابه‌جایی بین Phaseها:

-  ***نباید*** آیدی ها (ID) تغییر کنند.
    
- ***نباید*** Taskهای قبلی حذف شوند.
    
-  ***نباید*** Acceptance Criteria قبلی بازنویسی شوند.
    
-  ***نباید*** تاریخچه توسعه از بین برود.
    
-  ***نباید*** Contractها به‌صورت مخفیانه Breaking Change پیدا کنند.
    

---

# 5. مشاهده وضعیت Pipeline

برای مشاهده وضعیت کلی:

```text
/dev-pipeline status
```

این دستور اطلاعاتی مانند موارد زیر را نشان می‌دهد:

- فاز (Phase) فعال
    
- وضعیت Epicها
    
- وضعیت Featureها
    
- تسک (Task) های آماده
    
- بلاک کننده (Blocker) ها
    
- الویت (Priority) ها
    
- وابستگی‌ها
    

---

# 6. دریافت Task بعدی

برای اینکه Pipeline مناسب‌ترین Task بعدی را انتخاب کند:

```text
/dev-pipeline next
```

فرآیند انتخاب به‌صورت کلی:

```text
Active Phase
     ↓
Ready Tasks
     ↓
Dependencies
     ↓
Priority
     ↓
Next Task
```

در هر بار اجرا فقط **یک Prompt** تولید می‌شود.

فایل Prompt معمولاً در مسیر زیر قرار می‌گیرد:

```text
agent-prompts/TASK-....md
```

این فایل برای تحویل مستقیم به Implementer Agent آماده است.

---

# 7. درخواست یک Task مشخص

اگر می‌خواهید Task مربوط به یک Feature مشخص تولید شود:

```text
/dev-pipeline task <FEATURE-ID>
```

مثال:

```text
/dev-pipeline task ASK-01
```

پرامپت تولیدشده باید اطلاعات کافی برای اجرای مستقل Task را داشته باشد، از جمله:

- کانتکست محصول
    
- وضعیت فعلی
    
- تغییرات موردنیاز
    
- موارد خارج از Scope
    
- وابستگی‌ها
    
- قرارداد (Contract) ها
    
- معیار های پذیرش (Acceptance Criteria)
    
- تعریف کار انجام شده (Definition of Done)
    
- روش اعتبار سنجی  (Validation)
    

---

# 8. تحویل Task به Implementer Agent

فایل تولیدشده را به Agent پیاده‌ساز بدهید:

```text
agent-prompts/TASK-ASK-01-01.md
```

این Agent می‌تواند مثلاً: Cursor، Claude، Bolt یا هر Agent دیگری باشد.


هر Agent باید **فقط Task مشخص‌شده را پیاده‌سازی کند** و از انجام تغییرات خارج از Scope خودداری کند.

> پایپ لاین (Pipeline) مسئول برنامه‌ریزی و رهگیری است؛ Implementer مسئول پیاده‌سازی کد است.

---

# 9. کامیت کردن تغییرات

پس از پایان پیاده‌سازی:

```text
/commit
```

کامیت باید فقط تغییرات مربوط به همان Task را شامل شود.

نکته مهم:

```text
Implementation ≠ Done
```

پیاده‌سازی به‌تنهایی به معنی تکمیل Task نیست.

چرخه صحیح:

```text
Implementation
      ↓
Commit
      ↓
Review
      ↓
PASS
      ↓
DONE
```

---

# 10. Review کردن Task

پس از Commit:

```text
/review-task TASK-ASK-01-01
```

اگر Task موردنظر از Context قابل تشخیص باشد:

```text
/review-task
```

نیز قابل استفاده است.

بازنگری (Reviewer) تغییرات را در برابر **Task Prompt اصلی** بررسی می‌کند.

موارد اصلی بررسی:

```text
Acceptance Criteria
        +
Definition of Done
        +
Scope
        +
Dependencies
        +
Contracts
        +
Build / Tests
        +
Phase Invariants
        +
Secrets
```

هدف از Review این نیست که صرفاً کد را «خوب یا بد» ارزیابی کند؛ بلکه باید مشخص کند آیا **Task دقیقاً همان چیزی که تعریف شده بود را انجام داده است یا خیر.**

---

# 11. نتیجه Review

بازنگری (Review) می‌تواند یکی از سه نتیجه زیر را داشته باشد:

```text
PASS
FAIL
PARTIAL
```

## قبول شدن (PASS)

اگر تمام معیارهای پذیرش (Acceptance Criteria) رعایت شده باشند:

```text
TASK
 ↓
DONE
 ↓
NEXT TASK
```

باز نگری (Reviewer):

1. تسک را `done` می‌کند.
    
2. در صورت نیاز وضعیت Feature را به‌روزرسانی می‌کند.
    
3. پرامپت مربوط به Task بعدی را ایجاد می‌کند.
    

---

## عدم موفقیت (FAIL / PARTIAL)

اگر Task کامل نباشد، Pipeline نباید مستقیماً به Task بعدی برود.

```text
TASK-ASK-01-01
       ↓
      FAIL
       ↓
TASK-ASK-01-01-R1
```

یک Rework Prompt ایجاد می‌شود:

```text
agent-prompts/TASK-ASK-01-01-R1.md
```

این Prompt باید فقط مشکلات و اصلاحات موردنیاز را مشخص کند.

---

# 12. انجام اصلاحیه (Rework)

پرامپت اصلاحیه را دوباره به Implementer Agent بدهید:

```text
agent-prompts/TASK-ASK-01-01-R1.md
```

پس از اصلاح:

```text
/commit
```

و سپس:

```text
/review-task TASK-ASK-01-01
```

در صورت ادامه داشتن مشکل، زنجیره می‌تواند ادامه پیدا کند:

```text
TASK-ASK-01-01
       ↓ FAIL
TASK-ASK-01-01-R1
       ↓ FAIL
TASK-ASK-01-01-R2
       ↓ PASS
      DONE
```

محتوای تسک اصلی را بازنویسی نکنید

تسک اصلی باید بخشی از تاریخچه توسعه باقی بماند.

هر اصلاحیه باید با یک ID جدید و قابل رهگیری ثبت شود.

---

# 13. سیستم IDها

آیدی (ID) ها باید کوتاه، پایدار و برای انسان و Agent قابل فهم باشند.

### فاز (Phase)

```text
PH-01
```

### اپیک (Epic)

```text
EPIC-ASK
```

### ویژگی (Feature)

```text
ASK-01
```

### تسک (Task)

```text
TASK-ASK-01-01
```

یعنی Task شماره `01` مربوط به Feature `ASK-01`.

### اصلاحیه (Rework)

اولین اصلاحیه Task.
```text
TASK-ASK-01-01-R1
```


دومین اصلاحیه Task.
```text
TASK-ASK-01-01-R2
```


---

# 14. وضعیت‌ها

## وضعیت Phase

```text
intake
active
parked
done
```

### حالت `intake`

فاز در حال آماده‌سازی و شکل‌دهی است.

### حالت `active`

فاز فعلی توسعه است.

### حالت `parked`

فاز موقتاً متوقف شده ولی توسعه آن هنوز تمام نشده است.

### حالت `done`

اهداف Phase تکمیل شده‌اند.

---

## وضعیت Task

```text
todo
ready
in_progress
blocked
partial
done
cancelled
superseded
```

مهم‌ترین وضعیت‌ها:

| Status        |                       معنی                       |
| ------------- | :----------------------------------------------: |
| `todo`        |                  هنوز شروع نشده                  |
| `ready`       |        تمام Dependencyهای لازم آماده‌اند         |
| `in_progress` |           Task به Agent تحویل داده شده           |
| `blocked`     | به دلیل Dependency یا تصمیم دیگری قابل اجرا نیست |
| `partial`     |       بخشی از کار انجام شده ولی کامل نیست        |
| `done`        |            Review با موفقیت انجام شده            |
| `cancelled`   |               دیگر انجام نخواهد شد               |
| `superseded`  |          با مورد دیگری جایگزین شده است           |

---

# 15. وابستگی (Dependency)ها

برای مشخص کردن ارتباط بین Taskها و Featureها از موارد زیر استفاده می‌شود:

```text
depends_on
co_req
blocks
blocked_by
```

مثال:

```text
AUTH-01
   │
   └── blocks → USER-02
```

یعنی تا `AUTH-01` تکمیل نشود، `USER-02` نباید شروع شود.

این اطلاعات باعث می‌شود Agent مجبور نباشد Dependencyها را از روی کل پروژه حدس بزند.

---

# 16. قوانین اصلی Pipeline

## 1. آیدی (IDها) دائمی هستند

هرگز:

❌ آیدی را Rename **نکنید**
❌ آیدی را Renumber **نکنید**
❌ یک آیدی را دوباره استفاده **نکنید**


---

## 2. فاز متوقف‌شده را حذف نکنید

```text
active → parked
```

و بعداً:

```text
parked → active
```

---

## 3. قراردادها (Contract)ها را بی‌دلیل تغییر ندهید

***نباید*** API، DTO، Entity و سایر Contractهای مشترک بدون ثبت و هماهنگی تغییر کنند.

**باید** Breaking Change به‌صورت *صریح* در Pipeline ثبت شود.

---

## 4. بازنگری (Review) تعیین‌کننده تکمیل Task است

```text
Implementation ≠ Done
```

بلکه:

```text
Implementation
      ↓
Commit
      ↓
Review
      ↓
PASS
      ↓
DONE
```

---

## 5. تسک ناموفق نباید جلو برود

در صورت شکست:

```text
FAIL
 ↓
REWORK
 ↓
REVIEW
```

نه:

```text
FAIL
 ↓
NEXT TASK
```

---

## 6. مسئولیت Agentها جدا باشد

```text
/dev-pipeline
    ↓
Plan & Track

Implementer Agent
    ↓
Implement

/commit
    ↓
Commit

/review-task
    ↓
Review
```

این جداسازی اجازه می‌دهد توسعه بین Agentهای مختلف و Sessionهای مختلف ادامه پیدا کند، بدون اینکه Context پروژه از بین برود.

---

# 17. ساختار فایل‌ها

یک پروژه معمولاً ساختاری مشابه زیر خواهد داشت:

```text
docs/
├── PRODUCT.md
├── ARCHITECTURE.md
├── ROADMAP.md
│
├── epics/
│   └── EPIC-*.md
│
└── dev-pipeline/
    ├── PHASES.md
    │
    └── phases/
        └── PH-01-*/
            ├── README.md
            ├── CONTEXT.md
            └── TASK-QUEUE.md

agent-prompts/
└── TASK-*.md
```

در صورتی که پروژه از قبل مستندات یا ساختار مشابهی داشته باشد، Pipeline باید تا حد امکان از همان مستندات استفاده کند و Source of Truthهای موازی ایجاد نکند.

---

# 18. جریان کاری (Workflow) روزانه

اگر Pipeline قبلاً راه‌اندازی شده است، فرآیند معمول توسعه به این شکل است:

### 1. مشاهده وضعیت

```text
/dev-pipeline status
```

### 2. دریافت Task بعدی

```text
/dev-pipeline next
```

### 3. تحویل Prompt به Implementer Agent

```text
agent-prompts/TASK-....md
```

### 4. پیاده‌سازی

توسط Agent

### 5. کامیت (Commit)

```text
/commit
```

### 6. باز نگری (Review)

```text
/review-task TASK-...
```

### اگر PASS شد

```text
/dev-pipeline next
```

### اگر FAIL / PARTIAL شد

پرامپت اصلاحیه را به Agent بدهید:

```text
agent-prompts/TASK-...-R1.md
```

سپس:

```text
/commit
/review-task TASK-...
```

این چرخه تا PASS شدن Task ادامه پیدا می‌کند.

---

# 19. جابه‌جایی Context توسعه

ممکن است توسعه یک بخش از محصول متوقف شود و لازم باشد روی بخش دیگری کار شود.

مثلاً:

```text
PH-01 → Frontend
PH-02 → Backend
```

می‌توان Context را تغییر داد:

```text
/dev-pipeline phase switch PH-02
```

و بعداً به Phase قبلی برگشت:

```text
/dev-pipeline phase switch PH-01
```

قبل از ادامه یک Phase پارک‌شده، Pipeline باید وضعیت فعلی موارد زیر را بررسی کند:

- بررسی Context آن Phase
    
- بررسی Contractهای جدید
    
- بررسی Dependencyها
    
- بررسی Blockerها
    
- بررسی تغییرات انجام‌شده توسط Phaseهای دیگر
    

به این ترتیب توسعه می‌تواند بین بخش‌های مختلف محصول جابه‌جا شود، بدون اینکه Business Logic و Context پروژه از بین برود.

---

# جریان کاری (Workflow) در یک نگاه

```text
PLAN
  ↓
PHASE
  ↓
NEXT
  ↓
PROMPT
  ↓
IMPLEMENT
  ↓
COMMIT
  ↓
REVIEW
  │
  ├─────────────── PASS ──────────────→ DONE → NEXT
  │
  └──────────── FAIL / PARTIAL
                         ↓
                       REWORK
                         ↓
                     IMPLEMENT
                         ↓
                       COMMIT
                         ↓
                       REVIEW
```

---

# سه دستور اصلی

اگر فقط سه دستور را بخواهید به خاطر بسپارید:

### دریافت Task بعدی

```text
/dev-pipeline next
```

**تسک بعدی را پیدا و Prompt آن را تولید می‌کند.**

### ثبت تغییرات

```text
/commit
```

**پیاده‌سازی انجام‌شده را Commit می‌کند.**

### بررسی Task

```text
/review-task TASK-...
```

**مشخص می‌کند Task پذیرفته شده یا نیاز به Rework دارد.**

---

## چرخه اصلی

> **Plan → Implement → Commit → Review → Rework or Advance**

این چرخه، توسعه محصول با AI Agentهای متعدد را به یک فرآیند قابل رهگیری، قابل ادامه و قابل بررسی تبدیل می‌کند.
