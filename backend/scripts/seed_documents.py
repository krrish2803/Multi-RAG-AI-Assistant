"""Seed sample documents into the knowledge base."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.db.mongodb import init_db
from app.db.qdrant import init_qdrant
from app.models.document import IngestedDocument, SensitivityLevel
from app.ingestion.pipeline import IngestionPipeline

# Sample documents to create as text files if they don't exist
SAMPLE_DOCUMENTS = [
    {
        "filename": "company_policy.txt",
        "department": "company-wide",
        "sensitivity": "internal",
        "content": """COMPANY GENERAL POLICIES AND PROCEDURES

1. WORK HOURS AND ATTENDANCE
Standard work hours are 9:00 AM to 5:00 PM, Monday through Friday.
Flexible working arrangements are available with manager approval.
Remote work is permitted up to 3 days per week for eligible positions.
Employees must notify their manager if they will be absent or late.

2. CODE OF CONDUCT
All employees must maintain professional behavior at all times.
Discrimination, harassment, or bullying of any kind will not be tolerated.
Employees must report any violations of the code of conduct to HR.
Conflicts of interest must be disclosed to management immediately.

3. DATA SECURITY
All company data must be stored on approved systems only.
Employees must use strong passwords and enable two-factor authentication.
Sharing of login credentials is strictly prohibited.
Report any suspected data breaches to IT Security immediately.

4. COMMUNICATION POLICIES
Use company email for all business communications.
Internal messaging platform (Slack) should be used for team communication.
External communications must follow brand guidelines.
Sensitive information must not be shared via unencrypted channels.

5. EXPENSE REIMBURSEMENT
Business expenses must be pre-approved by the employee's manager.
Submit expense reports within 30 days of incurring the expense.
Receipts are required for all expenses over $25.
Corporate credit cards are available for frequent travelers.
"""
    },
    {
        "filename": "hr_benefits_guide.txt",
        "department": "hr",
        "sensitivity": "confidential",
        "content": """HR BENEFITS AND COMPENSATION GUIDE (CONFIDENTIAL)

1. HEALTH INSURANCE
The company offers comprehensive health insurance through Blue Cross Blue Shield.
Employees are eligible for health benefits after 30 days of employment.
The company covers 80% of individual premiums and 60% of family premiums.
Dental and vision coverage are included in the standard plan.
Annual deductible: $1,500 individual / $3,000 family.

2. RETIREMENT PLANNING
401(k) plan available through Fidelity Investments.
Company matches 100% of employee contributions up to 4% of salary.
Vesting schedule: 25% per year, fully vested after 4 years.
Roth 401(k) option available.
Financial advisory services provided at no cost.

3. PAID TIME OFF
New employees receive 15 days PTO per year.
PTO increases to 20 days after 3 years of service.
25 days PTO after 7 years of service.
11 paid company holidays per year.
5 sick days per year (separate from PTO).
Unlimited PTO available for senior leadership positions.

4. PARENTAL LEAVE
12 weeks paid parental leave for birthing parents.
8 weeks paid parental leave for non-birthing parents.
Leave can be taken within 12 months of birth or adoption.
Phase-back program available: reduced hours for first 4 weeks back.

5. SALARY BANDS (CONFIDENTIAL)
Junior: $60,000 - $85,000
Mid-level: $85,000 - $120,000
Senior: $120,000 - $165,000
Staff: $165,000 - $210,000
Principal: $210,000 - $280,000
Director: $250,000 - $350,000
VP: $300,000 - $450,000

6. PERFORMANCE REVIEWS
Performance reviews conducted bi-annually (June and December).
Merit increases effective January 1 each year.
Promotion cycles align with review periods.
360-degree feedback collected from peers and direct reports.
"""
    },
    {
        "filename": "engineering_standards.txt",
        "department": "engineering",
        "sensitivity": "internal",
        "content": """ENGINEERING STANDARDS AND PRACTICES

1. TECHNOLOGY STACK
Backend: Python (FastAPI), Go, Node.js
Frontend: React/Next.js with TypeScript
Database: PostgreSQL, MongoDB, Redis
Cloud: AWS (primary), Azure (secondary)
Containerization: Docker, Kubernetes
CI/CD: GitHub Actions, ArgoCD

2. CODE REVIEW PROCESS
All code changes require at least one peer review.
Critical systems require two reviewers including a senior engineer.
Pull requests must include tests for new functionality.
Code review turnaround time: 24 hours maximum.
Use conventional commit messages.

3. TESTING STANDARDS
Unit test coverage: minimum 80% for new code.
Integration tests required for all API endpoints.
End-to-end tests for critical user journeys.
Performance tests for high-traffic services.
Security scanning in CI pipeline (SAST/DAST).

4. DEPLOYMENT PRACTICES
Blue-green deployments for all production services.
Feature flags for gradual rollouts.
Canary deployments for high-risk changes.
Rollback procedure documented for each service.
Production deployments restricted to business hours.

5. INCIDENT RESPONSE
Severity levels: P1 (outage), P2 (degraded), P3 (minor), P4 (cosmetic).
P1 response time: 15 minutes, 24/7.
P2 response time: 1 hour during business hours.
Incident commander assigned for P1/P2 incidents.
Post-mortem required within 48 hours of P1/P2 incidents.
Blameless culture: focus on systems, not individuals.

