# **Project Development and Collaboration Guidelines**

This document aims to standardize the team's Git branch management, commit message formats, and development workflows, ensuring that frontend and backend development proceeds orderly and the code history remains clear and traceable.

## **1\. Core Branch Strategy**

This project follows a **split-stack development, unified merge** strategy, maintaining three core permanent branches:

| Branch Name | Description | Permissions |
| :---- | :---- | :---- |
| **main** | **Production Branch**. Contains stable code that is tested and ready for deployment at any time. | 🔒 Git Admin Merge Only |
| **frontend/dev** | **Frontend Development Branch**. Integration branch for all frontend features. | 🤝 Frontend Developers PR/MR Merge |
| **backend/dev** | **Backend Development Branch**. Integration branch for all backend features. | 🤝 Backend Developers PR/MR Merge |

## **2\. Branch Naming Convention**

When developing new features or fixing bugs, it is **strictly prohibited** to commit code directly to main or dev branches. You must create a temporary branch based on the corresponding dev branch.

**Format:** \[scope\]/\[type\]/\[description\]

### **Naming Rules Detail**

* **Scope:**  
  * frontend  
  * backend  
* **Type:**  
  * feat: New feature  
  * fix: Bug fix  
  * refactor: Code refactoring  
  * chore: Miscellaneous/Configuration changes  
* **Description:** Short English description, words separated by hyphens \-.

### **Correct Examples**

* Frontend login page: frontend/feat/login-page  
* Backend fix user API: backend/fix/user-api-error  
* Frontend refactor button component: frontend/refactor/button-component

## **3\. Commit Message Convention**

All commit messages must follow the **Conventional Commits** specification.

**Format:** type: subject

⚠️ Note: There must be a space after the colon.

### **Type Definitions**

| Type | Description | Example |
| :---- | :---- | :---- |
| **feat** | New feature | feat: add user profile page |
| **fix** | Bug fix | fix: resolve null pointer in auth service |
| **docs** | Documentation changes only | docs: update api documentation |
| **style** | Formatting changes (white-space, formatting, missing semi-colons, etc.) | style: format code with prettier |
| **refactor** | Code change that neither fixes a bug nor adds a feature | refactor: simplify data processing logic |
| **perf** | Performance improvement | perf: improve image loading speed |
| **test** | Adding missing tests or correcting existing tests | test: add unit tests for login component |
| **chore** | Changes to the build process or auxiliary tools | chore: update npm dependencies |

## **4\. Standard Workflow**

Please strictly follow these steps for daily development:

### **Step 1: Sync and Create Branch**

Pull the latest code from the corresponding dev branch based on your stack (frontend/backend) and create a new branch.

**Frontend Example:**

\# 1\. Checkout to frontend dev branch and pull updates  
git checkout frontend/dev  
git pull origin frontend/dev

\# 2\. Create your feature branch (following naming convention)  
git checkout \-b frontend/feat/my-new-feature

**Backend Example:**

\# 1\. Checkout to backend dev branch and pull updates  
git checkout backend/dev  
git pull origin backend/dev

\# 2\. Create your feature branch  
git checkout \-b backend/fix/api-issue

### **Step 2: Develop and Commit**

Write code on your branch and commit using the standard Commit Message format.

git add .  
git commit \-m "feat: complete user registration form layout"

### **Step 3: Push and Request Merge**

After development is complete, push the branch to the remote repository.

git push origin frontend/feat/my-new-feature

👉 **Action:** Create a **Pull Request (PR)** or **Merge Request (MR)** on the Git platform (GitLab/GitHub).

* **Source Branch:** Your feature branch (e.g., frontend/feat/xxx)  
* **Target Branch:** The corresponding dev branch (e.g., frontend/dev)

⛔ **Warning:** Cross-stack merging (e.g., merging a frontend branch into backend dev) is strictly prohibited. Developers are strictly prohibited from creating PRs directly to main.

## **5\. Release and Integration (Git Admin)**

When a development phase (e.g., Sprint) ends, and features are completed and tested, the **Git Admin** performs the final merge:

1. **Code Review:** Ensure code quality in frontend/dev and backend/dev.  
2. **Merge to Main Dev:**  
   * Merge frontend/dev into dev.  
   * Merge backend/dev into dev.
3. **Final Testing:** When it is confirmed that the dev branch is stable, merge dev into main.
4. **Tag & Release:** Create a Tag on the main branch and release the version.

## **6\. Self-Checklist**

Before committing code, please check:

* \[ \] Did I create the branch based on the correct dev branch?  
* \[ \] Does my branch name include the frontend/ or backend/ prefix?  
* \[ \] Does my Commit Message start with feat:, fix:, etc.?  
* \[ \] Did I request a merge to the corresponding dev branch (instead of main)?

## **7\. CI/CD pipeline**

The CI/CD pipeline will automatically run tests. **Frontend preview deployment** triggers when changes are merged into `frontend/dev` and `dev` branches.
**Frontend production deployment** and **Backend production deployment** triggers when changes are merged into `main`.
