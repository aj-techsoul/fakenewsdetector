/**
 * theme-engine.js — Theme Engine for FakeGuard AI
 * =================================================
 * Manages active document theme classes, updates state
 * via session endpoints, and persists preferences.
 */

const THEMES = ['midnight-blue', 'emerald-green', 'royal-purple', 'sunset-orange', 'crimson-red'];

function applyTheme(themeName) {
    if (!THEMES.includes(themeName)) {
        themeName = 'midnight-blue';
    }
    
    // Apply attribute to html element
    document.documentElement.setAttribute('data-theme', themeName);
    
    // Update theme selector if present
    const selector = document.getElementById('themeSelector');
    if (selector) {
        selector.value = themeName;
    }
}

// Handle Selector Changes
document.addEventListener('DOMContentLoaded', () => {
    const selector = document.getElementById('themeSelector');
    
    if (selector) {
        // Apply initial theme from markup
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'midnight-blue';
        selector.value = currentTheme;
        
        selector.addEventListener('change', (e) => {
            const selected = e.target.value;
            applyTheme(selected);
            
            // Sync with backend database if user is authenticated
            fetch('/auth/profile/theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ theme: selected })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(`Theme changed to ${selected.replace('-', ' ')}`, 'info');
                }
            })
            .catch(err => {
                console.error('Failed to sync theme preference:', err);
                // Keep local preference active
                localStorage.setItem('local-theme', selected);
            });
        });
    }
});
