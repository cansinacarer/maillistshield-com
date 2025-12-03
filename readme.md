<p align="center">
    <img alt="MailListShield Logo" height="50" src="app/static/media/mail-list-shield-logo.png#gh-light-mode-only">
    <img alt="MailListShield Logo" height="50" src="app/static/media/mail-list-shield-logo-dark-mode.png#gh-dark-mode-only">
</p>
<p align="center">
    An email validation SaaS built with microservices architecture
</p>

<!-- Links -->
<p align="center">
    <a href="https://maillistshield.com"><img alt="Live Demo" src="https://img.shields.io/badge/Live%20Demo-blueviolet?logo=Google%20Chrome&logoColor=white"></a>
    <a href="https://documenter.getpostman.com/view/39218943/2sB3QDxDUr"><img alt="API Docs" src="https://img.shields.io/badge/API%20Docs-blue?&logo=read-the-docs&logoColor=white"></a>
    <a href="https://cansinacarer.github.io/My-Base-SaaS-Flask/"><img alt="Developer Docs" src="https://img.shields.io/badge/Developer%20Docs-blue?&logo=read-the-docs&logoColor=white"></a>
    <a href="https://deepwiki.com/cansinacarer/maillistshield-com"><img alt="DeepWiki" src="https://deepwiki.com/badge.svg"></a>
    <a href="https://www.producthunt.com/products/mail-list-shield?embed=true&utm_source=badge-featured&utm_medium=badge&utm_source=badge-mail&#0045;list&#0045;shield" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1045775&theme=light&t=1764802529738" alt="Mail&#0032;List&#0032;Shield - Remove&#0032;spam&#0032;traps&#0032;and&#0032;invalid&#0032;addresses&#0032;from&#0032;your&#0032;email&#0032;list | Product Hunt" style="height: 20px;" height="20" /></a>
</p>

<!-- Status -->
<p align="center">
    <a href="https://status.maillistshield.com/status/maillistshield"><img alt="Uptime" src="https://status.maillistshield.com/api/badge/5/uptime"></a>
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/cansinacarer/maillistshield-com?color=blue">
    <img alt="Test Coverage" src="tests/coverage/coverage-badge.svg">
    <a href="https://github.com/psf/black"><img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000"></a>
</p>

<!-- CI/CD -->
<p align="center">
    <a href="https://github.com/cansinacarer/maillistshield-com/actions/workflows/deploy.yml"><img alt="Build & Deploy" src="https://github.com/cansinacarer/maillistshield-com/actions/workflows/deploy.yml/badge.svg"></a>
    <a href="https://github.com/cansinacarer/maillistshield-com/actions/workflows/pre-commit.yml"><img alt="Pre-Commit Hooks" src="https://github.com/cansinacarer/maillistshield-com/actions/workflows/pre-commit.yml/badge.svg"></a>
    <a href="https://github.com/cansinacarer/maillistshield-com/actions/workflows/test.yml"><img alt="Run Tests" src="https://github.com/cansinacarer/maillistshield-com/actions/workflows/test.yml/badge.svg"></a>
    <a href="https://github.com/cansinacarer/maillistshield-com/actions/workflows/semantic-release.yml"><img alt="Semantic Release" src="https://github.com/cansinacarer/maillistshield-com/actions/workflows/semantic-release.yml/badge.svg"></a>
    <a href="https://github.com/cansinacarer/maillistshield-com/actions/workflows/docs.yml"><img alt="Build & Deploy Sphinx Docs" src="https://github.com/cansinacarer/maillistshield-com/actions/workflows/docs.yml/badge.svg"></a>
</p>

## Architecture

```mermaid
sequenceDiagram
  participant flask as 🌶️ 1. Flask Application
  participant db as 🐘 Postgres Database
  participant s3 as ☁️ S3 Bucket
  participant fis as 📁 2. File Intake Service
  participant f2vqp as 📤 3. File to Validation Queue Publisher
  participant rabbit as 🐰 RabbitMQ
  participant vo as ⚙️ 5. Validation Orchestrator
  participant evw as ✉️ 4. Email Validation Worker
  participant rfg as 📊 6. Results File Generator

  flask ->> s3: Uploads a batch validation job to validation/uploaded/
  flask ->> db: Records the job as pending_start
  s3 ->> fis: Clean up the file, calculate cost
  fis ->> db: Deduct credits from user, update status to file_accepted
  fis ->> s3: Upload cleaned file to validation/in-progress/
  s3 ->> f2vqp: Parse the cleaned file
  f2vqp ->> rabbit: Create a queue per file, publish each row as a message
  f2vqp ->> db: Update status to file_queued
  rabbit ->> vo: Consume N message per queue with Round-Robin
  vo ->> evw: API call to send each message, retrieve result
  vo ->> db: Update progress
  db ->> flask: Update progress in the UI
  vo ->> rabbit: Enqueue the results in each files' queue
  rabbit ->> rfg: Drain results queue of the file when expected message count is reached, build result file
  rfg ->> s3: Upload the result file to /validation/completed
  rfg ->> db: Set status to file_validation_in_progress or file_completed, save the name of the results file
  db ->> flask: Generate download link for results file
```

