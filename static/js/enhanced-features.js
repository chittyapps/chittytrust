/**
 * Enhanced ChittyTrust Features
 * Timeline visualization, insights, and advanced analytics
 */

class EnhancedTrustFeatures {
    constructor(trustEngine) {
        this.trustEngine = trustEngine;
        this.timelineChart = null;
        this.currentTimelinePeriod = 'all';
    }

    // Initialize enhanced features
    initialize() {
        this.setupTimelineControls();
        this.setupNotificationSystem();
        this.setupTrustRingAnimations();
    }

    // Setup timeline controls
    setupTimelineControls() {
        const controls = document.querySelectorAll('[data-period]');
        controls.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Update active state
                controls.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                // Update timeline
                this.currentTimelinePeriod = e.target.dataset.period;
                this.updateTimeline();
            });
        });
    }

    // Load and display timeline data
    async loadTimeline(personaId) {
        try {
            const response = await fetch(`/api/trust/${personaId}/timeline`);
            const timelineData = await response.json();
            
            this.trustEngine.timelineData = timelineData;
            this.renderTimeline(timelineData);
            this.showTimelineSection();
            
            // Update event count
            const eventCountEl = document.getElementById('timeline-events');
            if (eventCountEl) {
                eventCountEl.textContent = timelineData.summary.total_events;
            }
            
        } catch (error) {
            console.error('Failed to load timeline:', error);
        }
    }

    // Render timeline chart
    renderTimeline(data) {
        const ctx = document.getElementById('trustTimelineChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.timelineChart) {
            this.timelineChart.destroy();
        }

        // Prepare chart data
        const chartData = this.prepareTimelineData(data);

        this.timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Composite Score',
                        data: chartData.composite,
                        borderColor: '#0088ff',
                        backgroundColor: 'rgba(0, 136, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Chitty Score™',
                        data: chartData.chitty,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#8892b0'
                        }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#8892b0',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                onHover: (event, elements) => {
                    if (elements.length > 0) {
                        const dataIndex = elements[0].index;
                        this.showTimelineTooltip(data.timeline[dataIndex]);
                    }
                }
            }
        });
    }

    // Prepare timeline data for chart
    prepareTimelineData(data) {
        let filteredData = data.rolling_scores;
        
        // Filter by selected period
        if (this.currentTimelinePeriod !== 'all') {
            const cutoffDate = new Date();
            switch (this.currentTimelinePeriod) {
                case 'week':
                    cutoffDate.setDate(cutoffDate.getDate() - 7);
                    break;
                case 'month':
                    cutoffDate.setMonth(cutoffDate.getMonth() - 1);
                    break;
                case 'year':
                    cutoffDate.setFullYear(cutoffDate.getFullYear() - 1);
                    break;
            }
            
            filteredData = filteredData.filter(item => 
                new Date(item.date) >= cutoffDate
            );
        }

        return {
            labels: filteredData.map(item => 
                new Date(item.date).toLocaleDateString()
            ),
            composite: filteredData.map(item => item.composite_score),
            chitty: filteredData.map(item => item.chitty_score)
        };
    }

    // Load and display insights
    async loadInsights(personaId) {
        try {
            const response = await fetch(`/api/trust/${personaId}/insights`);
            const insightsData = await response.json();
            
            this.renderInsights(insightsData.insights);
            this.renderRecommendations(insightsData.patterns);
            this.showInsightsSection();
            
        } catch (error) {
            console.error('Failed to load insights:', error);
        }
    }

    // Render trust insights
    renderInsights(insights) {
        const container = document.getElementById('insights-container');
        if (!container) return;

        container.innerHTML = insights.map(insight => `
            <div class="insight-card glass-card-mini mb-3">
                <div class="insight-header">
                    <span class="insight-category badge bg-${this.getCategoryColor(insight.category)}">${insight.category}</span>
                    <span class="insight-confidence">${Math.round(insight.confidence * 100)}% confidence</span>
                </div>
                <h6 class="insight-title text-white">${insight.title}</h6>
                <p class="insight-description text-muted">${insight.description}</p>
                <div class="insight-impact">
                    <small class="text-${insight.impact > 0 ? 'success' : 'warning'}">
                        Impact: ${insight.impact > 0 ? '+' : ''}${insight.impact}%
                    </small>
                </div>
            </div>
        `).join('');
    }

    // Render recommendations
    renderRecommendations(patterns) {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        container.innerHTML = patterns.map(pattern => `
            <div class="recommendation-card glass-card-mini mb-3">
                <div class="recommendation-header">
                    <span class="risk-level badge bg-${this.getRiskColor(pattern.risk_level)}">${pattern.risk_level} Risk</span>
                    <span class="frequency-badge">${pattern.frequency}x</span>
                </div>
                <h6 class="recommendation-title text-white">${pattern.pattern_type}</h6>
                <p class="recommendation-description text-muted">${pattern.description}</p>
                <div class="recommendation-action">
                    <strong class="text-chitty-green">Recommendation:</strong>
                    <p class="mb-0">${pattern.recommendation}</p>
                </div>
            </div>
        `).join('');
    }

    // Update trust ring animation
    updateTrustRing(score) {
        const progressCircle = document.getElementById('trust-progress-circle');
        const scoreElement = document.getElementById('trust-ring-score');
        
        if (progressCircle && scoreElement) {
            const circumference = 2 * Math.PI * 80; // radius = 80
            const offset = circumference - (score / 100) * circumference;
            
            progressCircle.style.strokeDashoffset = offset;
            scoreElement.textContent = Math.round(score);
        }
    }

    // Show timeline section
    showTimelineSection() {
        const section = document.getElementById('trust-timeline');
        if (section) {
            section.style.display = 'block';
            this.animateIn(section);
        }
    }

    // Show insights section
    showInsightsSection() {
        const section = document.getElementById('trust-insights');
        if (section) {
            section.style.display = 'block';
            this.animateIn(section);
        }
    }

    // Animate section into view
    animateIn(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s cubic-bezier(0.23, 1, 0.320, 1)';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    }

    // Setup notification system
    setupNotificationSystem() {
        this.createNotificationContainer();
    }

    // Create notification container
    createNotificationContainer() {
        if (document.querySelector('.notification-container')) return;
        
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    // Show notification
    showNotification(message, type = 'success') {
        const container = document.querySelector('.notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i data-feather="${this.getNotificationIcon(type)}" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            ${message}
        `;

        container.appendChild(notification);
        feather.replace();

        // Auto-remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutNotification 0.3s ease forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    // Setup trust ring animations
    setupTrustRingAnimations() {
        // Add CSS for ring animations if not exists
        if (!document.getElementById('trust-ring-styles')) {
            const style = document.createElement('style');
            style.id = 'trust-ring-styles';
            style.textContent = `
                @keyframes slideOutNotification {
                    to { transform: translateX(100%); opacity: 0; }
                }
                .glass-card-mini {
                    background: rgba(26, 26, 46, 0.3);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 1rem;
                }
                .insight-header, .recommendation-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                }
                .insight-confidence, .frequency-badge {
                    font-size: 0.75rem;
                    color: #8892b0;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Helper methods
    getCategoryColor(category) {
        const colors = {
            'strength': 'success',
            'concern': 'warning',
            'opportunity': 'info',
            'risk': 'danger'
        };
        return colors[category.toLowerCase()] || 'secondary';
    }

    getRiskColor(level) {
        const colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        };
        return colors[level.toLowerCase()] || 'secondary';
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'alert-circle',
            'info': 'info',
            'warning': 'alert-triangle'
        };
        return icons[type] || 'bell';
    }

    // Trigger success notification
    triggerSuccess(message) {
        this.showNotification(message, 'success');
    }

    // Trigger error notification
    triggerError(message) {
        this.showNotification(message, 'error');
    }

    // Update timeline period
    updateTimeline() {
        if (this.trustEngine.timelineData) {
            this.renderTimeline(this.trustEngine.timelineData);
        }
    }
}

// Initialize enhanced features when trust engine loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.chittyTrustEnhanced) {
        window.chittyTrustEnhanced.enhancedFeatures = new EnhancedTrustFeatures(window.chittyTrustEnhanced);
        window.chittyTrustEnhanced.enhancedFeatures.initialize();
    }
});