@echo off
echo ===================================================
echo   Pushing Fake News Detector to GitHub
echo ===================================================
echo.

echo [1/5] Initializing Git repository...
git init
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to initialize git repository.
    goto error
)
echo.

echo [2/5] Staging files...
git add .
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to stage files.
    goto error
)
echo.

echo [3/5] Configuring Git user identity and creating initial commit...
git config user.email "aj-techsoul@users.noreply.github.com"
git config user.name "aj-techsoul"
git commit -m "Initial commit"
if %ERRORLEVEL% neq 0 (
    echo.
    echo Warning: Nothing to commit or commit failed.
)
echo.

echo [4/5] Setting default branch to main and configuring remote...
git branch -M main
git remote remove origin >nul 2>&1
git remote add origin https://github.com/aj-techsoul/fakenewsdetector.git
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to configure remote origin.
    goto error
)
echo.

echo [5/5] Pushing to GitHub (main branch)...
echo Note: If GitHub prompts you for authentication, please sign in or provide your Personal Access Token.
echo.
git push -f -u origin main
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to push to GitHub.
    goto error
)

echo.
echo ===================================================
echo   SUCCESS: Code pushed to GitHub successfully!
echo ===================================================
goto end

:error
echo.
echo ===================================================
echo   ERROR: The process failed. See errors above.
echo ===================================================

:end
echo.
pause