This application consists of 6 event driven services:

1. [Flask SaaS](https://github.com/cansinacarer/maillistshield-com) (this repository)
2. [File Intake Service](https://github.com/cansinacarer/maillistshield-file-intake-service)
3. [File to Validation Queue Publisher](https://github.com/cansinacarer/maillistshield-file-to-validation-queue-publisher)
4. [Email Validation Worker](https://github.com/cansinacarer/maillistshield-validation-worker)
5. [Validation Orchestrator](https://github.com/cansinacarer/maillistshield-validation-orchestrator)
6. [Results File Generator](https://github.com/cansinacarer/maillistshield-results-file-generator)

[See a more detailed architecture diagram →](https://app.diagrams.net/#Uhttps://raw.githubusercontent.com/cansinacarer/maillistshield-com/main/docs/drawio/mls-service-architecture.drawio)

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Flask |
| **Database** | PostgreSQL, SQLAlchemy ORM |
| **Message Queue** | RabbitMQ |
| **Infrastructure** | Docker, AWS S3, CapRover (PaaS deployment) |
| **Security** | OAuth 2.0, TOTP 2FA, reCAPTCHA, CSRF/XSS protection |
| **Observability** | Loki, Grafana, Uptime Kuma |
| **CI/CD** | GitHub Actions, Semantic Release |
| **Payments** | Stripe (subscriptions + one-time purchases) |

## Database Model

<details>
<summary>See the ER diagram</summary>

```mermaid
    erDiagram
        
        Users {
            int id PK
            string email
            string password
            string role
            string stripe_customer_id
            int tier_id FK
            bigint credits
            datetime cancel_at
            string firstName
            string lastName
            int newsletter
            datetime member_since
            datetime last_login
            string email_confirmation_code
            datetime last_confirmation_codes_sent
            int number_of_email_confirmation_codes_sent
            int email_confirmed
            string google_avatar_url
            boolean avatar_uploaded
            string totp_secret
            int totp_enabled
        }
        
        Tiers {
            int id PK
            string name
            string label
            string stripe_price_id
        }

        APIKeys {
            int id PK
            int user_id FK
            string key_hash
            string label
            datetime created_at
            datetime expires_at
            datetime last_used
            boolean is_active
        }

        BatchJobs {
            int id PK
            string uid
            int user_id FK
            string status
            string original_file_name
            string uploaded_file
            string accepted_file
            string results_file
            int row_count
            bigint last_pick_row
            datetime last_pick_time
            string source
            int header_row
            string email_column
            datetime uploaded
            datetime started
            datetime finished
            string result
        }

        Users }o--|| Tiers : "has"
        Users ||--o{ APIKeys : "owns"
        Users ||--o{ BatchJobs : "creates"
```

</details>

## Features of the Flask Application

### 🧑‍💻 Developer Experience

- Dev containers:

  - **Flask** container with pre-configured with:
    - VSCode launch.json for debugging the Flask app,
    - Prettier for HTML, CSS, and JS formatting,
    - Pre-commit hooks for code quality checks,
    - Markdownlint for Markdown formatting,
    - Black for Python code formatting,
    - Commitlint for commit message linting.

  - **Postgres** as a development database,

  - **pgAdmin** pre-connected to the development,

  - **docs** serving the built html files of the Sphinx documentation..

- CI/CD pipelines with GitHub Actions to:
  - Run pre-commit hooks,
  - Run tests,
  - Automate semantic release for versioning and changelog generation,
  - Build and deploy the documentation,
  - Build and deploy the app to production.

### ☁️ Deployment

- 🐳 Dockerized Flask for stateless continuous deployment for scalability,
- 🗄️ Database model abstracted with ORM,
- 📦 S3 object storage with pre-signed URLs.

### 💳 Stripe Integrations

- Subscriptions,
  - Different subscription tiers,
  - Billing page with Invoices,
  - Integration mechanism:
    - To begin a subscription, we send the user to Stripe with a checkout session,
    - Then listen to Stripe webhook events to process the results,
    - We set the Products in Stripe, then insert their prices into the Tiers table.

- One-off credit purchases for pre-paid metered usage.

### 🔒 Authentication

- Sign up flow,
  - Sign up with Google option,
  - Email validation requirement,

- Two factor authentication (TOTP only),
- Forgot password flow,
- reCAPTCHA v2 for sign up and login forms,
- Account details page where the user can:
  - Upload a profile picture (stored in S3),
  - Change profile details like first & last name.

### 📧 Transactional Emails with SMTP

- About Stripe subscription changes:
  - Confirmation,
  - Cancellation,
  - Expiration.

- Email verification on registration,
- Forgot password.

### 🚨 Security

- Cross-Site Request Forgery (CSRF) protection in all forms,
- Rate limiting: App-wide and form specific limits,
- Cross-Site Scripting (XSS) protection,
- Cross-Origin Resource Sharing (CORS) protection.
