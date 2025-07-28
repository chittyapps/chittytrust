// Authentic Dynamic Spark Component based on Chitty Brand Guidelines
class DynamicSpark {
    constructor() {
        this.sparkPositions = [];
        this.initializeSparkElements();
    }

    // Create authentic lightning bolt SVG based on brand guidelines
    createSparkSVG(level = 'L2', size = 16) {
        const colors = this.getTrustLevelColors(level);
        
        return `
            <svg width="${size}" height="${size * 1.25}" viewBox="0 0 16 20" class="dynamic-spark-svg">
                <!-- Lightning bolt path from brand guidelines -->
                <path 
                    d="M8 1 L6 8 L10 8 L6.5 19 L12 10 L8.5 10 Z" 
                    fill="url(#sparkGradient-${level})" 
                    class="lightning-bolt"
                />
                
                <!-- Energy rings -->
                <circle 
                    cx="8" 
                    cy="10" 
                    r="12" 
                    fill="none" 
                    stroke="${colors.primary}" 
                    stroke-width="0.5" 
                    opacity="0.3"
                    class="energy-ring-outer"
                />
                <circle 
                    cx="8" 
                    cy="10" 
                    r="8" 
                    fill="none" 
                    stroke="${colors.secondary}" 
                    stroke-width="0.3" 
                    opacity="0.5"
                    class="energy-ring-inner"
                />
                
                <defs>
                    <linearGradient id="sparkGradient-${level}" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="${colors.start}" />
                        <stop offset="50%" stop-color="${colors.middle}" />
                        <stop offset="100%" stop-color="${colors.end}" />
                    </linearGradient>
                </defs>
            </svg>
        `;
    }

    // Get colors based on trust level from brand guidelines
    getTrustLevelColors(level) {
        const colorMap = {
            'L4': {
                start: '#10B981',    // Success Green
                middle: '#059669',   // Darker Green
                end: '#047857',      // Deep Green
                primary: '#10B981',
                secondary: '#34D399'
            },
            'L3': {
                start: '#3B82F6',    // Primary Blue
                middle: '#2563EB',   // Darker Blue
                end: '#1D4ED8',      // Deep Blue
                primary: '#3B82F6',
                secondary: '#60A5FA'
            },
            'L2': {
                start: '#8B5CF6',    // Secondary Purple
                middle: '#7C3AED',   // Darker Purple
                end: '#6D28D9',      // Deep Purple
                primary: '#8B5CF6',
                secondary: '#A78BFA'
            },
            'L1': {
                start: '#F97316',    // Accent Orange
                middle: '#EA580C',   // Darker Orange
                end: '#C2410C',      // Deep Orange
                primary: '#F97316',
                secondary: '#FB923C'
            },
            'L0': {
                start: '#9CA3AF',    // Gray
                middle: '#6B7280',   // Darker Gray
                end: '#4B5563',      // Deep Gray
                primary: '#9CA3AF',
                secondary: '#D1D5DB'
            }
        };
        
        return colorMap[level] || colorMap['L2'];
    }

    // Initialize all spark elements on the page
    initializeSparkElements() {
        // Find all elements with spark class and replace with authentic SVG
        const sparkElements = document.querySelectorAll('.spark');
        
        sparkElements.forEach((element, index) => {
            const trustLevel = this.extractTrustLevel(element);
            const size = this.extractSize(element);
            
            // Replace content with authentic spark SVG
            element.innerHTML = this.createSparkSVG(trustLevel, size);
            
            // Add dynamic particle effects for high trust levels
            if (trustLevel === 'L4' || trustLevel === 'L3') {
                this.addParticleEffects(element, index);
            }
        });
    }

    // Extract trust level from parent element classes
    extractTrustLevel(element) {
        const parent = element.closest('[class*="trust-level-"]');
        if (parent) {
            const classes = parent.className.split(' ');
            const levelClass = classes.find(cls => cls.startsWith('trust-level-'));
            return levelClass ? levelClass.replace('trust-level-', '') : 'L2';
        }
        return 'L2';
    }

    // Extract size from element or use default
    extractSize(element) {
        const parent = element.closest('.radar-chart-spark');
        if (parent) return 20;
        
        const logoParent = element.closest('.chitty-dynamic-logo');
        if (logoParent) return 18;
        
        return 16;
    }

    // Add dynamic particle effects for high trust levels
    addParticleEffects(element, index) {
        const particles = document.createElement('div');
        particles.className = 'spark-particles';
        particles.style.cssText = `
            position: absolute;
            top: -5px;
            left: -5px;
            right: -5px;
            bottom: -5px;
            pointer-events: none;
            z-index: 1;
        `;

        // Create individual particles
        for (let i = 0; i < 3; i++) {
            const particle = document.createElement('div');
            particle.className = `particle particle-${i}`;
            particle.style.cssText = `
                position: absolute;
                width: 3px;
                height: 3px;
                border-radius: 50%;
                background: #F59E0B;
                animation: particleFloat-${i} ${2 + i * 0.5}s ease-in-out infinite;
                animation-delay: ${index * 0.2 + i * 0.3}s;
            `;
            particles.appendChild(particle);
        }

        element.appendChild(particles);
    }

