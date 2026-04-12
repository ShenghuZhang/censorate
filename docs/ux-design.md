# Censorate Management System - UX Design Document

## 1. Design Philosophy

**Minimalist Architectural Style** with high contrast, clean line-based separation, and focus on clarity over ornamentation.

### Typography
- **Font Family**: Manrope (Google Fonts)
- **Headings**: 700 weight, tighter letter-spacing
- **Body Text**: 400-500 weight
- **Captions/Labels**: 400 weight, smaller size, uppercase letter-spacing

### Color System
Low-saturation background tints with high-contrast foreground text for accessibility.

| Phase | Background | Text | Accent |
|-------|-----------|------|--------|
| New Requirement | `#F5F5F5` (Gray 100) | `#1A1A1A` | `#6B7280` |
| Analysis | `#FFF8ED` (Amber 50) | `#1A1A1A` | `#F59E0B` |
| Design | `#E0F2FE` (Blue 50) | `#1A1A1A` | `#0EA5E9` |
| Development | `#ECFDF5` (Emerald 50) | `#1A1A1A` | `#10B981` |
| Testing | `#F3E8FF` (Purple 50) | `#1A1A1A` | `#8B5CF6` |
| Completed | `#F0FDF4` (Green 50) | `#1A1A1A` | `#22C55E` |
| RETURNED | `#FEF2F2` (Red 50) | `#991B1B` | `#EF4444` |

## 2. Kanban Board Layout

### Structure
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Project: [Project Name] ▼  |  Type: [Technical/Non-Technical]       │
├─────────────────────────────────────────────────────────────────────────┤
│  [New] 112 ───►  [Analysis] 47  ───►  [Design] 23  ───►  [Dev] 89  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ REQ-0001        │  │ REQ-0002        │  │ REQ-0003        │      │
│  │ User login      │  │ API endpoints   │  │ Database schema  │      │
│  │ Priority: High  │  │ ↺ RETURNED      │  │                 │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│                                                                   ►     │
│  [Testing] 34  ───►  [Completed] 156                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                           │
│  │ REQ-0004        │  │ REQ-0005        │                           │
│  │ Test suite      │  │ Email service   │                           │
│  │ 3 tests pending │  │ ✓ Merged        │                           │
│  └─────────────────┘  └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Card Design
Each requirement card displays:
1. **REQ-ID** (top left, monospace, small) - persistent ID for traceability
2. **Title** (heading, truncate after 2 lines)
3. **Summary** (caption, truncate after 3 lines)
4. **Priority Badge** (High/Medium/Low)
5. **AI Status** (icon + label if AI processing)
6. **RETURNED Badge** (if dragged back, with ↺ icon)
7. **Progress Indicator** (for Dev/Testing lanes)
8. **Assignee Avatar** (bottom right, if assigned)

### Card Interactions
- **Click**: Expand to detail view
- **Drag**: Move between lanes (with confirmation for state changes)
- **Right-click**: Context menu (edit, duplicate, archive)
- **Hover**: Show quick actions (assign, comment, tag)

## 3. Lane Visibility

### Non-Technical Project Lanes
```
New Requirement → Analysis → Design → Completed
```

### Technical Project Lanes
```
New Requirement → Analysis → Design → Development → Testing → Completed
```

### Lane Transitions
- **Forward drag**: Opens confirmation dialog showing required AI checks
- **Backward drag** (The "Drag-Back" Rule):
  - Applies "RETURNED" tag
  - Shows ↺ arrow icon
  - Requires rejection reason input
  - Creates comment card automatically

## 4. State Transition UX

### AI First, Human Check Pattern

**Step 1: AI Processing (Automatic)**
- Show spinner with "AI analyzing..." message
- Display AI confidence score
- Show real-time progress for multi-step AI tasks

**Step 2: Human Confirmation (Required)**
```
┌─────────────────────────────────────────┐
│  Confirm Transition: Analysis → Design  │
├─────────────────────────────────────────┤
│  ✓ AI generated 3 sub-tasks            │
│  ✓ AI suggested 5 test cases          │
│  ✓ No duplicates detected              │
├─────────────────────────────────────────┤
│  [Review AI Suggestions]  [Confirm]     │
└─────────────────────────────────────────┘
```

**Step 3: Review UI (if selected)**
- Show AI-generated task breakdown
- Allow manual editing
- One-click approve all or approve individually

## 5. Data Drill-Down UX

