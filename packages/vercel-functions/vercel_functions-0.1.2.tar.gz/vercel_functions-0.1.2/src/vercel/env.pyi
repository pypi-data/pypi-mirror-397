def __getattr__(key: str) -> str: ...

VERCEL: str
"""
An indicator to show that system environment variables have been exposed to your project's Deployments.
"""

CI: str
"""
An indicator that the code is running in a Continuous Integration environment.
"""

VERCEL_ENV: str
"""
The environment that the app is deployed and running on.
"""

VERCEL_TARGET_ENV: str
"""
The system or custom environment that the app is deployed and running on.
"""

VERCEL_URL: str
"""
The domain name of the generated deployment URL. The value does not include the protocol scheme.
"""

VERCEL_BRANCH_URL: str
"""
The domain name of the generated Git branch URL. The value does not include the protocol scheme.
"""

VERCEL_PROJECT_PRODUCTION_URL: str
"""
A production domain name of the project. We select the shortest production custom domain, or
vercel.app domain if no custom domain is available. Note that this is always set, even in preview
deployments. This is useful to reliably generate links that point to production such as OG-image
URLs. The value does not include the protocol scheme.
"""

VERCEL_REGION: str
"""
The ID of the Region where the app is running.
"""

VERCEL_DEPLOYMENT_ID: str
"""
The unique identifier for the deployment, which can be used to implement Skew Protection.
"""

VERCEL_PROJECT_ID: str
"""
The unique identifier for the project.
"""

VERCEL_SKEW_PROTECTION_ENABLED: str
"""
When Skew Protection is enabled in Project Settings, this value is set to 1.
"""

VERCEL_AUTOMATION_BYPASS_SECRET: str
"""
The Protection Bypass for Automation value, if the secret has been generated in the project's
Deployment Protection settings.
"""

VERCEL_GIT_PROVIDER: str
"""
The Git Provider the deployment is triggered from.
"""

VERCEL_GIT_REPO_SLUG: str
"""
The origin repository the deployment is triggered from.
"""

VERCEL_GIT_REPO_OWNER: str
"""
The account that owns the repository the deployment is triggered from.
"""

VERCEL_GIT_REPO_ID: str
"""
The ID of the repository the deployment is triggered from.
"""

VERCEL_GIT_COMMIT_REF: str
"""
The git branch of the commit the deployment was triggered by.
"""

VERCEL_GIT_COMMIT_SHA: str
"""
The git SHA of the commit the deployment was triggered by.
"""

VERCEL_GIT_COMMIT_MESSAGE: str
"""
The message attached to the commit the deployment was triggered by.
"""

VERCEL_GIT_COMMIT_AUTHOR_LOGIN: str
"""
The username attached to the author of the commit that the project was deployed by.
"""

VERCEL_GIT_COMMIT_AUTHOR_NAME: str
"""
The name attached to the author of the commit that the project was deployed by.
"""

VERCEL_GIT_PULL_REQUEST_ID: str
"""
The pull request id the deployment was triggered by. If a deployment is created on a branch
before a pull request is made, this value will be an empty string.
"""
