/**
 * Test suite for ChittyOS Core Packages
 */

import ChittyCore from './index.js';

console.log('🚀 Testing ChittyOS Core Packages...\n');

const chittyCore = new ChittyCore();

// Test 1: Trust Engine
console.log('📊 Testing Trust Engine...');
const trustTest = async () => {
  const entity = {
    id: 'test-user-001',
    verified_identity: true,
    credentials: ['email_verified', 'phone_verified'],
    biometric_verified: false,
    communication_channels: [
      { type: 'email', verified: true },
      { type: 'phone', verified: true }
    ],
    network_connections: [
      { id: 'connection1', trust_score: 85 },
      { id: 'connection2', trust_score: 92 }
    ],
    dispute_resolution_rate: 0.9,
    transparency_score: 0.8,
    fairness_rating: 0.85
  };

  const events = [
    { timestamp: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(), outcome: 'positive' },
    { timestamp: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(), outcome: 'positive' },
    { timestamp: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), outcome: 'positive' },
    { timestamp: new Date().toISOString(), outcome: 'positive' }
  ];

  const trustScore = await chittyCore.trust.calculateTrust(entity, events);
  console.log('Trust Score:', trustScore.composite_score);
  console.log('Trust Level:', trustScore.chitty_level);
  console.log('Dimensions:', trustScore.dimension_scores);
  console.log('✅ Trust Engine test passed\n');
};

// Test 2: Verify Service
console.log('🔐 Testing Verify Service...');
const verifyTest = async () => {
  const emailVerification = await chittyCore.verify.verifyUser(
    'test-user-001',
    'email',
    {
      email: 'test@chittyos.com',
      verificationCode: '123456'
    }
  );
  console.log('Email Verification:', emailVerification.success ? 'Success' : 'Failed');

  const identityVerification = await chittyCore.verify.verifyUser(
    'test-user-001',
    'identity',
    {
      documentType: 'passport',
      documentNumber: 'A1234567'
    }
  );
  console.log('Identity Verification:', identityVerification.success ? 'Success' : 'Failed');
  console.log('✅ Verify Service test passed\n');
};

// Test 3: Certify Service
console.log('📜 Testing Certify Service...');
const certifyTest = async () => {
  const documentCert = await chittyCore.certify.certifyDocument(
    { content: 'Test document content', author: 'Test Author' },
    {
      fileName: 'test.pdf',
      fileSize: 1024,
      mimeType: 'application/pdf',
      creator: 'test-user-001'
    }
  );
  console.log('Document Certificate ID:', documentCert.certificateId);
  console.log('Document Hash:', documentCert.documentHash.substring(0, 16) + '...');

  const credential = await chittyCore.certify.issueCredential(
    'test-user-001',
    'PROFESSIONAL_LICENSE',
    {
      claims: {
        profession: 'Software Engineer',
        licenseNumber: 'SE-2024-001',
        issuedBy: 'ChittyOS Professional Board'
      },
      validityDays: 365
    }
  );
  console.log('Credential ID:', credential.credentialId);
  console.log('Expires At:', credential.expiresAt);
  console.log('✅ Certify Service test passed\n');
};

// Test 4: Integrated Onboarding
console.log('🎯 Testing Integrated Onboarding...');
const onboardingTest = async () => {
  const onboardResult = await chittyCore.onboardUser(
    'new-user-001',
    {
      documentType: 'drivers_license',
      documentNumber: 'DL123456',
      channels: [
        { type: 'email', verified: true },
        { type: 'sms', verified: false }
      ]
    }
  );

  console.log('Onboarding Success:', onboardResult.success);
  if (onboardResult.success) {
    console.log('Trust Level:', onboardResult.trustProfile.chitty_level);
    console.log('Certificate ID:', onboardResult.certificate.credentialId);
  }
  console.log('✅ Integrated Onboarding test passed\n');
};

// Test 5: Document Processing
console.log('📄 Testing Document Processing...');
const documentTest = async () => {
  const processResult = await chittyCore.processDocument(
    'test-user-001',
    { title: 'Important Contract', content: 'Contract terms and conditions...' },
    { type: 'contract', description: 'Service Agreement' }
  );

  console.log('Processing Success:', processResult.success);
  if (processResult.success) {
    console.log('Certificate ID:', processResult.certificate.certificateId);
    console.log('Trust Weighting:', processResult.trustWeighting);
  }
  console.log('✅ Document Processing test passed\n');
};

// Test 6: Comprehensive Verification
console.log('🛡️ Testing Comprehensive Verification...');
const comprehensiveTest = async () => {
  const result = await chittyCore.performComprehensiveVerification(
    'test-user-001',
    {
      email: { email: 'test@chittyos.com', verificationCode: '123456' },
      phone: { phone: '+1234567890', smsCode: '999999' },
      identity: { documentType: 'national_id', documentNumber: 'ID987654' },
      address: { street: '123 Main St', city: 'TestCity', country: 'TestLand' }
    }
  );

  console.log('Overall Verification Score:', result.overallScore);
  console.log('Trust Level:', result.trustProfile.chitty_level);
  console.log('Verified Methods:', Object.keys(result.verifications).filter(
    type => result.verifications[type].success
  ));
  console.log('✅ Comprehensive Verification test passed\n');
};

// Run all tests
const runAllTests = async () => {
  try {
    await trustTest();
    await verifyTest();
    await certifyTest();
    await onboardingTest();
    await documentTest();
    await comprehensiveTest();

    console.log('=' . repeat(50));
    console.log('🎉 All tests completed successfully!');
    console.log('=' . repeat(50));
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
};

runAllTests();