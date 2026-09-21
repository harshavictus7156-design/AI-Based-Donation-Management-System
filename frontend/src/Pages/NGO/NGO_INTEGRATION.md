# NGO frontend changes

This folder preserves the existing NGO visual language and adds a persistent NGO workspace shell.

## Add these routes to the existing App.jsx / router

Import:

```jsx
import NGOPageShell from "./Pages/NGO/NGOPageShell";
import NGODashboard from "./Pages/NGO/NGODashboard";
import { NGODonations, NGORequirements, NGOAllocations, NGOPickups, NGOAnalytics, NGOImpact, NGONotifications, NGOSettings } from "./Pages/NGO/NGOFeaturePages";
```

Then wrap each NGO route with the same shell:

```jsx
<Route path="/ngo-dashboard" element={<NGOPageShell><NGODashboard /></NGOPageShell>} />
<Route path="/ngo-donations" element={<NGOPageShell><NGODonations /></NGOPageShell>} />
<Route path="/ngo-requirements" element={<NGOPageShell><NGORequirements /></NGOPageShell>} />
<Route path="/ngo-allocations" element={<NGOPageShell><NGOAllocations /></NGOPageShell>} />
<Route path="/ngo-pickups" element={<NGOPageShell><NGOPickups /></NGOPageShell>} />
<Route path="/ngo-analytics" element={<NGOPageShell><NGOAnalytics /></NGOPageShell>} />
<Route path="/ngo-impact" element={<NGOPageShell><NGOImpact /></NGOPageShell>} />
<Route path="/ngo-notifications" element={<NGOPageShell><NGONotifications /></NGOPageShell>} />
<Route path="/ngo-profile" element={<NGOPageShell><NGOProfile /></NGOPageShell>} />
<Route path="/ngo-settings" element={<NGOPageShell><NGOSettings /></NGOPageShell>} />
```

Keep the existing `NGOProfile` import/component from your project.

## What changed

- Existing NGO dashboard theme is retained: navy/ivory/coral/green visual language, white cards, subtle borders and existing spacing style.
- Dashboard is now a clean overview only: welcome, 4 compact KPIs, two quick actions, and a small activity-at-a-glance row.
- NGO sidebar is persistent and uses the existing light/green visual direction rather than introducing a new dark theme.
- Requirements, Donations, Allocations, Pickups, Analytics, Impact, Notifications and Settings are separate pages.
- Non-dashboard pages show `← Back to Dashboard` in the shared shell.
- Existing API endpoints are reused: `ngo/donations/`, `ngo/requirements/`, `ngo/allocations/`, `pickup/ngo/`, and the existing donation status endpoint.
- No new backend endpoint is assumed.
