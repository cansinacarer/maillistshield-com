# MailListShield.com SaaS

[![Build & Deploy](https://github.com/cansinacarer/maillistshield-com/actions/workflows/deploy.yml/badge.svg)](https://github.com/cansinacarer/maillistshield-com/actions/workflows/deploy.yml)

This repo contains the SaaS at [maillistshield.com](https://maillistshield.com/). It is built on top of [my Flask base saas](https://github.com/cansinacarer/my-base-saas-flask).

To pull updates from the base saas, connect it as an upstream:

```sh
git remote add upstream https://github.com/cansinacarer/my-base-saas-flask
```

Then you can fetch and merge:

```sh
git fetch upstream
git merge upstream/main
```

## Services

### 1. [Flask SaaS](https://github.com/cansinacarer/maillistshield-com)

The customer facing web application built with Flask. This has my [my base saas](https://github.com/cansinacarer/my-base-saas-flask) as an upstream repository. When I build a feature that is generally applicable and not specific to MailListShield, I build it in my base saas and pull them into this repository.

### 2. [File Intake Service](https://github.com/cansinacarer/maillistshield-file-intake-service)

This microservice runs a monitoring loop to check the `/validation/uploaded` directory on the S3 bucket and the `Jobs` table in the database for matching job records.

When a new file and a corresponding job is found, this service performs the following tasks:

- Remove all columns except email,
- Remove empty rows,
- Rename the email column as "Email",
- Count the rows and record it into the job record in the database,
- Deduct credits based on the record count in the cleaned up file,
- Create a standardized version of the file in `/validation/in-progress` in the S3 bucket.

This loop can be paused by setting an environment variable: `PAUSE=True`.

__Job States:__

- Expected before:
  - `pending_start`
- Error states
  - `error_too_old` : file deleted because it has been here too long
  - `error_df` : file could not be read
  - `error_column_count` : user did not select a column name but we detect more than 1 column
  - `error_insufficient_credits` :  User didn't have enough credits to process the file.
- Success state:
  - `file_accepted`

#### Clean up of orphan files

If a file is found but a corresponding job is not found, there is a retention period to allow for delays in database update. This retention period is declared in seconds with the environment variable `RETENTION_PERIOD_FOR_ORPHAN_FILES`. If there is no job record found in the database for a file found on the S3 bucket at the end of the retention period, the file is deleted.

### 3. [File to Validation Queue Publisher](https://github.com/cansinacarer/maillistshield-file-to-validation-queue-publisher)

This microservice monitors the S3 bucket for cleaned, standardized files. When a file is found, its rows are queued in a RabbitMQ Queue at `RABBITMQ_DEFAULT_VHOSTS[0]`. The queued files are moved to `validation/queued`.

__Job States:__

- Expected before:
  - `file_accepted`
- Interim states
  - `in_progress`
- Error states
  - `error_?`
- Success state:
  - `file_queued`

### 4. [Email Validation Worker](https://github.com/cansinacarer/maillistshield-validation-worker)

This service performs the email validation. It takes API requests with an API key and responds with the validation result JSON shown on the SaaS home page.

#### Deployment note for the validation worker

This service should be deployed in multiple servers in different IP blocks (preferably in different regions) because the success of the validation depends on the IP reputation determined by the email service providers. A worker in one server might return an unknown result while another instance that is deployed on a server with a different IP reputation can find a valid result.

The other services that use this worker can try multiple workers and use the best result.

__Job States:__

This service does not change the job state, because it only works with individual email addresses and is unaware of files.

### 5. [Validation Orchestrator](https://github.com/cansinacarer/maillistshield-validation-orchestrator)

This service monitors the results queues at vhost `RABBITMQ_DEFAULT_VHOSTS[1]` and when a queue at this vhost has the expected number of messages (i.e. `row_count` attribute of the queue), the messages from this queue are consumed and bundled into a final results file.

__Job States:__

This service does not change the job state in the database. The progress of a file is tracked using the number of messages in the queue for that file at vhost `RABBITMQ_DEFAULT_VHOSTS[1]`.

### 6. [Results File Generator](https://github.com/cansinacarer/maillistshield-results-file-generator)

This service monitors the results queues at vhost `RABBITMQ_DEFAULT_VHOSTS[1]`, and when a queue at this vhost has the expected number of messages (i.e. `row_count` attribute of the queue), the messages from this queue are bundled into the final results file.

__Job States:__

- Expected before:
  - `file_queued`
- Error states
  - `error_?`
- Success state:
  - `file_completed`

---

### [Initial Tests & Notes](https://github.com/cansinacarer/email-verification-test)

### [File Processor OLD](https://github.com/cansinacarer/maillistshield-scheduler)
