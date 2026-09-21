import {
  NGODonations,
  NGORequirements,
  NGOAllocations,
  NGOPickups,
  NGOAnalytics,
  NGOImpact,
  NGONotifications,
  NGOSettings,
} from "./NGOFeaturePages";

export default function NGOWorkspacePage({ type }) {
  const pages = {
    donations: NGODonations,
    requirements: NGORequirements,
    allocations: NGOAllocations,
    pickups: NGOPickups,
    analytics: NGOAnalytics,
    impact: NGOImpact,
    notifications: NGONotifications,
    settings: NGOSettings,
  };

  const Page = pages[type];
  return Page ? <Page /> : null;
}
