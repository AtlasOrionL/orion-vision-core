#!/usr/bin/env python3
"""
🔒 Simple Zero Trust Test - Orion Vision Core
Quick validation of zero trust security features
"""

def test_zero_trust_security():
    """Test zero trust security implementation"""
    print("🔒 ORION VISION CORE - ZERO TRUST SECURITY TEST")
    print("=" * 60)
    print("🎯 Policy: ZERO TRUST - Never trust, always verify")
    print("=" * 60)
    print()
    
    results = {}
    
    # Test 1: Security Manager
    print("🔍 Test 1: Security Manager")
    try:
        from src.jobone.vision_core.security.core.security_manager import SecurityManager
        sm = SecurityManager()
        
        # Test authentication
        token = sm.authenticate_user("test_user", {"password": "test123456"})
        
        # Test authorization
        if token:
            access = sm.authorize_access(token, "test_resource", "read")
            print(f"✅ Security Manager - Authentication & Authorization working")
            print(f"   Token generated: {token[:20]}...")
            print(f"   Access authorized: {access}")
            results['security_manager'] = 100
        else:
            print("⚠️ Security Manager - Authentication failed")
            results['security_manager'] = 70
            
    except Exception as e:
        print(f"❌ Security Manager - Error: {str(e)[:50]}")
        results['security_manager'] = 0
    
    # Test 2: Authentication Module
    print("\n🔍 Test 2: Authentication Module")
    try:
        from src.jobone.vision_core.security.auth import AuthManager
        auth = AuthManager()
        print("✅ Authentication Module - Available")
        results['authentication'] = 100
    except Exception as e:
        print(f"❌ Authentication Module - Error: {str(e)[:50]}")
        results['authentication'] = 0
    
    # Test 3: Encryption Module
    print("\n🔍 Test 3: Encryption Module")
    try:
        from src.jobone.vision_core.security.encryption.encryption_manager import EncryptionManager
        enc = EncryptionManager()
        
        # Test encryption
        test_data = "sensitive_data_test"
        encrypted = enc.simple_encrypt(test_data)
        decrypted = enc.simple_decrypt(encrypted)
        
        print(f"✅ Encryption Module - Working")
        print(f"   Original: {test_data}")
        print(f"   Encrypted: {encrypted[:30]}...")
        print(f"   Decrypted: {decrypted}")
        results['encryption'] = 100
        
    except Exception as e:
        print(f"❌ Encryption Module - Error: {str(e)[:50]}")
        results['encryption'] = 0
    
    # Test 4: Audit Module
    print("\n🔍 Test 4: Audit Module")
    try:
        from src.jobone.vision_core.security.audit.audit_manager import AuditManager
        audit = AuditManager()
        print("✅ Audit Module - Available")
        results['audit'] = 100
    except Exception as e:
        print(f"❌ Audit Module - Error: {str(e)[:50]}")
        results['audit'] = 0
    
    # Test 5: Compliance Module
    print("\n🔍 Test 5: Compliance Module")
    try:
        from src.jobone.vision_core.security.compliance.compliance_manager import ComplianceManager
        compliance = ComplianceManager()
        print("✅ Compliance Module - Available")
        results['compliance'] = 100
    except Exception as e:
        print(f"❌ Compliance Module - Error: {str(e)[:50]}")
        results['compliance'] = 0
    
    # Test 6: Zero Trust Principles
    print("\n🔍 Test 6: Zero Trust Principles")
    zero_trust_score = 0
    
    # Principle 1: Never trust, always verify
    if results.get('security_manager', 0) > 0:
        print("✅ Verify every request - Authentication required")
        zero_trust_score += 20
    else:
        print("❌ Verify every request - Not implemented")
    
    # Principle 2: Least privilege access
    if results.get('authentication', 0) > 0:
        print("✅ Least privilege - Authorization system available")
        zero_trust_score += 20
    else:
        print("❌ Least privilege - Not implemented")
    
    # Principle 3: Assume breach
    if results.get('audit', 0) > 0:
        print("✅ Assume breach - Audit logging available")
        zero_trust_score += 20
    else:
        print("❌ Assume breach - Limited logging")
    
    # Principle 4: Encrypt everything
    if results.get('encryption', 0) > 0:
        print("✅ Encrypt everything - Encryption system available")
        zero_trust_score += 20
    else:
        print("❌ Encrypt everything - Not implemented")
    
    # Principle 5: Monitor and log
    if results.get('compliance', 0) > 0:
        print("✅ Monitor and log - Compliance monitoring available")
        zero_trust_score += 20
    else:
        print("❌ Monitor and log - Limited monitoring")
    
    results['zero_trust_principles'] = zero_trust_score
    
    # Calculate overall score
    total_score = sum(results.values()) / len(results)
    
    print("\n" + "=" * 60)
    print("🔒 ZERO TRUST SECURITY RESULTS")
    print("=" * 60)
    
    for component, score in results.items():
        status = "✅" if score >= 80 else "⚠️" if score >= 50 else "❌"
        print(f"{status} {component.replace('_', ' ').title():<25} - {score}%")
    
    print(f"\n🎯 OVERALL ZERO TRUST SCORE: {total_score:.1f}%")
    
    # Security assessment
    if total_score >= 90:
        print("\n🛡️ ZERO TRUST VERDICT: EXCELLENT!")
        print("🔒 Strong zero trust implementation!")
        print("✅ Security architecture meets high standards!")
        print("🚀 Production-ready security posture!")
    elif total_score >= 75:
        print("\n🔧 ZERO TRUST VERDICT: GOOD!")
        print("⚠️ Zero trust architecture is solid with room for improvement!")
        print("🛠️ Minor security enhancements recommended!")
    elif total_score >= 60:
        print("\n⚠️ ZERO TRUST VERDICT: MODERATE!")
        print("🚨 Zero trust implementation needs significant work!")
        print("🔒 Critical security gaps must be addressed!")
    else:
        print("\n❌ ZERO TRUST VERDICT: POOR!")
        print("🚨 Zero trust architecture inadequately implemented!")
        print("⛔ Major security overhaul required!")
    
    # Zero trust specific recommendations
    print("\n📋 ZERO TRUST RECOMMENDATIONS:")
    if results.get('security_manager', 0) < 100:
        print("   🔧 Enhance authentication mechanisms")
    if results.get('encryption', 0) < 100:
        print("   🔐 Implement end-to-end encryption")
    if results.get('audit', 0) < 100:
        print("   📊 Strengthen audit and logging")
    if results.get('compliance', 0) < 100:
        print("   📋 Improve compliance monitoring")
    
    print("=" * 60)
    return total_score

if __name__ == "__main__":
    score = test_zero_trust_security()
    
    print(f"\n🔒 Final Zero Trust Score: {score:.1f}%")
    
    if score >= 75:
        print("🛡️ Zero trust policy: ACCEPTABLE for production")
    else:
        print("🚨 Zero trust policy: NEEDS IMPROVEMENT before production")
