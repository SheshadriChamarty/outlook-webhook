# Test Email Templates

Use these email templates to test the Outlook webhook endpoint. Send these emails to the email address configured in your Outlook subscription.

## Test Email 1: HIGH Impact - Security Update (Recommended for Testing)

**Subject:**

```
URGENT: Workday Security Patch Required - Action Needed by Dec 15
```

**Body:**

```
Hello HRIT Team,

I wanted to bring to your attention a critical security update from Workday Community that requires immediate action.

Workday has announced a mandatory security patch that will be deployed on December 15, 2024. This patch addresses a vulnerability in the authentication module that could potentially expose employee data if not applied.

Key Details:
- Patch Release Date: December 15, 2024
- Impact: All production environments
- Action Required: Configuration update must be completed before deployment
- Affected Modules: HCM, Security, Integrations

This is a breaking change that will affect our existing SSO configuration. We need to update our integration settings and test in our sandbox environment before the production rollout.

Please review the Workday Community post and let me know if you need any additional information.

Best regards,
Sheshadri Chamarty
```

---

## Test Email 2: MEDIUM Impact - Feature Update

**Subject:**

```
Workday Community: New Payroll Reporting Feature Available Q1 2025
```

**Body:**

```
Hi Team,

I came across an interesting update in Workday Community about a new payroll reporting feature that will be available in Q1 2025.

The new feature includes:
- Enhanced payroll analytics dashboard
- Custom report builder for payroll data
- Real-time payroll reconciliation tools

This feature will require some configuration work on our end, including:
- Setting up new report templates
- Training the payroll team
- Testing in our sandbox environment

The feature is optional but could significantly improve our payroll reporting efficiency. I think it's worth evaluating for our team.

Let me know if you'd like to schedule a review meeting to discuss implementation.

Thanks,
Sheshadri Chamarty
```

---

## Test Email 3: LOW Impact - Informational

**Subject:**

```
Workday Community Newsletter - December Updates
```

**Body:**

```
Hello,

Just sharing the latest Workday Community newsletter highlights:

- New community forum features
- Upcoming webinars schedule
- Best practices articles
- User success stories

Nothing urgent here, just keeping you informed about what's happening in the Workday ecosystem.

Feel free to review when you have time.

Best,
Sheshadri Chamarty
```

---

## Test Email 4: Needs Review - Complex Issue

**Subject:**

```
Workday Integration Issue - Need Guidance on API Rate Limits
```

**Body:**

```
Hi HRIT Team,

We're experiencing some challenges with our Workday API integration and I'm hoping you can help.

The Issue:
- Our automated data sync process is hitting API rate limits
- Error messages indicate we're exceeding the 1000 requests per minute threshold
- This is affecting our nightly payroll data synchronization

Current Setup:
- We're using Workday REST APIs for employee data sync
- Running syncs every 4 hours
- Processing approximately 5000 employee records per sync

Questions:
1. Are there best practices for handling rate limits?
2. Should we implement retry logic with exponential backoff?
3. Is there a way to batch requests more efficiently?
4. Should we consider using Workday's bulk export features instead?

I've posted this in Workday Community but wanted to get your input as well. This is impacting our operations and we need to find a solution soon.

Appreciate your help!

Sheshadri Chamarty
```

---

## How to Test

1. **Send Email**: Send one of the above emails from `sheshadri.chamarty@gmail.com` to the email address configured in your Outlook subscription.

2. **Check Webhook**: The webhook endpoint `/email-webhook` should receive the notification.

3. **Verify Processing**: Check the logs to see:

   - Email received and parsed
   - Filtering classification (should not be "spam")
   - AI triage report generated
   - Auto-reply sent back to sender

4. **Check Response**: You should receive an auto-reply email with the AI-generated triage report.

---

## Expected Results

- **Test Email 1**: Should be classified as HIGH impact, Security module
- **Test Email 2**: Should be classified as MEDIUM impact, Payroll module
- **Test Email 3**: Should be classified as LOW impact, Informational
- **Test Email 4**: Should be classified as "needs_review" or "urgent"

All emails should receive an AI-generated triage report as a reply.