### Development Lane Drill-Down
Clicking a card in Development lane expands to show sub-tasks:
```
┌─────────────────────────────────────────┐
│  REQ-0007: User Authentication System   │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │ ☑ TASK-001: Login endpoint       │  │
│  │    Status: In Progress          │  │
│  │    Assignee: @dev1              │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ ☐ TASK-002: Token validation     │  │
│  │    Status: Pending              │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ ☑ TASK-003: Session management   │  │
│  │    Status: Completed             │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  [+ Add Task]  [Generate AI Tasks]      │
└─────────────────────────────────────────┘
```

### Testing Lane Drill-Down
Many-to-many relationship visualization:
```
┌─────────────────────────────────────────┐
│  REQ-0012: Payment Processing          │
├─────────────────────────────────────────┤
│  Tasks (3)  →  Test Cases (7)           │
├─────────────────────────────────────────┤
│  TASK-045: Payment Gateway              │
│    ├─ TEST-001: Happy path ✓           │
│    ├─ TEST-002: Failure handling ✓      │
│    └─ TEST-003: Timeout recovery ⏳      │
│                                         │
│  TASK-046: Refund Processing             │
│    ├─ TEST-004: Full refund ✓          │
│    └─ TEST-005: Partial refund ✓         │
├─────────────────────────────────────────┤
│  [Generate Test Cases]  [Run Tests]     │
└─────────────────────────────────────────┘
```

## 6. Project Dashboard UX

### Project List View
```
┌────────────────────────────────────────────────────────────────┐
│  Projects                            [+ New Project]  [Search] │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  📊 E-Commerce Platform  [Technical]  Active  23d ago  │ │
│  │     Requirements: 89  |  In Progress: 45  |  Completed: 44 │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  📋 Marketing Campaign  [Non-Technical]  Active  5d ago │ │
│  │     Requirements: 12  |  In Progress: 8  |  Completed: 4 │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Project Detail Upgrades
**Non-Technical to Technical Upgrade:**
```
┌─────────────────────────────────────────┐
│  Upgrade to Technical Project            │
├─────────────────────────────────────────┤
│  This will add Development and Testing  │
│  lanes and enable GitHub integration.  .│
│                                         │
│  Link GitHub Repository:                 │
│  ┌───────────────────────────────────┐  │
│  │ organization/repo-name             │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [Cancel]  [Link Repository & Upgrade]  │
└─────────────────────────────────────────┘
```

## 7. Backlog & Intake Hub

### Intake Methods
1. **Feishu Integration**: Floating button with message icon
2. **WeChat Integration**: QR code setup modal
3. **File Upload**: Drag-and-drop zone

### Intake Form
```
┌─────────────────────────────────────────┐
│  New Requirement                         │
├─────────────────────────────────────────┤
│  Title: [_________________________]     │
│                                         │
│  Description:                           │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │                                   │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Priority: [High ▼]                     │
│  Source: [Select ▼]  (Feishu/WeChat/Direct)│
│                                         │
│  Attachments: [+ Add File]              │
│                                         │
│  [AI Analyze]  [Create Without AI]     │
└─────────────────────────────────────────┘
```

### AI Analysis Results
```
┌─────────────────────────────────────────┐
│  AI Analysis Complete                    │
├─────────────────────────────────────────┤
│  Confidence: 92%                        │
│                                         │
│  Duplicates Found:                      │
│  • REQ-0045: "User login" (85% match)   │
│                                         │
│  Suggested Tasks:                       │
│  1. Authentication endpoint              │
│  2. Session management                 │
│  3. Password reset flow                │
│                                         │
│  [Create as Duplicate]  [Create New]   │
└─────────────────────────────────────────┘
```

## 8. Automation Settings (No-Code Builder)

### Automation Builder UI
```
┌─────────────────────────────────────────┐
│  Automation Rules                        │
├─────────────────────────────────────────┤
│  [+ Create Rule]                         │
│                                         │
│  ┌Rule 1: Notify on High Priority──────┐ │
│  │ When: Priority changes to High     │ │
│  │ Then: Send Slack notification      │ │
│  │       to @engineering-lead          │ │
│  │ [Edit] [Delete]                    │ │
│  └─────────────────────────────────────┘ │
│                                         │
│  ┌Rule 2: Auto-assign─────────────────┐ │
│  │ When: Item enters Development     │ │
│  │ Then: Assign to @team-lead        │ │
│  │       if no assignee              │ │
│  │ [Edit] [Delete]                    │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Rule Builder Flow
```
Step 1: Trigger
┌─────────────────────────────────────┐
│ When: [Item enters lane ▼]         │
│       [Development]                 │
└─────────────────────────────────────┘
      [Next →]

Step 2: Conditions (Optional)
┌─────────────────────────────────────┐
│ If: [Priority ▼] [is] [High]       │
│     [+ Add Condition]                │
└─────────────────────────────────────┘
      [Next →]

Step 3: Actions
┌─────────────────────────────────────┐
│ Then: [Send notification ▼]        │
│      [Slack] to [@channel]         │
│      [+ Add Action]                 │
└─────────────────────────────────────┘
      [Save Rule]
```

