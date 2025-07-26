/**
 * ChittyTrust Frontend
 * Handles persona selection, trust calculations, and visualizations
 */

class TrustEngine {
    constructor() {
        this.currentPersona = null;
        this.radarChart = null;
        this.personas = [];
    }

    static init() {
        const engine = new TrustEngine();
        engine.loadPersonas();
        return engine;
    }

    async loadPersonas() {
        try {
            const response = await fetch('/api/personas');
            this.personas = await response.json();
            this.renderPersonaSelector();
        } catch (error) {
            console.error('Failed to load personas:', error);
        }
    }

    renderPersonaSelector() {
        const selector = document.getElementById('persona-selector');
        if (!selector) return;

        selector.innerHTML = this.personas.map(persona => `
            <div class="persona-card" data-persona-id="${persona.id}" onclick="trustEngine.selectPersona('${persona.id}')">
                <div class="persona-avatar">${persona.avatar}</div>
                <div class="persona-name">${persona.name}</div>
                <div class="persona-description">${persona.description}</div>
                <div class="persona-type">${persona.type}</div>
            </div>
        `).join('');
    }

    async selectPersona(personaId) {
        // Update UI
        document.querySelectorAll('.persona-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-persona-id="${personaId}"]`).classList.add('active');

        // Show loading states
        this.showLoadingStates();
        
        // Show analysis section
        document.getElementById('trust-analysis').style.display = 'block';
        document.getElementById('dimension-explanations').style.display = 'block';

        try {
            const response = await fetch(`/api/trust/${personaId}`);
            const trustData = await response.json();
            
            this.currentPersona = personaId;
            this.updateTrustDisplay(trustData);
        } catch (error) {
            console.error('Failed to load trust data:', error);
            this.showError('Failed to calculate trust score');
        }
    }

    showLoadingStates() {
        // Add loading animation to scores
        const scoreElements = [
            'composite-score', 'people-score', 'legal-score', 
            'state-score', 'chitty-score'
        ];
        
        scoreElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = '--';
                element.classList.add('loading-pulse');
            }
        });

        // Clear ChittyID level
        const levelElement = document.getElementById('chitty-level');
        if (levelElement) {
            levelElement.innerHTML = '<span class="badge bg-secondary">Calculating...</span>';
        }
    }

    updateTrustDisplay(trustData) {
        // Remove loading states
        document.querySelectorAll('.loading-pulse').forEach(el => {
            el.classList.remove('loading-pulse');
        });

        // Update composite score
        this.animateScore('composite-score', trustData.scores.composite, '%');
        
        // Update output scores
        this.animateScore('people-score', trustData.scores.people);
        this.animateScore('legal-score', trustData.scores.legal);
        this.animateScore('state-score', trustData.scores.state);
        this.animateScore('chitty-score', trustData.scores.chitty);

        // Update ChittyID level
        this.updateChittyLevel(trustData.persona.chitty_level);

        // Update radar chart
        this.updateRadarChart(trustData.dimensions);

        // Update explanations
        this.updateExplanations(trustData.metadata.explanation);
    }

    animateScore(elementId, finalValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;

        const roundedValue = Math.round(finalValue);
        let currentValue = 0;
        const increment = roundedValue / 30; // Animation duration
        
        element.classList.add('score-animate');
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= roundedValue) {
                currentValue = roundedValue;
                clearInterval(timer);
            }
            element.textContent = Math.round(currentValue) + suffix;
        }, 16); // ~60fps
    }

    updateChittyLevel(levelData) {
        const levelElement = document.getElementById('chitty-level');
        if (!levelElement || !levelData) return;

        levelElement.innerHTML = `
            <span class="chitty-level-badge" style="background-color: ${levelData.color}20; color: ${levelData.color}; border: 1px solid ${levelData.color};">
                ${levelData.level} - ${levelData.name}
            </span>
        `;
    }

    updateRadarChart(dimensions) {
        const ctx = document.getElementById('trustRadarChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.radarChart) {
            this.radarChart.destroy();
        }

        const data = {
            labels: [
                'Source (Who)',
                'Temporal (When)', 
                'Channel (How)',
                'Outcome (Results)',
                'Network (Connections)',
                'Justice (Impact)'
            ],
            datasets: [{
                label: 'Trust Score',
                data: [
                    dimensions.source,
                    dimensions.temporal,
                    dimensions.channel,
                    dimensions.outcome,
                    dimensions.network,
                    dimensions.justice
                ],
                backgroundColor: 'rgba(0, 136, 255, 0.2)',
                borderColor: '#0088ff',
                borderWidth: 2,
                pointBackgroundColor: '#00ff88',
                pointBorderColor: '#00ff88',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        };

        const config = {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: '#666',
                            backdrop: 'rgba(0, 0, 0, 0)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: '#fff',
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    }
                },
                elements: {
                    line: {
                        tension: 0.1
                    }
                }
            }
        };

        this.radarChart = new Chart(ctx, config);
    }

    updateExplanations(explanations) {
        const grid = document.getElementById('explanations-grid');
        if (!grid || !explanations) return;

        const dimensionIcons = {
            source: 'user-check',
            temporal: 'clock',
            channel: 'send',
            outcome: 'target',
            network: 'share-2',
            justice: 'balance-scale'
        };

        grid.innerHTML = Object.entries(explanations).map(([dimension, explanation]) => `
            <div class="col-md-6 col-lg-4">
                <div class="explanation-card">
                    <div class="d-flex align-items-center mb-2">
                        <i data-feather="${dimensionIcons[dimension]}" class="me-2 text-chitty-blue"></i>
                        <div class="explanation-title">${dimension}</div>
                    </div>
                    <div class="explanation-text">${explanation}</div>
                </div>
            </div>
        `).join('');

        // Re-initialize feather icons
        feather.replace();
    }

    showError(message) {
        const analysisSection = document.getElementById('trust-analysis');
        if (analysisSection) {
            analysisSection.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger" role="alert">
                        <i data-feather="alert-circle" class="me-2"></i>
                        ${message}
                    </div>
                </div>
            `;
            feather.replace();
        }
    }
}

// Global instance
let trustEngine;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    trustEngine = TrustEngine.init();
});
