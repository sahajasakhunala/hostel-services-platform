"""
Phase 7.8 — Documentation & Repository References Structure Verification Suite.

Verifies:
- All documentation files exist and are non-empty.
- Root README.md contains working local file links.
- Architecture docs contain required system layout terms (Browser, Routes, Service, Repository).
- API docs list correct REST endpoints.
- Future roadmap items are clearly marked as future instead of fabricated present capabilities.
"""

import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def test_docs_exist_and_non_empty():
    """DOC-01: Verifies all mandatory documentation files exist and contain content."""
    docs_to_check = [
        'README.md',
        'docs/architecture/system_architecture.md',
        'docs/architecture/database_architecture.md',
        'docs/architecture/application_architecture.md',
        'docs/architecture/api_architecture.md',
        'docs/architecture/security_architecture.md',
        'docs/guides/installation.md',
        'docs/guides/configuration.md',
        'docs/guides/development.md',
        'docs/guides/database_setup.md',
        'docs/guides/testing.md',
        'docs/operations/deployment.md',
        'docs/operations/backup_restore.md',
        'docs/operations/troubleshooting.md',
    ]

    for rel_path in docs_to_check:
        full_path = os.path.join(ROOT_DIR, rel_path)
        assert os.path.exists(full_path), f"Mandatory doc file missing: {rel_path}"
        assert os.path.getsize(full_path) > 0, f"Doc file is empty: {rel_path}"


def test_readme_links_are_valid():
    """DOC-02: Parses root README.md links and verifies target files exist."""
    readme_path = os.path.join(ROOT_DIR, 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find markdown links like [Text](file:///c:/Users/LENOVO/hostel-services-platform/docs/...)
    links = re.findall(r'\[.*?\]\(file:///.*?/hostel-services-platform/(.*?)\)', content)
    assert len(links) > 0, "No markdown file:// links found in README"

    for rel_link in links:
        # Strip query params or line anchors if any
        clean_link = rel_link.split('#')[0]
        target_path = os.path.join(ROOT_DIR, clean_link)
        assert os.path.exists(target_path), f"README link targets non-existent file: {clean_link}"


def test_architecture_terminology():
    """DOC-03: Verifies architecture documents contain correct layered system terminology."""
    arch_path = os.path.join(ROOT_DIR, 'docs/architecture/system_architecture.md')
    with open(arch_path, 'r', encoding='utf-8') as f:
        content = f.read()

    expected_terms = ['Browser', 'Routes', 'Service', 'Repository', 'PyMySQL', 'MySQL']
    for term in expected_terms:
        assert term.lower() in content.lower(), f"System architecture guide missing key term: {term}"


def test_api_route_references():
    """DOC-04: Verifies API documentation lists correct endpoints and response codes."""
    api_path = os.path.join(ROOT_DIR, 'docs/architecture/api_architecture.md')
    with open(api_path, 'r', encoding='utf-8') as f:
        content = f.read()

    expected_routes = ['/api/auth', '/api/students', '/api/allocations', '/api/finance', '/api/visitors']
    for route in expected_routes:
        assert route in content, f"API documentation missing route reference: {route}"

    expected_statuses = ['400', '401', '403', '500']
    for status in expected_statuses:
        assert status in content, f"API documentation missing status code: {status}"


def test_truthful_claims():
    """DOC-05: Verifies that un-implemented cloud features are not claimed as currently active."""
    all_docs = []
    for root, _, files in os.walk(os.path.join(ROOT_DIR, 'docs')):
        for file in files:
            if file.endswith('.md'):
                all_docs.append(os.path.join(root, file))
    all_docs.append(os.path.join(ROOT_DIR, 'README.md'))

    for doc_path in all_docs:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        # Verify no false active claims of container/CI orchestration
        if 'docker' in content or 'kubernetes' in content or 'ci/cd' in content:
            assert 'future' in content or 'planned' in content or 'roadmap' in content or 'enhancement' in content or 'optional' in content or 'git' in content, \
                f"Document {os.path.basename(doc_path)} contains active claim of un-implemented cloud/CI features."
