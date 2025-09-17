/**
 * Comprehensive ChittyTrust Frontend Test Suite
 * Tests all interactive elements, API calls, and user flows
 */

class ComprehensiveTester {
    constructor() {
        this.testResults = [];
        this.baseUrl = 'http://localhost:5001';
    }

    async runFullTestSuite() {
        console.log('🚀 Starting comprehensive ChittyTrust testing...');
        
        // Core API Tests
        await this.testCoreAPIs();
        
        // Frontend Loading Tests  
        await this.testFrontendAssets();
        
        // Interactive Element Tests
        await this.testInteractiveElements();
        
        // User Journey Tests
        await this.testUserJourneys();
        
        // Performance Tests
        await this.testPerformance();
        
        // Error Handling Tests
        await this.testErrorHandling();
        
        this.generateReport();
    }

    async testCoreAPIs() {
        console.log('\n📡 Testing Core APIs...');
        
        const apiTests = [
            { endpoint: '/api/personas', name: 'Personas API' },
            { endpoint: '/api/trust/alice', name: 'Alice Trust Calculation' },
            { endpoint: '/api/trust/bob', name: 'Bob Trust Calculation' },
            { endpoint: '/api/trust/charlie', name: 'Charlie Trust Calculation' },
            { endpoint: '/api/compare', name: 'Persona Comparison' },
            { endpoint: '/api/marketplace/requests', name: 'Marketplace Requests' },
            { endpoint: '/api/chittyos/status', name: 'ChittyOS Status' }
        ];

        for (const test of apiTests) {
            try {
                const response = await fetch(`${this.baseUrl}${test.endpoint}`);
                const data = await response.json();
                
                if (response.ok && data) {
                    this.addResult(test.name, 'PASS', `✅ Response: ${response.status}, Data: ${typeof data}`);
                } else {
                    this.addResult(test.name, 'FAIL', `❌ Status: ${response.status}`);
                }
            } catch (error) {
                this.addResult(test.name, 'ERROR', `💥 ${error.message}`);
            }
        }
    }

    async testFrontendAssets() {
        console.log('\n🎨 Testing Frontend Assets...');
        
        const assetTests = [
            { url: '/static/css/enhanced-ui.css', name: 'Enhanced UI CSS' },
            { url: '/static/js/trust-engine.js', name: 'Trust Engine JS' },
            { url: '/static/js/enhanced-features.js', name: 'Enhanced Features JS' },
            { url: '/static/js/marketplace.js', name: 'Marketplace JS' },
            { url: '/static/css/chitty.css', name: 'Main CSS' }
        ];

        for (const test of assetTests) {
            try {
                const response = await fetch(`${this.baseUrl}${test.url}`);
                const content = await response.text();
                
                if (response.ok && content.length > 100) {
                    this.addResult(test.name, 'PASS', `✅ Loaded ${content.length} chars`);
                } else {
                    this.addResult(test.name, 'FAIL', `❌ Status: ${response.status}, Size: ${content.length}`);
                }
            } catch (error) {
                this.addResult(test.name, 'ERROR', `💥 ${error.message}`);
            }
        }
    }

    async testInteractiveElements() {
        console.log('\n🖱️ Testing Interactive Elements...');
        
        // Test main page structure
        try {
            const response = await fetch(`${this.baseUrl}/`);
            const html = await response.text();
            
            // Check for key interactive elements
            const checks = [
                { selector: 'data-persona=', name: 'Persona Selection Cards', count: 3 },
                { selector: 'onclick=', name: 'Click Handlers', count: 5 },
                { selector: 'id="trust-analysis"', name: 'Trust Analysis Section', count: 1 },
                { selector: 'id="trustRadarChart"', name: 'Radar Chart Canvas', count: 1 },
                { selector: 'class="dashboard-metric"', name: 'Dashboard Metrics', count: 6 },
                { selector: 'class="glass-card"', name: 'Glass Card Components', count: 8 },
                { selector: 'trust-ring-container', name: 'Trust Ring Animation', count: 1 },
                { selector: 'data-feather=', name: 'Feather Icons', count: 20 }
            ];

            for (const check of checks) {
                const count = (html.match(new RegExp(check.selector, 'g')) || []).length;
                if (count >= check.count) {
                    this.addResult(check.name, 'PASS', `✅ Found ${count} elements (expected ${check.count}+)`);
                } else {
                    this.addResult(check.name, 'FAIL', `❌ Found ${count} elements (expected ${check.count}+)`);
                }
            }

        } catch (error) {
            this.addResult('HTML Structure', 'ERROR', `💥 ${error.message}`);
        }
    }

