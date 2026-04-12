# Censorate Management System - Technical Design Document (Claude Code Optimized)

## 1. System Overview
Censorate is an AI-native requirement management system organized by **Projects**. It leverages an "AI First, Human Check" philosophy to manage the lifecycle of requirements from intake to completion.

## 2. Core Architecture: Project-Based Namespacing
All entities (Requirements, Tasks, Test Cases) exist within a **Project** namespace.

### 2.1 Project Types
*   **Non-Technical Project**: Focused on business requirements and design.
    *   *Lanes*: New Requirement -> Analysis -> Design -> Completed.
*   **Technical Project**: Defined by the attachment of one or more **GitHub Repositories**.
    *   *Lanes*: New Requirement -> Analysis -> Design -> **Development** -> **Testing** -> Completed.

### 2.2 Project Evolution Rules
*   **Upgrade Path**: A Non-Technical Project can be upgraded to a Technical Project by linking a GitHub repository.
*   **Restriction**: A Technical Project **cannot** be downgraded to a Non-Technical Project once code repositories are linked (to preserve data integrity of dev/test assets).

## 3. Workflow Logic & Automation

### 3.1 AI-Human Collaboration (AI First, Human Check)
*   **AI Agent Role**: Automatically triages backlog items, detects duplicates, generates initial development task breakdowns, and suggests test cases.
*   **Human Role**: All state transitions (moving between lanes) and AI-generated content (schema updates, task lists) require manual confirmation or "Human Check" approval.

### 3.2 Rejection Logic (The "Drag-Back" Rule)
*   Requirements are rejected by dragging them back to a previous lane (e.g., from Design back to Analysis).
*   **Visual Indicator**: Items returned from a subsequent stage receive a "RETURNED" tag and arrow icon to signify rework.

### 3.3 Data Drill-Down
*   **Development Lane**: Supports expanding a single Requirement (REQ-ID) into multiple sub-tasks.
*   **Testing Lane**: Manages many-to-many relationships between Development Tasks and Test Cases.

## 4. Feature Modules
*   **Backlog & Intake Hub**: Direct integration with Feishu, WeChat, and file uploads.
*   **Automation Settings**: No-code builder for transition rules and notification triggers.
*   **Analytics**: Efficiency insights (Cycle time, CFD).
*   **Archive**: Permanent storage for completed requirements with full traceability.

## 5. UI/UX Principles (Censorate Management System)
*   **Minimalist Architectural Style**: High contrast, Manrope typography, clean line-based separation.
*   **Color-Coded Phases**: Low-saturation background tints for lanes (e.g., Amber for Analysis, Blue for Dev).
*   **Unique ID Traceability**: Every requirement is tracked via a persistent REQ-XXXX ID across all phases.