## 9. Analytics Dashboard

### Cycle Time Chart
- X-axis: Time (weeks/months)
- Y-axis: Days
- Multiple lines per lane transition
- Hover shows detailed breakdown

### Cumulative Flow Diagram (CFD)
- Stacked area chart showing lane counts over time
- Color-coded by lane
- Ideal flow shown as faint reference line
- Bottlenecks highlighted when area expands

### Efficiency Metrics
```
┌─────────────────────────────────────────┐
│  Project Efficiency                     │
├─────────────────────────────────────────┤
│  Average Cycle Time: 12.3 days ↓ 15%    │
│  Throughput: 8.5 req/week ↑ 22%         │
│  Work in Progress: 45 items              │
│  Flow Efficiency: 78% ↑ 5%               │
├─────────────────────────────────────────┤
│  Bottleneck Detection:                   │
│  ⚠ Testing lane - average wait: 4.2 days│
└─────────────────────────────────────────┘
```

## 10. Archive View

### Archive Search
```
┌─────────────────────────────────────────┐
│  Search Archived Requirements            │
├─────────────────────────────────────────┤
│  [Search: ___________________]          │
│  Filter by: [Date Range ▼]  [Lane ▼]  │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │ REQ-0089: Email service          │  │
│  │ Completed: 2024-03-15            │  │
│  │ Cycle Time: 18 days              │  │
│  │ [View] [Restore] [Trace]        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Traceability View
```
┌─────────────────────────────────────────┐
│  Trace History: REQ-0089                │
├─────────────────────────────────────────┤
│  2024-02-25  Created                    │
│  2024-02-26  → Analysis (AI triage)     │
│  2024-03-01  → Design (by @user1)      │
│  2024-03-08  → Development              │
│  2024-03-12  → ↺ Analysis (rejected)   │
│  2024-03-14  → Development              │
│  2024-03-15  → Completed                │
├─────────────────────────────────────────┤
│  Total Cycle Time: 18 days               │
│  Rejection Count: 1                     │
└─────────────────────────────────────────┘
```

## 11. Notifications & Toast System

### Toast Types
- **Success**: Green checkmark, auto-dismiss 3s
- **Error**: Red X, auto-dismiss 5s, show details
- **Info**: Blue info icon, auto-dismiss 4s
- **AI Processing**: Spinner, persists until complete
- **Action Required**: Yellow warning, requires click

### Notification Center
```
┌─────────────────────────────────────────┐
│  Notifications (3)                      │
├─────────────────────────────────────────┤
│  🔔 REQ-0045 needs approval            │
│     Moved to Design lane               │
│     2 minutes ago  [Review]             │
│                                         │
│  ✓ AI analysis complete for REQ-0046    │
│     5 minutes ago                       │
│                                         │
│  ⚠ Potential duplicate: REQ-0047       │
│     Matches REQ-0023 (87%)             │
│     10 minutes ago  [Review]            │
└─────────────────────────────────────────┘
```

## 12. Accessibility & Responsive Design

### Accessibility Standards
- WCAG 2.1 AA compliance
- Keyboard navigation for all interactions
- Screen reader support with ARIA labels
- High contrast mode support
- Focus indicators on all interactive elements

### Responsive Breakpoints
- **Mobile** (< 640px): Single card view, horizontal scroll for lanes
- **Tablet** (640-1024px): 2-column layout, collapsible lanes
- **Desktop** (> 1024px): Full Kanban board, optimal experience

## 13. REQ-ID Traceability

### ID Pattern
- Format: `REQ-XXXX` where XXXX is incremental number
- Displayed in monospace font (SFMono-Regular, Consolas)
- Always visible on cards, detail views, and notifications
- Searchable via global search (Cmd+K)

### ID Quick Actions
- Click REQ-ID: Copy to clipboard
- Double-click: Open in new tab
- Hover: Show full history tooltip
