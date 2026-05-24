__PRD Addendum — v1\.1__

__Subscription Model & Monetisation Update__

This document updates the original PRD \(v1\.0\) with the finalised subscription model, pricing strategy, and App Store/Play Store launch requirements\.

__1\. Subscription Model \(Final\)__

The app operates on a two\-tier model — a full\-featured free trial followed by a single paid tier\. There are no ads on either tier\.

__Feature__

__🆓  Free Tier__

__⭐  Pro Tier \(Paid\)__

__Price__

₹0 — always free

₹49–₹99 / month \(TBD\)

__Trial Duration__

2 weeks full access from sign\-up date

Unlimited — no expiry

__Smart Scheduler__

✅  Full access for 2 weeks

✅  Unlimited

__Health Module__

✅  Full access for 2 weeks

✅  Unlimited

__Productivity Module__

✅  Full access for 2 weeks

✅  Unlimited

__Schedule View Range__

2 weeks ahead only

Unlimited — full future view

__Ads__

❌  No ads ever

❌  No ads ever

__After Trial Ends__

Modules locked — schedule view limited to 2 weeks only

N/A — full access maintained

*Note: The exact Pro price \(₹49 or ₹99/month\) will be finalised after user research\. Both price points will be A/B tested at launch\.*

__2\. What Happens After Free Trial Ends__

After 14 days, free users see a paywall screen when trying to access locked features\. The following rules apply:

- Smart Scheduler remains accessible but schedule view is capped at 2 weeks ahead
- Health Module is fully locked — user sees upgrade prompt
- Productivity Module is fully locked — user sees upgrade prompt
- All existing data is preserved — nothing is deleted if user does not upgrade
- User can upgrade at any time to instantly unlock everything

__3\. App Store & Play Store Requirements__

__3\.1  Google Play Store__

- In\-app subscriptions must use Google Play Billing API — no external payment links
- Subscription price must be set in Google Play Console in INR
- Requires a Privacy Policy URL publicly accessible before submission
- Requires a complete Data Safety form declaring what data is collected
- Free trial period must be clearly disclosed in the store listing

__3\.2  Apple App Store__

- In\-app subscriptions must use Apple StoreKit / In\-App Purchase API
- Apple takes 30% commission \(15% for small developers under $1M revenue\)
- Requires Privacy Policy URL and App Privacy labels filled in App Store Connect
- Free trial must be configured in App Store Connect — cannot be hardcoded
- Requires Apple Developer Account — $99/year \(approx ₹8,200/year\)

__3\.3  Required Before Submitting to Either Store__

- Privacy Policy — publicly hosted URL \(e\.g\. on your website or Notion\)
- Terms of Service — publicly hosted URL
- App icon — 1024x1024px PNG, no alpha channel
- Screenshots — minimum 3 per device size for each store
- Age rating completed — this app will be rated 4\+ / Everyone
- Data collection disclosure — declare: name, email, schedule data, health data

__4\. Revenue Projections \(Simple Estimate\)__

Based on ₹49/month Pro pricing and conservative conversion assumptions:

__Milestone__

__Total Users__

__Monthly Revenue \(₹49\)__

__Launch \(Month 1\)__

1,000

~₹9,800

__Early Growth \(Month 6\)__

10,000

~₹98,000

__Scale \(Month 12\)__

50,000

~₹4,90,000

__Target \(Year 2\)__

__1,00,000__

__~₹49,00,000/month__

*Assumes 20% free\-to\-paid conversion rate, which is realistic for a no\-ads, student\-focused product with a strong free trial\.*

__5\. Reclaim\.ai Features to Incorporate \(New Addition\)__

Based on competitive research, the following Reclaim\-inspired features should be added to the product roadmap:

- Flexible Habits — daily routines \(gym, prayer, meals\) that auto\-move around the schedule instead of being fixed
- Priority System — Class \(P1\) > Travel \(P2\) > Study \(P3\) > Meals \(P4\) — conflicts auto\-resolve by priority
- Smart Buffer Time — gaps between events that shrink automatically when calendar is tight
- Study Lock — protects study blocks from being overwritten by other events
- Weekly Stats Dashboard — summary of study hours, meals logged, free time, and productivity score

__End of Addendum — PRD v1\.1__

*Read alongside the original PRD v1\.0 document\.*

