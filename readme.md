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

### 2. [File Processor Service](https://github.com/cansinacarer/maillistshield-file-processor)

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

### 3. [Validation Queue Loader](https://github.com/cansinacarer/maillistshield-file-validator)

This microservice monitors the S3 bucket for cleaned, standardized files. When a file is found, its rows are queued in the RabbitMQ Queue #1.

__Job States:__

- Expected before:
  - `file_accepted`
- Interim states
  - `queued`
  - `in_progress`
- Error states
  - `error_?`
- Success state:
  - `file_queued`

### 4. [In progress] Results Queue Producer

This service consumes the individual validation tasks from the RabbitMQ Queue #1 and orchestrates email validation with the following tasks:

- Send the email to a worker, if the result is invalid, send it to the next worker.
- Queue the best result in RabbitMQ Queue #2.

__Job States:__

This service does not change the job state, because it only works with individual email addresses and is unaware of files.

### 5. [Email Validation Worker](https://github.com/cansinacarer/maillistshield-validation-worker)

This service performs the email validation.

#### Deployment note for the validation worker

This service should be deployed in multiple servers in different IP blocks (preferably in different regions) because the success of the validation depends on the IP reputation determined by the email service providers. A worker in one server might return an unknown result while another instance that is deployed on a server with a different IP reputation can find a valid result.

The other services that use this worker can try multiple workers and use the best result.

__Job States:__

This service does not change the job state, because it only works with individual email addresses and is unaware of files.

### 6. [In progress] Results File Generator

This service consumes the RabbitMQ Queue #2 and bundles the email validation results into a results file when all email addresses in a job (i.e. file uploaded) are validated.

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