    // Update spark based on verification state
    updateSparkState(element, state) {
        const svg = element.querySelector('.dynamic-spark-svg');
        if (!svg) return;

        const lightningBolt = svg.querySelector('.lightning-bolt');
        const outerRing = svg.querySelector('.energy-ring-outer');
        const innerRing = svg.querySelector('.energy-ring-inner');

        switch (state) {
            case 'verification-active':
                svg.style.animation = 'sparkVerify 0.8s ease-in-out infinite';
                if (outerRing) outerRing.style.animation = 'energyPulse 1s ease-in-out infinite';
                break;
            case 'verification-pending':
                svg.style.animation = 'sparkPending 1.5s ease-in-out infinite';
                if (outerRing) outerRing.style.opacity = '0.6';
                break;
            case 'verification-failed':
                svg.style.animation = 'sparkError 2s ease-in-out infinite';
                if (lightningBolt) lightningBolt.style.fill = 'url(#sparkGradient-error)';
                break;
            default:
                svg.style.animation = 'sparkPulse 2s ease-in-out infinite';
        }
    }

    // Initialize hover effects for logo
    initializeLogoEffects() {
        const logo = document.querySelector('.chitty-dynamic-logo');
        if (!logo) return;

        logo.addEventListener('mouseenter', () => {
            const spark = logo.querySelector('.dynamic-spark-svg');
            if (spark) {
                spark.style.animation = 'sparkActive 1s ease-in-out infinite';
                spark.style.filter = 'drop-shadow(0 0 10px rgba(245, 158, 11, 0.9))';
            }
        });

        logo.addEventListener('mouseleave', () => {
            const spark = logo.querySelector('.dynamic-spark-svg');
            if (spark) {
                spark.style.animation = 'sparkPulse 2s ease-in-out infinite';
                spark.style.filter = 'drop-shadow(0 0 4px rgba(245, 158, 11, 0.6))';
            }
        });
    }
}

// CSS animations for particles and effects
const sparkAnimationCSS = `
/* Particle animations */
@keyframes particleFloat-0 {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.6; }
    50% { transform: translate(5px, -8px) scale(1.2); opacity: 1; }
}

@keyframes particleFloat-1 {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.5; }
    50% { transform: translate(-6px, -5px) scale(1.1); opacity: 0.9; }
}

@keyframes particleFloat-2 {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.7; }
    50% { transform: translate(3px, -10px) scale(1.3); opacity: 1; }
}

/* Energy ring animations */
@keyframes energyPulse {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.1); }
}

/* Enhanced spark animations */
@keyframes sparkActive {
    0%, 100% { 
        transform: scale(1) rotate(0deg);
        filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.9)) brightness(1);
    }
    50% { 
        transform: scale(1.2) rotate(5deg);
        filter: drop-shadow(0 0 15px rgba(245, 158, 11, 1)) brightness(1.3);
    }
}

@keyframes sparkVerify {
    0%, 100% { 
        transform: scale(1) rotate(0deg);
        filter: drop-shadow(0 0 6px rgba(16, 185, 129, 0.8)) brightness(1);
    }
    33% { 
        transform: scale(1.1) rotate(3deg);
        filter: drop-shadow(0 0 8px rgba(16, 185, 129, 1)) brightness(1.2);
    }
    66% { 
        transform: scale(1.05) rotate(-2deg);
        filter: drop-shadow(0 0 7px rgba(16, 185, 129, 0.9)) brightness(1.1);
    }
}

@keyframes sparkPending {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}

@keyframes sparkError {
    0%, 100% { 
        transform: scale(1);
        filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.6)) brightness(1);
    }
    25%, 75% { 
        transform: scale(0.95);
        filter: drop-shadow(0 0 2px rgba(239, 68, 68, 0.4)) brightness(0.9);
    }
    50% { 
        transform: scale(1.1);
        filter: drop-shadow(0 0 6px rgba(239, 68, 68, 0.8)) brightness(1.1);
    }
}
`;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add animation CSS
    const style = document.createElement('style');
    style.textContent = sparkAnimationCSS;
    document.head.appendChild(style);
    
    // Initialize dynamic spark system
    const sparkSystem = new DynamicSpark();
    sparkSystem.initializeLogoEffects();
    
    // Make available globally for trust engine updates
    window.dynamicSparkSystem = sparkSystem;
});

// Export for ES6 modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicSpark;
}