# AgencyDesk - System Design & Architecture

## 1. Multi-Tenancy & Tenant Isolation
AgencyDesk implements multi-tenancy at both the application and database query levels. 

* **Tenant Context**: Every API request (except public auth) requires an `X-Agency-ID` header, which identifies the active tenant context.
* **Database Isolation**: Tables (`projects`, `tasks`, `task_files`, `task_comments`, `time_entries`) contain an explicit `agency_id` column indexed for direct filtering.
* **Access Control Enforcement**: FastAPI dependency injection (`deps.get_current_agency`) validates that the user holds an active membership in the target agency. All SQL queries explicitly bind `WHERE agency_id = :active_agency_id`, preventing cross-tenant data leaks even if an attacker guesses valid resource UUIDs.

---

## 2. RBAC & Client Visibility Rules
We enforce a strict 3-tier Role-Based Access Control (RBAC) model:

1. **`agency_admin`**: Full administrative read/write access across all agency resources and client projects.
2. **`agency_member`**: Assigned project read/write access and time logging capabilities.
3. **`client_user`**: Guest portal access scoped strictly to their own client record.

### Blocking Internal Content from Clients
Tasks, comments, and file attachments carry a boolean `is_internal` flag. When the authenticated user has the `client_user` role, database queries across all endpoints dynamically append an additional condition:
```sql
AND is_internal = FALSE

```

This query-level enforcement guarantees that internal notes, design drafts, and internal tasks are filtered out at the database layer before reaching the client serializer.

---

## 3. Identity Model: Supporting One Person Across Multiple Agencies

Users log in with a single set of identity credentials (`users` table). Agency memberships are managed separately in a `memberships` table (`user_id`, `agency_id`, `role`).

* **Decoupled Identity & Tenant Role**: A single user account can have distinct roles across different tenants (e.g., `client_user` in Agency A and `agency_member` in Agency B).
* **Contextual Token Claims**: Switching agencies updates the active tenant context in local state and attaches the target `agency_id` to subsequent API calls, resolving the specific membership role dynamically for that request.

---

## 4. Handled Edge Case: Removing a Team Member Mid-Task

When an `agency_member` is removed from a project or agency:

* Their historic time entries (`time_entries`) remain intact for audit and project hour accounting.
* Assigned tasks (`tasks.assignee_membership_id`) are set to `NULL` (unassigned) via foreign key constraints (`ON DELETE SET NULL`), preventing orphaned task references while preserving task history and status.
