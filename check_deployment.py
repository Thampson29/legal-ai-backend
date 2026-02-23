#!/usr/bin/env python3
"""
Deployment Preparation Script
Checks if all requirements are met for cloud deployment.
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if required files exist."""
    print("=" * 60)
    print("DEPLOYMENT READINESS CHECK")
    print("=" * 60)
    print()
    
    required_files = [
        'requirements.txt',
        'Dockerfile',
        'Procfile',
        'render.yaml',
        'docker-compose.yml',
        '.env.example',
        'app/main.py',
        'app/rag.py',
        'app/vectorstore.py',
    ]
    
    missing_files = []
    present_files = []
    
    for file in required_files:
        if os.path.exists(file):
            present_files.append(file)
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file} - MISSING")
    
    print()
    return len(missing_files) == 0

def check_env_vars():
    """Check environment variables."""
    print("=" * 60)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)
    print()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google Gemini API Key',
        'CHROMA_DB_PATH': 'ChromaDB Path'
    }
    
    all_set = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask API key for security
            if 'KEY' in var or 'SECRET' in var:
                display_value = value[:10] + '*' * (len(value) - 10)
            else:
                display_value = value
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} - NOT SET")
            all_set = False
    
    print()
    return all_set

def check_vector_db():
    """Check if vector database exists."""
    print("=" * 60)
    print("VECTOR DATABASE CHECK")
    print("=" * 60)
    print()
    
    chroma_path = os.getenv('CHROMA_DB_PATH', 'chroma_db_gemini')
    
    if os.path.exists(chroma_path):
        # Check if it has content
        files = list(Path(chroma_path).rglob('*'))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        
        print(f"✅ Vector database found: {chroma_path}")
        print(f"   Files: {len(files)}")
        print(f"   Size: {total_size_mb:.2f} MB")
        print()
        return True
    else:
        print(f"❌ Vector database NOT found at: {chroma_path}")
        print(f"   Run migration script first: python migrate_to_gemini.py")
        print()
        return False

def check_dependencies():
    """Check if dependencies can be imported."""
    print("=" * 60)
    print("DEPENDENCIES CHECK")
    print("=" * 60)
    print()
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'langchain',
        'langchain_google_genai',
        'chromadb',
        'pydantic',
        'dotenv'
    ]
    
    all_imported = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            all_imported = False
    
    print()
    return all_imported

def check_git():
    """Check git status."""
    print("=" * 60)
    print("GIT REPOSITORY CHECK")
    print("=" * 60)
    print()
    
    if os.path.exists('.git'):
        print("✅ Git repository initialized")
        
        # Check for uncommitted changes
        import subprocess
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("⚠️  You have uncommitted changes:")
                print(result.stdout)
                print("\nRun: git add . && git commit -m 'Prepare for deployment'")
            else:
                print("✅ No uncommitted changes")
            
            # Check for remote
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("✅ Git remote configured:")
                print(result.stdout)
            else:
                print("⚠️  No git remote configured")
                print("\nAdd remote: git remote add origin https://github.com/username/repo.git")
        except Exception as e:
            print(f"⚠️  Could not check git status: {e}")
    else:
        print("❌ Not a git repository")
        print("\nInitialize: git init")
        return False
    
    print()
    return True

def generate_deployment_commands():
    """Generate platform-specific deployment commands."""
    print("=" * 60)
    print("DEPLOYMENT COMMANDS")
    print("=" * 60)
    print()
    
    print("📦 RAILWAY DEPLOYMENT:")
    print("-" * 60)
    print("1. Push to GitHub:")
    print("   git add .")
    print("   git commit -m 'Deploy to Railway'")
    print("   git push origin main")
    print()
    print("2. Create Railway project:")
    print("   - Visit: https://railway.app")
    print("   - Click 'New Project' → 'Deploy from GitHub'")
    print("   - Select your repository")
    print()
    print("3. Set environment variables in Railway dashboard:")
    print(f"   GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY', 'your_key_here')}")
    print(f"   CHROMA_DB_PATH={os.getenv('CHROMA_DB_PATH', 'chroma_db_gemini')}")
    print("   CORS_ORIGINS=*")
    print()
    
    print("📦 RENDER DEPLOYMENT:")
    print("-" * 60)
    print("1. Push to GitHub (same as above)")
    print()
    print("2. Create Render service:")
    print("   - Visit: https://render.com")
    print("   - Click 'New' → 'Blueprint' or 'Web Service'")
    print("   - Connect GitHub repository")
    print()
    print("3. Render will auto-detect render.yaml")
    print()
    
    print("📦 DOCKER DEPLOYMENT:")
    print("-" * 60)
    print("1. Build image:")
    print("   docker build -t legal-ai-backend .")
    print()
    print("2. Test locally:")
    print("   docker run -d -p 8000:8000 \\")
    print(f"     -e GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY', 'your_key')} \\")
    print(f"     -e CHROMA_DB_PATH={os.getenv('CHROMA_DB_PATH', 'chroma_db_gemini')} \\")
    print("     legal-ai-backend")
    print()
    print("3. Test:")
    print("   curl http://localhost:8000/health")
    print()

def main():
    """Main check function."""
    print("\n🚀 Legal AI Backend - Deployment Readiness Check\n")
    
    checks = [
        ("Files", check_files()),
        ("Environment Variables", check_env_vars()),
        ("Vector Database", check_vector_db()),
        ("Dependencies", check_dependencies()),
        ("Git Repository", check_git())
    ]
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    print()
    
    if passed == total:
        print("🎉 All checks passed! You're ready to deploy.")
        print()
        generate_deployment_commands()
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above before deploying.")
        print()
        print("📖 See DEPLOYMENT.md for detailed instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
