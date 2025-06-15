# Brainstorming: Lead Management System Enhancements

This document outlines potential feature ideas for enhancing the lead management prototype, focusing on historization, PLZ-based segmentation, lead selection optimization, and role-specific functionalities.

## 1. Lead Historization & Deduplication

**Context:** Currently, leads are sourced from a partner company. A key requirement is to avoid re-contacting leads multiple times within a given timeframe by remembering which leads were previously provided.

**Ideas:**

*   **Track Lead Assignment History:**
    *   Implement a system (likely new tables in the SQL Server database) to record every instance a lead is assigned.
    *   Key data points: `lead_id`, `assigned_to_user_id`, `assignment_date`, `office_id`, `status` (e.g., new, contacted, interested, converted, do_not_contact_until).
    *   Include a field for `source_batch_id` or `import_date` to track when a set of leads was received from the partner.
*   **Historize Lead Status Changes:**
    *   Track changes to a lead's status over time, providing a full audit trail.
*   **Deduplication Logic:**
    *   Before importing new leads from the partner, check against the historical assignment data.
    *   Flag or prevent re-import of leads that have been contacted or are under a "do not contact" period.
    *   This directly addresses the pain point of annoying prospects by contacting them too frequently.
*   **Benefits:**
    *   Prevents re-contacting leads inappropriately.
    *   Enables analysis of lead lifecycle and conversion patterns.
    *   Provides data for evaluating partner lead quality over time.

## 2. PLZ-Based Lead Segmentation for Offices

**Context:** Three independent offices (Luzern, Romandie, Egeli) must have strictly separated access to companies based on PLZ (postal codes).

**Ideas:**

*   **Add `PLZ` Field:**
    *   Ensure a `PLZ` (postal code) field is a core part of the lead data structure (e.g., in the main `Leads` table in SQL Server). The current `ort` (city) field is good, but PLZ is essential for precise routing.
*   **PLZ-to-Office Mapping:**
    *   Create a manageable system (e.g., a dedicated table in SQL Server or a section in a configuration file if mappings are static) to define PLZ ranges for each office.
    *   Example Mapping:
        *   Luzern: PLZs 6000-6999
        *   Romandie: PLZs 1000-2999, 3900-3999 (example, actual Swiss PLZs would be used)
        *   Egeli: All other PLZs not covered by Luzern or Romandie.
*   **Strict Data Separation in Application Logic:**
    *   **Filtering:** When a user logs in, their office affiliation (derived from their user profile) should automatically filter all lead views (dashboards, assignment lists, reports) to only show leads within their designated PLZs.
    *   **Assignment Restrictions:** Managers should only be able to assign leads to representatives within their own office or for PLZs their office is responsible for.
    *   **Database Queries:** All database queries retrieving leads must incorporate PLZ filters based on the user's office.
*   **New Lead Routing:**
    *   When new leads are imported, they should be automatically associated with the correct office based on their PLZ.

## 3. Lead Selection Optimization

**Context:** How can the company optimize the process of selecting which leads to pursue?

**Ideas:**

*   **Lead Scoring System:**
    *   Develop a scoring model based on available data points in your SQL Server database.
    *   Potential factors: `branche` (industry), `size_kategorie` (company size), location (PLZ/region), past interaction history (if available from historization), specific keywords in company descriptions (if you have that data).
    *   Scores could help prioritize high-potential leads.
*   **Prioritization Mechanisms:**
    *   Managers could use scores or other criteria (e.g., campaign focus) to manually prioritize leads for their teams.
    *   The system could automatically flag or sort leads by score on dashboards.
*   **Automated Lead Suggestions (Advanced):**
    *   For representatives, the system could suggest a "next best lead" based on:
        *   Lead score.
        *   Representative's past success with similar leads (industry, size).
        *   Current workload and capacity.
        *   Lead aging (how long a lead has been in the system unassigned or uncontacted).
*   **Feedback Loop for Continuous Improvement:**
    *   Representatives provide feedback on lead quality (e.g., "not interested - wrong segment," "data inaccurate," "already a customer").
    *   This feedback is stored and used to:
        *   Refine the lead scoring model.
        *   Provide feedback to the partner company on lead quality.
        *   Identify data hygiene issues.
*   **Integration with Sales Process:**
    *   Consider how lead selection aligns with defined sales stages or campaign objectives.

## 4. Role-Specific Features (Manager vs. Representative)

**Context:** Differentiate features for Managers and Representatives to support their distinct roles.

**A. Manager Role:**

*   **Comprehensive Dashboard:**
    *   Overview of lead distribution across all their managed offices/PLZ ranges.
    *   Key Performance Indicators (KPIs):
        *   Total leads assigned vs. available per office/representative.
        *   Conversion rates (e.g., contacted -> interested, interested -> customer) per rep/office.
        *   Contact rates.
        *   Lead aging reports.
    *   Visualization of lead pipeline health.
*   **PLZ-to-Office Management Interface:**
    *   If PLZ mappings are dynamic, provide a UI for managers (or a central admin) to update these mappings.
*   **Lead Import & Deduplication Management:**
    *   Interface for overseeing the import of new leads from the partner.
    *   Reviewing deduplication results and handling exceptions.
*   **Team Performance Management:**
    *   View individual representative performance metrics.
    *   Tools for reassigning leads if necessary (e.g., due to workload or absence).
*   **Advanced Filtering & Reporting:**
    *   Ability to generate custom reports on lead data, assignment history, and outcomes.
*   **User Management (for their office/scope):**
    *   Potentially, the ability to add/manage representative accounts within their designated office structure.

**B. Representative Role:**

*   **Personalized Dashboard:**
    *   Clear, prioritized list of assigned leads.
    *   Key details for each lead readily visible.
    *   Alerts for new assignments or aging leads needing attention.
*   **Efficient Lead Interaction Logging:**
    *   Simple forms to update lead status (e.g., contacted, meeting scheduled, proposal sent, won, lost).
    *   Log call notes, email summaries, and next steps.
    *   This data feeds into the historization and lead scoring systems.
*   **Access to Lead History:**
    *   View previous interactions with a lead (if any) by others in the company (respecting PLZ restrictions). This helps avoid awkward re-introductions.
*   **Calendar/Task Integration (Potential):**
    *   Links or integration to schedule follow-ups or tasks related to a lead.
*   **Personal Performance Indicators:**
    *   View their own conversion rates, activity levels, etc.
*   **Simplified Lead View:**
    *   Focus only on information relevant to contacting and qualifying the lead.

## 5. Data Handling and System Architecture

*   **Transition to SQL Server:**
    *   All above features presuppose moving from the current `data.py` mock data to a robust SQL Server backend.
    *   This involves:
        *   Designing appropriate database schemas for leads, users, assignments, history, PLZ mappings, etc.
        *   Implementing database connection logic in the Flask application.
        *   Using an ORM (like SQLAlchemy) or writing direct SQL queries for data manipulation and retrieval.
*   **Configuration Management:**
    *   Store database connection strings, office definitions (if not in DB), and other configurations securely (e.g., using environment variables or a more robust config solution than the current `config.yaml` for sensitive data).

This brainstorming provides a foundation for discussion and prioritization of features for the lead management system.