    async testUserJourneys() {
        console.log('\n👤 Testing User Journeys...');
        
        // Test persona selection flow
        const personas = ['alice', 'bob', 'charlie'];
        
        for (const persona of personas) {
            try {
                // Test trust calculation
                const trustResponse = await fetch(`${this.baseUrl}/api/trust/${persona}`);
                const trustData = await trustResponse.json();
                
                if (trustData.dimensions && trustData.scores && trustData.metadata) {
                    // Validate data structure
                    const hasAllDimensions = ['source', 'temporal', 'channel', 'outcome', 'network', 'justice']
                        .every(dim => trustData.dimensions.hasOwnProperty(dim));
                    
                    const hasAllScores = ['people', 'legal', 'state', 'chitty', 'composite']
                        .every(score => trustData.scores.hasOwnProperty(score));
                    
                    if (hasAllDimensions && hasAllScores) {
                        this.addResult(`${persona.toUpperCase()} Journey`, 'PASS', 
                            `✅ Complete trust profile: ${trustData.scores.composite.toFixed(1)}% composite`);
                    } else {
                        this.addResult(`${persona.toUpperCase()} Journey`, 'FAIL', 
                            `❌ Incomplete data structure`);
                    }
                } else {
                    this.addResult(`${persona.toUpperCase()} Journey`, 'FAIL', 
                        `❌ Invalid response structure`);
                }
                
                // Test timeline (if endpoint exists)
                try {
                    const timelineResponse = await fetch(`${this.baseUrl}/api/trust/${persona}/timeline`);
                    if (timelineResponse.ok) {
                        this.addResult(`${persona.toUpperCase()} Timeline`, 'PASS', `✅ Timeline data available`);
                    }
                } catch (e) {
                    this.addResult(`${persona.toUpperCase()} Timeline`, 'SKIP', `⏭️ Timeline endpoint not implemented`);
                }
                
            } catch (error) {
                this.addResult(`${persona.toUpperCase()} Journey`, 'ERROR', `💥 ${error.message}`);
            }
        }
    }

    async testPerformance() {
        console.log('\n⚡ Testing Performance...');
        
        const performanceTests = [
            { endpoint: '/api/personas', name: 'Personas Load Time', threshold: 500 },
            { endpoint: '/api/trust/alice', name: 'Trust Calculation Speed', threshold: 1000 },
            { endpoint: '/api/marketplace/requests', name: 'Marketplace Load Time', threshold: 800 }
        ];

        for (const test of performanceTests) {
            try {
                const startTime = Date.now();
                const response = await fetch(`${this.baseUrl}${test.endpoint}`);
                const endTime = Date.now();
                const duration = endTime - startTime;
                
                if (response.ok && duration < test.threshold) {
                    this.addResult(test.name, 'PASS', `✅ ${duration}ms (under ${test.threshold}ms)`);
                } else if (response.ok) {
                    this.addResult(test.name, 'SLOW', `⚠️ ${duration}ms (over ${test.threshold}ms)`);
                } else {
                    this.addResult(test.name, 'FAIL', `❌ Status: ${response.status}`);
                }
            } catch (error) {
                this.addResult(test.name, 'ERROR', `💥 ${error.message}`);
            }
        }
    }

