/**
 * Google OAuth Integration for Meeting App
 * Handles OAuth flow and JWT token management
 */

class GoogleOAuthHandler {
    constructor(baseURL = '/api/accounts') {
        this.baseURL = baseURL;
        this.setupEventListeners();
    }

    /**
     * Initialize Google OAuth flow
     */
    async initGoogleAuth() {
        try {
            const response = await fetch(`${this.baseURL}/auth/google/init/`);
            const data = await response.json();
            
            if (data.auth_url) {
                // Redirect to Google OAuth
                window.location.href = data.auth_url;
            }
        } catch (error) {
            console.error('Error initiating Google OAuth:', error);
            this.showError('Failed to start Google authentication');
        }
    }

    /**
     * Handle OAuth callback and get JWT tokens
     */
    async handleOAuthCallback() {
        try {
            const response = await fetch(`${this.baseURL}/auth/google/callback/`);
            const data = await response.json();
            
            if (data.access && data.refresh) {
                // Store JWT tokens
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('user_data', JSON.stringify(data.user));
                
                this.showSuccess('Google authentication successful!');
                
                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = '/video/dashboard/';
                }, 1500);
                
                return data;
            } else {
                throw new Error(data.error || 'Authentication failed');
            }
        } catch (error) {
            console.error('OAuth callback error:', error);
            this.showError('Google authentication failed');
        }
    }

    /**
     * Check social account connection status
     */
    async getSocialAccountStatus() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                throw new Error('No access token');
            }

            const response = await fetch(`${this.baseURL}/auth/social/status/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to get social account status');
            }
        } catch (error) {
            console.error('Error getting social account status:', error);
            return null;
        }
    }

    /**
     * Disconnect Google account
     */
    async disconnectGoogle() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${this.baseURL}/auth/social/disconnect/google/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.showSuccess('Google account disconnected successfully');
                return true;
            } else {
                throw new Error('Failed to disconnect Google account');
            }
        } catch (error) {
            console.error('Error disconnecting Google account:', error);
            this.showError('Failed to disconnect Google account');
            return false;
        }
    }

    /**
     * Setup event listeners for OAuth buttons
     */
    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            // Google OAuth buttons
            const googleButtons = document.querySelectorAll('[data-oauth="google"]');
            googleButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.initGoogleAuth();
                });
            });

            // Check if we're on OAuth callback page
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('code') && window.location.pathname.includes('callback')) {
                this.handleOAuthCallback();
            }

            // Disconnect buttons
            const disconnectButtons = document.querySelectorAll('[data-disconnect="google"]');
            disconnectButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (confirm('Are you sure you want to disconnect your Google account?')) {
                        this.disconnectGoogle();
                    }
                });
            });
        });
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showAlert(message, 'danger');
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }

    /**
     * Update UI to show OAuth connection status
     */
    async updateOAuthStatus() {
        const status = await this.getSocialAccountStatus();
        if (status) {
            const googleStatusElements = document.querySelectorAll('[data-google-status]');
            googleStatusElements.forEach(element => {
                if (status.google_connected) {
                    element.textContent = 'Connected';
                    element.className = 'badge bg-success';
                } else {
                    element.textContent = 'Not Connected';
                    element.className = 'badge bg-secondary';
                }
            });
        }
    }
}

// Initialize OAuth handler
const googleOAuth = new GoogleOAuthHandler();

// Export for use in other scripts
window.GoogleOAuthHandler = GoogleOAuthHandler;
window.googleOAuth = googleOAuth;