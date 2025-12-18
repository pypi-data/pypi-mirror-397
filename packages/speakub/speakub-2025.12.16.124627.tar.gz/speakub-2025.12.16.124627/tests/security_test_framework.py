#!/usr/bin/env python3
"""
Security Test Framework for SpeakUB.
Phase 3: Security enhancements with comprehensive testing
"""

import tempfile
import unittest
from pathlib import Path
from speakub.utils.security import InputValidator, TextSanitizer


class TestSecurityValidations:
    """Comprehensive security validation tests."""

    def test_epub_path_validation(self):
        """Test EPUB path validation security."""
        # Create temporary files for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create valid EPUB file
            valid_epub = temp_path / "test.epub"
            valid_epub.write_bytes(b"Fake EPUB content")

            # Create invalid file types
            exe_file = temp_path / "malware.exe"
            exe_file.write_bytes(b"Fake executable")

            # Test valid EPUB
            assert InputValidator.validate_epub_path(str(valid_epub))

            # Test invalid types
            assert not InputValidator.validate_epub_path(str(exe_file))

            # Test non-existent file
            assert not InputValidator.validate_epub_path(
                str(temp_path / "nonexistent.epub"))

            print("✓ EPUB path validation security tests passed")

    def test_text_sanitization(self):
        """Test TTS text sanitization."""
        # Test normal text
        normal_text = "Hello, this is normal text for TTS."
        sanitized = TextSanitizer.sanitize_tts_text(normal_text)
        assert sanitized == normal_text

        # Test XSS attempts
        malicious_text = 'Hello <script>alert("XSS")</script> world'
        sanitized = TextSanitizer.sanitize_tts_text(malicious_text)
        assert "<script>" not in sanitized

        # Test excessive whitespace
        whitespace_text = "  Too    much  \n\n\nwhitespace   \n  here\n\n\n"
        sanitized = TextSanitizer.sanitize_tts_text(whitespace_text)
        lines = sanitized.count('\n')
        assert lines <= 2  # Should normalize excessive newlines

        print("✓ Text sanitization security tests passed")

    def test_file_size_limits(self):
        """Test file size limit enforcement."""
        from speakub.utils.config import ConfigManager

        config = ConfigManager()
        max_size = config.get("epub_security.max_file_size_mb", 50)
        max_bytes = max_size * 1024 * 1024

        # Test reasonable file
        reasonable_text = "X" * (max_bytes // 2)  # Half max size

        with tempfile.NamedTemporaryFile(suffix='.epub', mode='w', delete=False) as f:
            f.write(reasonable_text)
            temp_path = f.name

        try:
            # Should pass validation
            assert InputValidator.validate_epub_path(temp_path)
            print("✓ File size limit tests passed")
        finally:
            Path(temp_path).unlink()

    def test_filename_sanitization(self):
        """Test filename sanitization."""
        dangerous_names = [
            "../../../etc/passwd",
            "file<script>.epub",
            "file:with:colons.epub",
            "file|with|pipes.epub",
            "file\nwith\nnewlines.epub",
        ]

        for dangerous in dangerous_names:
            safe = InputValidator.sanitize_filename(dangerous)
            # Should not contain dangerous characters
            assert "<" not in safe
            assert ">" not in safe
            assert ":" not in safe
            assert "|" not in safe
            assert "\n" not in safe
            assert ".." not in safe
            # Should still be a reasonable filename
            assert len(safe) > 0
            assert safe != dangerous

        print("✓ Filename sanitization security tests passed")


class SecurityAudit:
    """Automated security audit for SpeakUB."""

    @staticmethod
    def run_security_audit():
        """Run comprehensive security audit."""
        print("🔒 Running SpeakUB Security Audit...")
        print()

        issues_found = []
        recommendations = []

        # Check 1: Dependency vulnerabilities
        try:
            import subprocess
            result = subprocess.run([
                'pip', 'audit'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                issues_found.append("Dependency vulnerabilities detected")
                recommendations.append(
                    "Review pip audit output and update vulnerable packages")
        except Exception as e:
            issues_found.append(f"Could not check dependencies: {e}")

        # Check 2: File permissions
        import os
        import stat

        config_files = [
            '~/.local/share/speakub',
            '~/.config/speakub',
        ]

        for config_path in config_files:
            expanded_path = os.path.expanduser(config_path)
            if os.path.exists(expanded_path):
                st = os.stat(expanded_path)
                # Check if others have write access
                if st.st_mode & stat.S_IWOTH:
                    issues_found.append(
                        f"Config directory has world write access: {config_path}")
                    recommendations.append(
                        f"Set proper permissions: chmod 755 {config_path}")

        # Check 3: Environment variables (basic)
        dangerous_env_vars = ['LD_PRELOAD', 'LD_LIBRARY_PATH']
        for var in dangerous_env_vars:
            if var in os.environ:
                print(
                    f"⚠️  Environment variable set: {var} = {os.environ[var][:20]}...")

        # Report findings
        if issues_found:
            print("❌ Security Issues Found:")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("✅ No major security issues detected")

        if recommendations:
            print("\n💡 Security Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

        print(
            f"\n🔒 Security audit completed. {len(issues_found)} issues found.")
        return len(issues_found) == 0


if __name__ == "__main__":
    # Run security tests
    test_suite = TestSecurityValidations()
    test_suite.test_epub_path_validation()
    test_suite.test_text_sanitization()
    test_suite.test_file_size_limits()
    test_suite.test_filename_sanitization()

    print()

    # Run security audit
    SecurityAudit.run_security_audit()

    print()
    print("✨ Security testing framework completed!")