6. ARCHITECTURE GUIDELINES
Microservices architecture with clear domain boundaries.
API-first design with OpenAPI specifications.
Event-driven communication for async workflows.
Circuit breakers for external service calls.
Structured logging with correlation IDs.
All services must be observable (metrics, logs, traces).
"""
    },
    {
        "filename": "q3_financial_report.txt",
        "department": "finance",
        "sensitivity": "restricted",
        "content": """Q3 2025 FINANCIAL REPORT (RESTRICTED - EXECUTIVE ACCESS ONLY)

REVENUE SUMMARY
Total Revenue: $47.3M (up 12% YoY)
Product Revenue: $32.1M (68% of total)
Services Revenue: $11.8M (25% of total)
Other Revenue: $3.4M (7% of total)

COST BREAKDOWN
Cost of Revenue: $18.9M (40% of revenue)
R&D Expenses: $12.1M (25.6% of revenue)
Sales & Marketing: $8.4M (17.8% of revenue)
G&A Expenses: $4.2M (8.9% of revenue)
Total Operating Expenses: $43.6M

PROFITABILITY
Gross Profit: $28.4M (60% margin)
Operating Income: $3.7M (7.8% margin)
Net Income: $2.9M (6.1% margin)
EBITDA: $5.2M (11% margin)

KEY METRICS
Annual Recurring Revenue (ARR): $142M
Customer Acquisition Cost (CAC): $12,400
Lifetime Value (LTV): $89,500
LTV/CAC Ratio: 7.2x
Net Revenue Retention: 118%
Monthly Churn Rate: 1.2%

CASH FLOW
Operating Cash Flow: $6.8M
Capital Expenditures: $2.1M
Free Cash Flow: $4.7M
Cash Position (end of Q3): $38.2M

OUTLOOK Q4 2025
Projected Revenue: $51.2M
Expected Operating Margin: 9.2%
Planned Headcount Addition: 25 positions
Major Initiatives: Product v3.0 launch, APAC expansion
"""
    },
    {
        "filename": "marketing_brand_guide.txt",
        "department": "marketing",
        "sensitivity": "public",
        "content": """MARKETING BRAND GUIDELINES

1. BRAND IDENTITY
Our brand represents innovation, trust, and accessibility.
Brand Promise: Empowering businesses through intelligent solutions.
Brand Voice: Professional yet approachable, confident but not arrogant.
Brand Values: Innovation, Integrity, Collaboration, Excellence.

2. LOGO USAGE
Primary logo must maintain clear space equal to the height of the logo mark.
Minimum logo size: 1 inch for print, 80 pixels for digital.
Do not stretch, rotate, or modify the logo in any way.
Approved logo colors: Blue (#2563EB), Dark (#0F172A), White (#FFFFFF).
Logo on dark backgrounds must use the white version.

3. COLOR PALETTE
Primary Blue: #2563EB
Dark Navy: #0F172A
Light Gray: #F1F5F9
Accent Green: #10B981
Warning Orange: #F59E0B
Error Red: #EF4444

4. TYPOGRAPHY
Headlines: Inter Bold, 32-48px
Subheadings: Inter SemiBold, 20-24px
Body: Inter Regular, 14-16px
Code: JetBrains Mono, 14px
Line height: 1.5x for body text, 1.2x for headlines.

5. SOCIAL MEDIA GUIDELINES
Post frequency: LinkedIn 3x/week, Twitter 5x/week, Instagram 2x/week.
Content mix: 40% educational, 30% product updates, 20% culture, 10% promotional.
Hashtag strategy: #EnterpriseAI #KnowledgeManagement #RAG #TechInnovation.
Response time to comments/messages: within 4 hours during business hours.

6. CAMPAIGN FRAMEWORK
Awareness: Blog posts, social media, PR, events.
Consideration: Webinars, case studies, whitepapers, demos.
Conversion: Free trials, sales outreach, ROI calculators.
Retention: Customer success stories, product updates, community events.
"""
    },
]


async def seed_documents():
    """Create and ingest sample documents."""
    settings = get_settings()
    client = await init_db(settings)
    qdrant_client = await init_qdrant(settings)

    pipeline = IngestionPipeline(settings)
    data_dir = "/app/data/sample_documents"
    os.makedirs(data_dir, exist_ok=True)

    print("Seeding sample documents...")

    for doc_info in SAMPLE_DOCUMENTS:
        # Check if document already exists
        existing = await IngestedDocument.find_one(
            IngestedDocument.filename == doc_info["filename"]
        )
        if existing:
            print(f"  Document '{doc_info['filename']}' already exists, skipping.")
            continue

        # Write content to file
        file_path = os.path.join(data_dir, doc_info["filename"])
        with open(file_path, "w") as f:
            f.write(doc_info["content"])

        # Create document record
        doc = IngestedDocument(
            filename=doc_info["filename"],
            file_type="txt",
            file_size=len(doc_info["content"].encode()),
            file_path=file_path,
            department=doc_info["department"],
            sensitivity=SensitivityLevel(doc_info["sensitivity"]),
            uploaded_by="seed@company.com",
            status="pending",
        )
        await doc.insert()

        # Run ingestion
        try:
            await pipeline.process(
                document_id=str(doc.id),
                file_path=file_path,
                filename=doc_info["filename"],
                department=doc_info["department"],
                sensitivity=doc_info["sensitivity"],
                uploaded_by="seed@company.com",
            )
            print(f"  Ingested: {doc_info['filename']} ({doc_info['department']}, {doc_info['sensitivity']})")
        except Exception as e:
            print(f"  Failed to ingest {doc_info['filename']}: {e}")

    print("\nSample documents seeded successfully!")
    client.close()
    await qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(seed_documents())