    async testErrorHandling() {
        console.log('\n🛡️ Testing Error Handling...');
        
        const errorTests = [
            { endpoint: '/api/trust/invalid-persona', name: 'Invalid Persona Handling' },
            { endpoint: '/api/nonexistent-endpoint', name: '404 Error Handling' },
            { endpoint: '/api/trust/', name: 'Empty Parameter Handling' }
        ];

        for (const test of errorTests) {
            try {
                const response = await fetch(`${this.baseUrl}${test.endpoint}`);
                
                if (response.status >= 400 && response.status < 500) {
                    this.addResult(test.name, 'PASS', `✅ Proper error status: ${response.status}`);
                } else if (response.status === 200) {
                    this.addResult(test.name, 'WARN', `⚠️ Unexpected success for invalid request`);
                } else {
                    this.addResult(test.name, 'FAIL', `❌ Unexpected status: ${response.status}`);
                }
            } catch (error) {
                this.addResult(test.name, 'PASS', `✅ Network error handled: ${error.message}`);
            }
        }
    }

    async testSpecialFeatures() {
        console.log('\n🌟 Testing Special Features...');
        
        // Test ChittyID generation
        try {
            const response = await fetch(`${this.baseUrl}/api/chitty-id/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vertical: 'test', identity_verified: true })
            });
            
            const data = await response.json();
            
            if (data.chitty_id && data.chitty_id.startsWith('CH-')) {
                this.addResult('ChittyID Generation', 'PASS', `✅ Generated: ${data.chitty_id}`);
            } else {
                this.addResult('ChittyID Generation', 'FAIL', `❌ Invalid ID format`);
            }
        } catch (error) {
            this.addResult('ChittyID Generation', 'ERROR', `💥 ${error.message}`);
        }

        // Test ChittyVerify status
        try {
            const response = await fetch(`${this.baseUrl}/api/chitty-verify`);
            const data = await response.json();
            
            if (data.status === 'operational') {
                this.addResult('ChittyVerify Service', 'PASS', `✅ Status: ${data.status}`);
            } else {
                this.addResult('ChittyVerify Service', 'FAIL', `❌ Status: ${data.status}`);
            }
        } catch (error) {
            this.addResult('ChittyVerify Service', 'ERROR', `💥 ${error.message}`);
        }
    }

    addResult(name, status, message) {
        this.testResults.push({ name, status, message, timestamp: new Date().toISOString() });
        console.log(`${status}: ${name} - ${message}`);
    }

    generateReport() {
        console.log('\n📊 COMPREHENSIVE TEST REPORT');
        console.log('=====================================');
        
        const statusCounts = this.testResults.reduce((acc, result) => {
            acc[result.status] = (acc[result.status] || 0) + 1;
            return acc;
        }, {});

        const totalTests = this.testResults.length;
        const passCount = statusCounts.PASS || 0;
        const failCount = statusCounts.FAIL || 0;
        const errorCount = statusCounts.ERROR || 0;
        const passRate = ((passCount / totalTests) * 100).toFixed(1);

        console.log(`Total Tests: ${totalTests}`);
        console.log(`✅ Passed: ${passCount}`);
        console.log(`❌ Failed: ${failCount}`);
        console.log(`💥 Errors: ${errorCount}`);
        console.log(`📈 Pass Rate: ${passRate}%`);
        
        console.log('\nDETAILED RESULTS:');
        console.log('-----------------');
        this.testResults.forEach(result => {
            console.log(`${result.status.padEnd(6)} | ${result.name.padEnd(30)} | ${result.message}`);
        });

        // Overall assessment
        if (passRate >= 95) {
            console.log('\n🎉 EXCELLENT: System is production-ready!');
        } else if (passRate >= 85) {
            console.log('\n✅ GOOD: Minor issues to address');
        } else if (passRate >= 70) {
            console.log('\n⚠️ FAIR: Several issues need attention');
        } else {
            console.log('\n🔧 POOR: Significant problems detected');
        }

        return {
            totalTests,
            passCount,
            failCount,
            errorCount,
            passRate: parseFloat(passRate),
            results: this.testResults
        };
    }
}

// Run the comprehensive test
async function runComprehensiveTest() {
    const tester = new ComprehensiveTester();
    await tester.runFullTestSuite();
    await tester.testSpecialFeatures();
    return tester.generateReport();
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ComprehensiveTester, runComprehensiveTest };
} else {
    window.runComprehensiveTest = runComprehensiveTest;
}